#!/usr/bin/env python3
"""
audit_html.py — Design token adherence audit for HTML files.

Extracts all color values from an HTML file and compares them against
a design-tokens.json file. Reports matches, violations, font compliance,
and tabular-nums usage.

Usage:
  python3 audit_html.py --html page.html --tokens design-tokens.json
  python3 audit_html.py --html page.html --tokens design-tokens.json --verbose

Exit codes:
  0 = 100% adherence
  1 = violations found
  2 = input error
"""

import argparse
import json
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Patterns
# ---------------------------------------------------------------------------

HEX_RE = re.compile(r'#([0-9a-fA-F]{3,8})\b')
RGBA_RE = re.compile(r'rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)(?:\s*,\s*[\d.]+)?\s*\)')
FONT_FAMILY_RE = re.compile(r'font-family\s*:\s*([^;}{]+)', re.IGNORECASE)

# Colors to skip — common functional values that aren't design tokens
SKIP_COLORS = {
  '#fff', '#ffffff', '#000', '#000000',
  '#00000099', '#ffffff0d', '#ffffff0a',
}


# ---------------------------------------------------------------------------
# Token loading
# ---------------------------------------------------------------------------

def load_tokens(tokens_path):
  """Load design-tokens.json and build a set of all resolved hex values."""
  with open(tokens_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

  # Flatten all values
  raw = {}
  def walk(node, path_parts):
    if not isinstance(node, dict):
      return
    for key, val in node.items():
      if key.startswith('$'):
        continue
      current = path_parts + [key]
      if isinstance(val, dict) and 'value' in val:
        raw['.'.join(current)] = val['value']
      elif isinstance(val, dict):
        walk(val, current)
  walk(data, [])

  # Resolve aliases
  alias_pat = re.compile(r'^\{(.+)\}$')
  resolved = dict(raw)
  for _ in range(len(resolved) + 1):
    changed = False
    for k, v in list(resolved.items()):
      if isinstance(v, str):
        m = alias_pat.match(v)
        if m and m.group(1) in resolved:
          ref = resolved[m.group(1)]
          if not alias_pat.match(str(ref)):
            resolved[k] = ref
            changed = True
    if not changed:
      break

  # Build value set and reverse index
  color_set = set()
  color_index = {}  # normalized hex -> [token paths]

  for path, val in resolved.items():
    if isinstance(val, str) and val.startswith('#'):
      norm = normalize_hex(val)
      if norm:
        color_set.add(norm)
        color_index.setdefault(norm, []).append(path)

  # Extract font names
  fonts = set()
  for path, val in resolved.items():
    if 'font' in path.lower() and isinstance(val, str) and not val.startswith('#') and not val.startswith('{'):
      # Skip dimension values
      if not re.match(r'^[\d.]+(px|rem|em|%)$', val):
        fonts.add(val.strip())

  return data, color_set, color_index, fonts


def normalize_hex(value):
  """Normalize a hex color to lowercase 6-digit form."""
  v = value.strip().lower()
  if not v.startswith('#'):
    return None

  h = v[1:]
  if len(h) == 3:
    h = h[0]*2 + h[1]*2 + h[2]*2
  elif len(h) == 6:
    pass
  elif len(h) == 8:
    pass  # keep alpha hex as-is
  else:
    return None

  return '#' + h


def rgba_to_hex(r, g, b):
  """Convert RGB ints to hex string."""
  return f'#{r:02x}{g:02x}{b:02x}'


# ---------------------------------------------------------------------------
# HTML scanning
# ---------------------------------------------------------------------------

def extract_colors_from_html(html_content):
  """
  Extract all color values from HTML.
  Returns list of (line_number, raw_value, normalized_hex, context).
  """
  found = []
  lines = html_content.split('\n')

  for lineno, line in enumerate(lines, start=1):
    # Hex colors
    for m in HEX_RE.finditer(line):
      raw = '#' + m.group(1)
      norm = normalize_hex(raw)
      if norm:
        # Get surrounding context
        start = max(0, m.start() - 20)
        end = min(len(line), m.end() + 20)
        ctx = line[start:end].strip()
        found.append((lineno, raw, norm, ctx))

    # rgba() colors — convert to hex for comparison
    for m in RGBA_RE.finditer(line):
      r, g, b = int(m.group(1)), int(m.group(2)), int(m.group(3))
      hex_val = rgba_to_hex(r, g, b)
      norm = normalize_hex(hex_val)
      if norm:
        start = max(0, m.start() - 10)
        end = min(len(line), m.end() + 10)
        ctx = line[start:end].strip()
        found.append((lineno, m.group(0), norm, ctx))

  return found


def extract_fonts_from_html(html_content):
  """Extract all font-family declarations from HTML."""
  fonts = set()
  for m in FONT_FAMILY_RE.finditer(html_content):
    families = m.group(1)
    # Parse individual font names
    for f in families.split(','):
      name = f.strip().strip('"').strip("'")
      # Skip generic families
      if name.lower() in ('sans-serif', 'serif', 'monospace', 'cursive', 'system-ui', 'inherit'):
        continue
      # Skip CSS variable references — these resolve to token fonts at runtime
      if name.startswith('var('):
        continue
      if name:
        fonts.add(name)
  return fonts


def check_tabular_nums(html_content):
  """Check for tabular-nums on data containers."""
  has_tabular = 'tabular-nums' in html_content or 'font-variant-numeric' in html_content
  # Look for font-mono classes as potential data containers
  mono_count = len(re.findall(r'font-mono|IBM Plex Mono|font-data', html_content))
  return has_tabular, mono_count


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------

def audit(html_path, tokens_path, verbose=False):
  """Run full audit and return (matches, violations, stats)."""

  with open(html_path, 'r', encoding='utf-8') as f:
    html_content = f.read()

  data, color_set, color_index, token_fonts = load_tokens(tokens_path)

  # --- Color audit ---
  all_colors = extract_colors_from_html(html_content)
  matches = []
  violations = []
  skipped = []

  for lineno, raw, norm, ctx in all_colors:
    if norm in SKIP_COLORS:
      skipped.append((lineno, raw, norm, 'common functional'))
      continue

    # For 8-digit hex (with alpha), check just the color part
    color_part = norm[:7] if len(norm) > 7 else norm

    if color_part in color_set or norm in color_set:
      token_paths = color_index.get(color_part, color_index.get(norm, ['(direct value)']))
      matches.append((lineno, raw, norm, token_paths))
    else:
      violations.append((lineno, raw, norm, ctx))

  # --- Font audit ---
  html_fonts = extract_fonts_from_html(html_content)
  font_matches = html_fonts & token_fonts
  font_violations = html_fonts - token_fonts
  # Material Symbols is an icon font, not a design violation
  font_violations -= {'Material Symbols Outlined', 'Material Icons', 'Material Symbols'}

  # --- Tabular-nums ---
  has_tabular, mono_count = check_tabular_nums(html_content)

  # --- Stats ---
  total_auditable = len(matches) + len(violations)
  adherence = (len(matches) / total_auditable * 100) if total_auditable > 0 else 100.0

  stats = {
    'total_colors': len(all_colors),
    'matches': len(matches),
    'violations': len(violations),
    'skipped': len(skipped),
    'adherence_pct': adherence,
    'font_matches': font_matches,
    'font_violations': font_violations,
    'has_tabular_nums': has_tabular,
    'mono_elements': mono_count,
  }

  return matches, violations, skipped, stats, verbose


def print_report(html_path, matches, violations, skipped, stats, verbose):
  """Print formatted audit report."""
  name = Path(html_path).name

  print(f'\n=== Token Adherence Audit: {name} ===')
  print(f'Colors: {stats["total_colors"]} total, {stats["matches"]} match, '
        f'{stats["violations"]} violations, {stats["skipped"]} skipped')
  print(f'Adherence: {stats["adherence_pct"]:.0f}%')

  if violations:
    print(f'\nVIOLATIONS ({len(violations)}):')
    seen = set()
    for lineno, raw, norm, ctx in violations:
      key = norm
      if key not in seen or verbose:
        seen.add(key)
        print(f'  line {lineno}: {raw} — not in token system')
        if verbose:
          print(f'    context: ...{ctx}...')

  if verbose and matches:
    print(f'\nMATCHES ({len(matches)}):')
    seen = set()
    for lineno, raw, norm, paths in matches:
      if norm not in seen:
        seen.add(norm)
        path_str = ', '.join(paths[:2])
        print(f'  {norm} → {path_str}')

  # Fonts
  print(f'\nFonts found: {", ".join(sorted(stats["font_matches"] | stats["font_violations"])) or "none"}')
  if stats['font_violations']:
    print(f'  Font violations: {", ".join(sorted(stats["font_violations"]))}')
  else:
    print(f'  All fonts match token system')

  # Tabular-nums
  if stats['has_tabular_nums']:
    print(f'Tabular-nums: present ({stats["mono_elements"]} mono elements)')
  else:
    print(f'Tabular-nums: MISSING — rule D-4 requires tabular-nums on data elements')

  # Final status
  passed = stats['violations'] == 0 and not stats['font_violations']
  status = 'PASS' if passed else 'FAIL'
  print(f'\nResult: {status}')

  return passed


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
  parser = argparse.ArgumentParser(
    description='Audit HTML file for design token adherence.'
  )
  parser.add_argument(
    '--html', required=True, metavar='FILE',
    help='Path to HTML file to audit'
  )
  parser.add_argument(
    '--tokens', required=True, metavar='FILE',
    help='Path to design-tokens.json'
  )
  parser.add_argument(
    '--verbose', action='store_true',
    help='Show detailed match info'
  )
  args = parser.parse_args()

  if not Path(args.html).is_file():
    print(f'Error: HTML file not found: {args.html}', file=sys.stderr)
    sys.exit(2)
  if not Path(args.tokens).is_file():
    print(f'Error: tokens file not found: {args.tokens}', file=sys.stderr)
    sys.exit(2)

  matches, violations, skipped, stats, _ = audit(args.html, args.tokens, args.verbose)
  passed = print_report(args.html, matches, violations, skipped, stats, args.verbose)

  sys.exit(0 if passed else 1)


if __name__ == '__main__':
  main()
