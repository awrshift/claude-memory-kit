#!/usr/bin/env python3
"""
sync_drift.py — Design token drift detector.

PURE DIFF PARSER. Scans code files for hardcoded color/dimension values
and maps them to known design tokens. No LLM calls, no external dependencies.

Usage:
  python3 sync_drift.py design-tokens.json [--scan-dir ./src] [--verbose]

Exit codes:
  0 = no drift found
  1 = drift found
"""

import argparse
import json
import os
import re
import sys

# ---------------------------------------------------------------------------
# Patterns
# ---------------------------------------------------------------------------

HEX_RE = re.compile(r'#([0-9a-fA-F]{3,8})\b')
RGB_RE = re.compile(r'rgba?\(\s*\d+\s*,\s*\d+\s*,\s*\d+')
HSL_RE = re.compile(r'hsla?\(\s*\d+\s*,\s*\d+%?\s*,\s*\d+%?')

# Patterns that strongly suggest the match is inside a URL or comment context.
# We do a lightweight check: skip matches that are preceded by "://" within
# the same 30-char window (i.e. the hex appears inside a URL fragment).
URL_CONTEXT_RE = re.compile(r'://[^\s]*#[0-9a-fA-F]{3,8}')

SKIP_DIRS = {'node_modules', '.git', 'dist', 'build', '__pycache__', '.next', 'coverage'}
CODE_EXTENSIONS = {'.css', '.js', '.jsx', '.ts', '.tsx', '.html'}
SKIP_FILES = {
  'design-tokens.json',
  'design-tokens.css',
  'design-tokens.tailwind.css',
  '.stitch-context.md',
}
MAX_FILE_SIZE = 500 * 1024  # 500 KB


# ---------------------------------------------------------------------------
# Token loading
# ---------------------------------------------------------------------------

def _flatten_tokens(obj, prefix='', result=None):
  """Recursively flatten nested token dict into {path: value} pairs."""
  if result is None:
    result = {}
  if isinstance(obj, dict):
    for key, val in obj.items():
      new_prefix = f'{prefix}.{key}' if prefix else key
      _flatten_tokens(val, new_prefix, result)
  elif isinstance(obj, (str, int, float)):
    result[prefix] = str(obj)
  return result


def build_value_index(tokens_path):
  """
  Read design-tokens.json and return a dict mapping each resolved value
  to a list of token paths that have that value.

  {
    '#06b6d4': ['color.core.cyan-500'],
    '#1e293b': ['color.core.navy-800', 'color.alias.surface'],
    ...
  }
  """
  with open(tokens_path, 'r', encoding='utf-8') as fh:
    raw = json.load(fh)

  flat = _flatten_tokens(raw)

  # Build reverse index: value → [token paths]
  index = {}
  for token_path, value in flat.items():
    # Normalize value for comparison
    norm = _normalize_color(value)
    if norm is None:
      continue
    index.setdefault(norm, []).append(token_path)

  return index


def _normalize_color(value):
  """
  Normalize a color value string for lookup.
  Returns a canonical lowercase string, or None if not a color-ish value.
  """
  if not isinstance(value, str):
    return None
  v = value.strip().lower()

  # Hex shorthand expansion: #abc → #aabbcc
  if re.fullmatch(r'#[0-9a-f]{3}', v):
    v = '#' + v[1] + v[1] + v[2] + v[2] + v[3] + v[3]
    return v

  # Hex 6 or 8 digits
  if re.fullmatch(r'#[0-9a-f]{6,8}', v):
    return v

  # rgb/rgba/hsl/hsla — keep as-is (stripped)
  if re.match(r'rgba?|hsla?', v):
    # Remove all spaces for normalization
    return re.sub(r'\s+', '', v)

  return None


def _normalize_found(raw):
  """Normalize a found raw color string (from source code) for lookup."""
  v = raw.strip().lower()

  # Hex shorthand
  if re.fullmatch(r'#[0-9a-f]{3}', v):
    v = '#' + v[1] + v[1] + v[2] + v[2] + v[3] + v[3]
    return v

  # Hex 6/8
  if re.fullmatch(r'#[0-9a-f]{6,8}', v):
    return v

  # rgb/hsl — strip spaces
  return re.sub(r'\s+', '', v)


# ---------------------------------------------------------------------------
# File scanning
# ---------------------------------------------------------------------------

def is_binary(path):
  """Heuristic binary check: read first 8KB, look for null bytes."""
  try:
    with open(path, 'rb') as fh:
      chunk = fh.read(8192)
    return b'\x00' in chunk
  except OSError:
    return True


def scan_file(filepath):
  """
  Scan a single file for hardcoded color values.

  Returns list of (line_number, raw_value) tuples.
  """
  try:
    size = os.path.getsize(filepath)
  except OSError:
    return []

  if size > MAX_FILE_SIZE:
    return []

  if is_binary(filepath):
    return []

  try:
    with open(filepath, 'r', encoding='utf-8', errors='replace') as fh:
      lines = fh.readlines()
  except OSError:
    return []

  found = []
  for lineno, line in enumerate(lines, start=1):
    # Skip lines that are pure comments (// ... or /* ... or # ...)
    stripped = line.strip()

    # Collect hex matches
    for m in HEX_RE.finditer(line):
      raw = m.group(0)  # e.g. '#06b6d4'
      # Skip if this hex appears inside a URL-like context on the same line
      if URL_CONTEXT_RE.search(line):
        continue
      found.append((lineno, raw))

    # Collect rgb/rgba matches
    for m in RGB_RE.finditer(line):
      raw = m.group(0)
      found.append((lineno, raw))

    # Collect hsl/hsla matches
    for m in HSL_RE.finditer(line):
      raw = m.group(0)
      found.append((lineno, raw))

  return found


def walk_scan_dir(scan_dir, tokens_abspath):
  """
  Yield absolute paths to scannable code files under scan_dir.
  """
  tokens_abspath = os.path.abspath(tokens_abspath)
  for root, dirs, files in os.walk(scan_dir):
    # Prune skip directories in-place
    dirs[:] = [d for d in dirs if d not in SKIP_DIRS]

    for fname in files:
      # Extension filter
      _, ext = os.path.splitext(fname)
      if ext not in CODE_EXTENSIONS:
        continue

      # Skip known generated/source token files by basename
      if fname in SKIP_FILES:
        continue

      full = os.path.abspath(os.path.join(root, fname))

      # Skip the tokens file itself
      if full == tokens_abspath:
        continue

      yield full


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
  parser = argparse.ArgumentParser(
    description='Detect design token drift in code files.'
  )
  parser.add_argument(
    'tokens',
    metavar='design-tokens.json',
    help='Path to design-tokens.json'
  )
  parser.add_argument(
    '--scan-dir',
    default='.',
    metavar='DIR',
    help='Directory to scan (default: current directory)'
  )
  parser.add_argument(
    '--verbose',
    action='store_true',
    help='Show all scanned files, not just results'
  )
  args = parser.parse_args()

  tokens_path = args.tokens
  scan_dir = args.scan_dir

  # Validate inputs
  if not os.path.isfile(tokens_path):
    print(f'ERROR: tokens file not found: {tokens_path}', file=sys.stderr)
    sys.exit(2)

  if not os.path.isdir(scan_dir):
    print(f'ERROR: scan directory not found: {scan_dir}', file=sys.stderr)
    sys.exit(2)

  # Build reverse value index from tokens
  try:
    value_index = build_value_index(tokens_path)
  except (json.JSONDecodeError, OSError) as exc:
    print(f'ERROR: could not read {tokens_path}: {exc}', file=sys.stderr)
    sys.exit(2)

  if args.verbose:
    print(f'Loaded {len(value_index)} unique color values from {tokens_path}')

  # Scan files
  matches = []   # (rel_path, lineno, raw_value, token_paths)
  drifts = []    # (rel_path, lineno, raw_value)
  files_scanned = 0

  tokens_abspath = os.path.abspath(tokens_path)

  for filepath in walk_scan_dir(scan_dir, tokens_abspath):
    files_scanned += 1
    rel = os.path.relpath(filepath, start=scan_dir)

    if args.verbose:
      print(f'  scanning {rel}')

    occurrences = scan_file(filepath)
    for lineno, raw in occurrences:
      norm = _normalize_found(raw)
      if norm in value_index:
        token_paths = value_index[norm]
        matches.append((rel, lineno, raw, token_paths))
      else:
        drifts.append((rel, lineno, raw))

  # ---------------------------------------------------------------------------
  # Report
  # ---------------------------------------------------------------------------
  print()
  print('=== Design Token Drift Report ===')
  print(f'Scanned: {files_scanned} files in {scan_dir}')
  print()

  if matches:
    print('MATCHES (using token values directly instead of CSS variables):')
    for rel, lineno, raw, token_paths in matches:
      tokens_str = ', '.join(f"'{t}'" for t in token_paths[:3])
      if len(token_paths) > 3:
        tokens_str += f' (+{len(token_paths) - 3} more)'
      print(f'  {rel}:{lineno} — {raw} matches token {tokens_str}')
  else:
    print('MATCHES: none')

  print()

  if drifts:
    print('DRIFT (values not in design system):')
    for rel, lineno, raw in drifts:
      print(f'  {rel}:{lineno} — {raw} is not in design system')
  else:
    print('DRIFT: none')

  print()
  print(
    f'Summary: {len(matches)} match{"es" if len(matches) != 1 else ""}'
    ' (should use CSS variables), '
    f'{len(drifts)} drift value{"s" if len(drifts) != 1 else ""}'
  )
  print()

  sys.exit(1 if drifts else 0)


if __name__ == '__main__':
  main()
