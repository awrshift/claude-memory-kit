#!/usr/bin/env python3
"""
postprocess_stitch.py — Post-process Stitch-generated HTML to enforce design token adherence.

Strategy (per Gemini engineering review):
  Mutate the Tailwind config inside the <script> tag — one hex change in config
  automatically fixes ALL Tailwind utility classes (bg-, text-, border-, opacity modifiers).

Usage:
  python3 postprocess_stitch.py input.html --tokens design-tokens.json
  python3 postprocess_stitch.py *.html --tokens design-tokens.json --output-dir processed/
  python3 postprocess_stitch.py input.html --tokens design-tokens.json --dry-run --verbose
"""

import argparse
import json
import math
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Version
# ---------------------------------------------------------------------------

VERSION = "1.1.0"

# ---------------------------------------------------------------------------
# Name-based mapping: Stitch key name → our token hex
# ---------------------------------------------------------------------------

NAME_MAP = {
  # Background family
  'background': '#1A1510', 'background-dark': '#1A1510', 'bg-dark': '#1A1510', 'bg': '#1A1510',
  'background-light': '#F5E6C8',

  # Surface family
  'surface': '#231C14', 'panel': '#231C14', 'panel-dark': '#231C14', 'sidebar': '#231C14',
  'sidebar-dark': '#231C14', 'card': '#2E251C', 'card-dark': '#2E251C',

  # Elevated
  'elevated': '#2E251C', 'surface-hover': '#2E251C', 'surface-light': '#2E251C',
  'hover': '#2E251C', 'card-hover': '#2E251C',

  # Border
  'border': '#3E3328', 'border-dark': '#3E3328', 'border-color': '#3E3328',
  'border-subtle': '#3E3328', 'divider': '#3E3328',

  # Text
  'text-cream': '#F5E6C8', 'text-primary': '#F5E6C8', 'text-main': '#F5E6C8',
  'cream': '#F5E6C8', 'text-light': '#F5E6C8',
  'text-secondary': '#C8A878', 'text-muted': '#9A8A72', 'text-disabled': '#9A8A72',
  'muted': '#9A8A72',

  # Accent
  'primary': '#E8B830', 'amber': '#E8B830', 'accent': '#E8B830', 'accent-amber': '#E8B830',
  'alert-amber': '#E8B830', 'warning': '#E8B830',
  'success': '#78C840', 'green': '#78C840', 'accent-green': '#78C840',
  'info': '#5CC8A0', 'teal': '#5CC8A0', 'accent-teal': '#5CC8A0',
  'error': '#EF5350', 'danger': '#EF5350', 'red': '#EF5350', 'accent-red': '#EF5350',
  'alert-red': '#EF5350', 'destructive': '#EF5350',

  # Chart / brand palette
  'terracotta': '#C96B2C', 'brand-4': '#8870A8',
  'violet': '#8870A8', 'purple': '#8870A8',
  'coral': '#E86850',
  'steel': '#4A9EC8', 'steel-blue': '#4A9EC8',
  'rose': '#D888A8',

  # Brand series
  'brand-1': '#E8B830',
  'brand-2': '#5CC8A0',
  'brand-3': '#C96B2C',
  'brand-5': '#E86850',
}

# ---------------------------------------------------------------------------
# Reference palette: all valid tokens for RGB distance matching
# ---------------------------------------------------------------------------

REFERENCE_PALETTE = [
  ('#1A1510', 'background'),
  ('#231C14', 'surface'),
  ('#2E251C', 'elevated'),
  ('#3E3328', 'border'),
  ('#F5E6C8', 'text-primary'),
  ('#C8A878', 'text-secondary'),
  ('#9A8A72', 'text-muted'),
  ('#E8B830', 'primary'),
  ('#78C840', 'success'),
  ('#5CC8A0', 'info'),
  ('#C96B2C', 'terracotta'),
  ('#EF5350', 'error'),
  ('#8870A8', 'violet'),
  ('#E86850', 'coral'),
  ('#4A9EC8', 'steel'),
  ('#D888A8', 'rose'),
  # Utility
  ('#000000', 'black'),
  ('#4A3E30', 'tooltip-bg'),
  ('#7A6B5A', 'disabled-text'),
  ('#FFFFFF', 'white'),
]

RGB_DISTANCE_THRESHOLD = 40

# ---------------------------------------------------------------------------
# Google Fonts replacement
# ---------------------------------------------------------------------------

FONT_LINKS_REPLACEMENT = (
  '<link href="https://fonts.googleapis.com/css2?family=Geist:wght@400;500;600;700'
  '&family=IBM+Plex+Mono:wght@400;500;600;700&display=swap" rel="stylesheet"/>\n'
  '  <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined'
  ':wght,FILL@100..700,0..1&display=swap" rel="stylesheet"/>'
)

# ---------------------------------------------------------------------------
# CSS injection block
# ---------------------------------------------------------------------------

CSS_INJECTION = """<style id="design-system-overrides">
  /* Design System: tabular-nums for all monospace data */
  .font-mono, [class*="font-mono"] { font-variant-numeric: tabular-nums; }
  /* Focus ring */
  *:focus-visible { outline: 2px solid #5CC8A0; outline-offset: 2px; }
  /* Override pure white text in dark mode */
  .dark .text-white { color: #F5E6C8; }
</style>"""

# ---------------------------------------------------------------------------
# Helpers: color parsing and distance
# ---------------------------------------------------------------------------

def parse_hex(hex_str):
  """Parse a 3- or 6-digit hex color string to (r, g, b) tuple. Returns None on failure."""
  s = hex_str.strip().lstrip('#')
  if len(s) == 3:
    s = s[0]*2 + s[1]*2 + s[2]*2
  if len(s) != 6:
    return None
  try:
    r = int(s[0:2], 16)
    g = int(s[2:4], 16)
    b = int(s[4:6], 16)
    return (r, g, b)
  except ValueError:
    return None


def rgb_distance(c1, c2):
  """Euclidean distance in RGB space."""
  return math.sqrt(sum((a - b) ** 2 for a, b in zip(c1, c2)))


def nearest_token(hex_str, threshold=RGB_DISTANCE_THRESHOLD):
  """
  Find nearest token hex from REFERENCE_PALETTE by Euclidean RGB distance.
  Returns (token_hex, token_name, distance) or None if beyond threshold.
  """
  rgb = parse_hex(hex_str)
  if rgb is None:
    return None
  best_dist = float('inf')
  best_hex = None
  best_name = None
  for ref_hex, ref_name in REFERENCE_PALETTE:
    ref_rgb = parse_hex(ref_hex)
    if ref_rgb is None:
      continue
    dist = rgb_distance(rgb, ref_rgb)
    if dist < best_dist:
      best_dist = dist
      best_hex = ref_hex
      best_name = ref_name
  if best_dist <= threshold:
    return (best_hex, best_name, best_dist)
  return None

# ---------------------------------------------------------------------------
# Token loader
# ---------------------------------------------------------------------------

def load_tokens(tokens_path):
  """
  Load design-tokens.json and extract resolved color hex values.
  Returns a dict of semantic_name → resolved_hex (uppercased).
  Only used as a fallback reference; NAME_MAP and REFERENCE_PALETTE are built-in.
  """
  try:
    with open(tokens_path, 'r', encoding='utf-8') as f:
      data = json.load(f)
  except Exception as e:
    print(f"Warning: could not load tokens file: {e}", file=sys.stderr)
    return {}

  # Collect raw token paths → values
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

  # Keep only color hex values
  colors = {}
  for path, val in resolved.items():
    if isinstance(val, str) and val.startswith('#'):
      # Last segment is the semantic name
      parts = path.split('.')
      name = parts[-1]
      colors[name] = val.upper()

  return colors

# ---------------------------------------------------------------------------
# Tailwind config extraction
# ---------------------------------------------------------------------------

def find_tailwind_config_block(html):
  """
  Find the <script> tag containing tailwind.config.
  Returns (script_start, script_end, config_start, config_end) indices
  where config_start..config_end is the JS object (including braces).
  Returns None if not found.
  """
  # Find the script tag with tailwind.config
  script_pattern = re.compile(r'<script[^>]*>', re.IGNORECASE)
  for m in script_pattern.finditer(html):
    tag_start = m.start()
    tag_end = m.end()
    # Find closing </script>
    close = html.find('</script>', tag_end)
    if close == -1:
      continue
    script_content = html[tag_end:close]
    if 'tailwind.config' not in script_content:
      continue

    # Find 'tailwind.config = {' or 'tailwind.config={'
    cfg_match = re.search(r'tailwind\.config\s*=\s*\{', script_content)
    if not cfg_match:
      continue

    # Find matching closing brace using brace counting
    inner_start = tag_end + cfg_match.end() - 1  # position of opening {
    depth = 0
    i = inner_start
    while i < close:
      ch = html[i]
      if ch == '{':
        depth += 1
      elif ch == '}':
        depth -= 1
        if depth == 0:
          return (tag_start, close + len('</script>'), inner_start, i + 1)
      i += 1

  return None


def extract_colors_from_config(config_js):
  """
  Extract color key → hex value pairs from a Tailwind config JS object string.
  Handles both single and double quoted hex values.
  Returns list of (key, hex_value, full_match_str) tuples.
  """
  # Match patterns like: 'key': '#hex' or "key": "#hex"
  # Also: key: '#hex' (unquoted key)
  pattern = re.compile(
    r'''(['"]?)(\w[\w-]*)(['"]?)\s*:\s*(['"])(#[0-9a-fA-F]{3,8})(['"])''',
    re.IGNORECASE
  )
  results = []
  for m in pattern.finditer(config_js):
    key = m.group(2)
    quote = m.group(4)
    hex_val = m.group(5)
    full = m.group(0)
    results.append((key, hex_val, full, m.start(), m.end()))
  return results

# ---------------------------------------------------------------------------
# Font replacement
# ---------------------------------------------------------------------------

def replace_fonts(html, verbose=False):
  """
  Replace Google Fonts <link> tags with Geist + IBM Plex Mono links.
  Keeps Material Symbols if already present in the replacement.
  Returns (new_html, description_str).
  """
  # Find all Google Fonts link tags
  gfont_pattern = re.compile(
    r'<link[^>]+href=["\']https://fonts\.googleapis\.com[^"\']*["\'][^>]*/?>',
    re.IGNORECASE
  )

  matches = list(gfont_pattern.finditer(html))
  if not matches:
    return html, 'No Google Fonts links found'

  # Collect what fonts were there
  old_fonts = []
  for m in matches:
    tag = m.group(0)
    # Extract family names
    family_m = re.search(r'family=([^&"\']+)', tag, re.IGNORECASE)
    if family_m:
      # Decode + to space
      fam = family_m.group(1).replace('+', ' ').split(':')[0]
      old_fonts.append(fam)

  # Remove all Google Fonts links
  new_html = gfont_pattern.sub('', html)

  # Find where to inject new links — after the last removed tag's position
  # Inject before </head> or at the top of what's left
  head_close = new_html.find('</head>')
  if head_close == -1:
    head_close = new_html.find('<body')

  if head_close == -1:
    # Inject at start
    new_html = FONT_LINKS_REPLACEMENT + '\n' + new_html
  else:
    new_html = new_html[:head_close] + '  ' + FONT_LINKS_REPLACEMENT + '\n' + new_html[head_close:]

  old_desc = ', '.join(old_fonts) if old_fonts else 'unknown'
  return new_html, f'{old_desc} → Geist, IBM Plex Mono'


def update_font_family_in_config(config_js, verbose=False):
  """
  Update fontFamily in Tailwind config: display/sans → Geist, mono → IBM Plex Mono.
  Handles both quoted and unquoted keys in JS objects.
  Returns updated config_js string.
  """
  # Pattern: "display": [...] or display: [...] (quoted or unquoted keys)
  def replace_font_array(match):
    prefix = match.group(1)  # quote + key + quote + colon
    key = match.group(2)
    if key in ('display', 'sans'):
      return f'{prefix} ["Geist", "sans-serif"]'
    elif key == 'mono':
      return f'{prefix} ["IBM Plex Mono", "monospace"]'
    return match.group(0)

  result = re.sub(
    r'''(["']?(display|sans|mono)["']?\s*:\s*)\[[^\]]*\]''',
    replace_font_array,
    config_js
  )

  # Also handle string format: "display": 'Font Name' (not array)
  def replace_font_str(match):
    prefix = match.group(1)
    key = match.group(2)
    if key in ('display', 'sans'):
      return f'{prefix}"Geist"'
    elif key == 'mono':
      return f'{prefix}"IBM Plex Mono"'
    return match.group(0)

  result = re.sub(
    r'''(["']?(display|sans|mono)["']?\s*:\s*)['"][^'"]+['"]''',
    replace_font_str,
    result
  )

  return result

# ---------------------------------------------------------------------------
# Arbitrary [#hex] sweeper for HTML body
# ---------------------------------------------------------------------------

def sweep_arbitrary_values(html, verbose=False):
  """
  Find and replace [#XXXXXX] arbitrary Tailwind values in HTML body.
  Returns (new_html, count_replaced).
  """
  arbitrary_pattern = re.compile(r'\[#([0-9a-fA-F]{3,8})\]')
  replacements = []

  for m in arbitrary_pattern.finditer(html):
    hex_val = '#' + m.group(1)
    nearest = nearest_token(hex_val)
    if nearest:
      token_hex, token_name, dist = nearest
      replacements.append((m.start(), m.end(), m.group(0), token_hex, token_name, dist))

  # Apply replacements in reverse order to preserve indices
  result = html
  count = 0
  for start, end, original, token_hex, token_name, dist in reversed(replacements):
    # Replace [#XXXXXX] with [#TOKEN_HEX]
    new_val = f'[{token_hex}]'
    result = result[:start] + new_val + result[end:]
    count += 1
    if verbose:
      print(f'  arbitrary: {original} → {new_val} ({token_name}, dist: {dist:.1f})')

  return result, count

# ---------------------------------------------------------------------------
# CSS injection
# ---------------------------------------------------------------------------

def inject_css(html, verbose=False):
  """Inject CSS overrides block before </head>. Returns new_html."""
  head_close = html.find('</head>')
  if head_close == -1:
    # Try before </body>
    body_close = html.find('</body>')
    if body_close == -1:
      html = html + '\n' + CSS_INJECTION
    else:
      html = html[:body_close] + CSS_INJECTION + '\n' + html[body_close:]
  else:
    html = html[:head_close] + CSS_INJECTION + '\n' + html[head_close:]
  if verbose:
    print('  CSS injected: tabular-nums, focus-ring, text-white override')
  return html

# ---------------------------------------------------------------------------
# Main processing logic
# ---------------------------------------------------------------------------

def process_file(input_path, tokens_path, output_path, dry_run=False, verbose=False, overrides=None):
  """
  Process a single HTML file. Returns a stats dict.
  overrides: dict of {stitch_key: hex_value} to override NAME_MAP per-screen.
  """
  with open(input_path, 'r', encoding='utf-8') as f:
    html = f.read()

  # --- Idempotency check ---
  if '<!-- POSTPROCESSED by design-tokens' in html:
    print(f'  SKIPPED — already postprocessed')
    return {'skipped': True}

  # --- Load tokens (for reference, mostly used via NAME_MAP / REFERENCE_PALETTE) ---
  _tokens = load_tokens(tokens_path) if tokens_path else {}

  stats = {
    'skipped': False,
    'colors_mapped': 0,
    'colors_total': 0,
    'colors_name': 0,
    'colors_distance': 0,
    'colors_skipped': 0,
    'fonts_desc': '',
    'arbitrary_replaced': 0,
    'css_injected': False,
  }

  mapping_log = []  # list of (key, old_hex, new_hex, method, extra)

  # =========================================================================
  # Step 1: Find and patch Tailwind config
  # =========================================================================
  config_bounds = find_tailwind_config_block(html)

  # Merge per-screen overrides into a local copy of NAME_MAP
  local_name_map = dict(NAME_MAP)
  if overrides:
    for k, v in overrides.items():
      local_name_map[k.lower()] = v
      if verbose:
        print(f'  override: {k} → {v}')

  if config_bounds:
    script_start, script_end, cfg_start, cfg_end = config_bounds
    config_js = html[cfg_start:cfg_end]

    color_entries = extract_colors_from_config(config_js)
    stats['colors_total'] = len(color_entries)

    # Build replacement map: offset → (old_str, new_str)
    # We'll do replacements from the config_js copy
    new_config_js = config_js

    # Process in reverse by position to preserve offsets
    sorted_entries = sorted(color_entries, key=lambda x: x[3], reverse=True)

    for key, hex_val, full_match, start, end in sorted_entries:
      key_lower = key.lower()
      old_upper = hex_val.upper()

      # Strategy 1: name-based match (with per-screen overrides)
      if key_lower in local_name_map:
        new_hex = local_name_map[key_lower]
        if new_hex.upper() != old_upper:
          # Replace hex value in the full_match string
          new_full = full_match.replace(hex_val, new_hex)
          new_config_js = new_config_js[:start] + new_full + new_config_js[end:]
          stats['colors_name'] += 1
          stats['colors_mapped'] += 1
          mapping_log.append((key, old_upper, new_hex.upper(), 'name match', ''))
        else:
          # Already correct
          stats['colors_name'] += 1
          stats['colors_mapped'] += 1
          mapping_log.append((key, old_upper, new_hex.upper(), 'name match (already correct)', ''))
        continue

      # Strategy 2: RGB distance fallback
      result = nearest_token(hex_val)
      if result:
        new_hex, token_name, dist = result
        if new_hex.upper() != old_upper:
          new_full = full_match.replace(hex_val, new_hex)
          new_config_js = new_config_js[:start] + new_full + new_config_js[end:]
          stats['colors_distance'] += 1
          stats['colors_mapped'] += 1
          mapping_log.append((key, old_upper, new_hex.upper(), f'distance: {dist:.0f}', ''))
        else:
          stats['colors_distance'] += 1
          stats['colors_mapped'] += 1
          mapping_log.append((key, old_upper, new_hex.upper(), f'distance: {dist:.0f} (already correct)', ''))
      else:
        # Skip
        dist_info = ''
        rgb = parse_hex(hex_val)
        if rgb:
          # Find nearest for reporting even if beyond threshold
          best = nearest_token(hex_val, threshold=9999)
          if best:
            dist_info = f'distance: {best[2]:.0f}, threshold: {RGB_DISTANCE_THRESHOLD}'
        stats['colors_skipped'] += 1
        mapping_log.append((key, old_upper, 'SKIPPED', 'no match', dist_info))

    # Update font families in config
    new_config_js = update_font_family_in_config(new_config_js, verbose=verbose)

    # Splice back into HTML
    html = html[:cfg_start] + new_config_js + html[cfg_end:]

  else:
    if verbose:
      print('  Warning: no tailwind.config block found in HTML')

  # =========================================================================
  # Step 1b: Replace font-family in <style> blocks
  # =========================================================================
  # Stitch sometimes adds: body { font-family: 'Space Grotesk', sans-serif; }
  html = re.sub(
    r'''(font-family\s*:\s*)['"]?(?:Space Grotesk|Inter|DM Sans)['"]?\s*,\s*sans-serif''',
    r"\1'Geist', sans-serif",
    html,
    flags=re.IGNORECASE,
  )
  # mono font-family in <style>
  html = re.sub(
    r'''(font-family\s*:\s*)(?:ui-monospace[^;]*|['"]?(?:Fira Code|Source Code Pro|JetBrains Mono)['"]?\s*,\s*monospace)''',
    r"\1'IBM Plex Mono', monospace",
    html,
    flags=re.IGNORECASE,
  )

  # =========================================================================
  # Step 2: Replace Google Fonts links
  # =========================================================================
  html, fonts_desc = replace_fonts(html, verbose=verbose)
  stats['fonts_desc'] = fonts_desc

  # =========================================================================
  # Step 3: Inject CSS features
  # =========================================================================
  html = inject_css(html, verbose=verbose)
  stats['css_injected'] = True

  # =========================================================================
  # Step 4: Arbitrary [#hex] sweeper on HTML body
  # =========================================================================
  html, arb_count = sweep_arbitrary_values(html, verbose=verbose)
  stats['arbitrary_replaced'] = arb_count

  # =========================================================================
  # Step 5: Add postprocessed comment
  # =========================================================================
  comment = f'<!-- POSTPROCESSED by design-tokens v{VERSION} -->\n'
  html = comment + html

  # =========================================================================
  # Output
  # =========================================================================
  stats['mapping_log'] = mapping_log

  if not dry_run:
    with open(output_path, 'w', encoding='utf-8') as f:
      f.write(html)

  return stats

# ---------------------------------------------------------------------------
# Report formatting
# ---------------------------------------------------------------------------

def print_report(filename, stats, output_path, dry_run=False):
  """Print per-file processing report."""
  print(f'\n=== {filename} ===')

  if stats.get('skipped'):
    print('  SKIPPED — already postprocessed')
    return

  total = stats['colors_total']
  mapped = stats['colors_mapped']
  name_count = stats['colors_name']
  dist_count = stats['colors_distance']
  skip_count = stats['colors_skipped']

  print(f'Colors mapped: {mapped}/{total} (name: {name_count}, distance: {dist_count}, skipped: {skip_count})')

  for key, old_hex, new_hex, method, extra in stats.get('mapping_log', []):
    if new_hex == 'SKIPPED':
      note = f'({extra})' if extra else ''
      print(f'  {key}: {old_hex} → SKIPPED {note}')
    else:
      arrow = f'{old_hex} → {new_hex}'
      print(f'  {key}: {arrow} ({method})')

  print(f'Fonts: {stats["fonts_desc"]}')

  if stats['css_injected']:
    print('CSS injected: tabular-nums, focus-ring')

  if stats['arbitrary_replaced']:
    print(f'Arbitrary values: {stats["arbitrary_replaced"]} replaced')

  if dry_run:
    print(f'Output: DRY RUN — no file written')
  else:
    print(f'Output: {output_path}')

# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser():
  parser = argparse.ArgumentParser(
    description='Post-process Stitch HTML files to enforce design token adherence.',
    formatter_class=argparse.RawDescriptionHelpFormatter,
    epilog='''Examples:
  python3 postprocess_stitch.py dashboard.html --tokens design-tokens.json
  python3 postprocess_stitch.py *.html --tokens design-tokens.json --output-dir processed/
  python3 postprocess_stitch.py input.html --tokens design-tokens.json --dry-run --verbose
'''
  )
  parser.add_argument(
    'inputs',
    nargs='+',
    metavar='input.html',
    help='One or more input HTML files'
  )
  parser.add_argument(
    '--tokens',
    required=True,
    metavar='design-tokens.json',
    help='Path to design-tokens.json'
  )
  parser.add_argument(
    '--output',
    metavar='output.html',
    help='Output path for single file (default: input_processed.html)'
  )
  parser.add_argument(
    '--output-dir',
    metavar='DIR',
    help='Output directory for multiple files'
  )
  parser.add_argument(
    '--dry-run',
    action='store_true',
    help='Show what would change without writing files'
  )
  parser.add_argument(
    '--verbose',
    action='store_true',
    help='Show detailed mapping info'
  )
  parser.add_argument(
    '--overrides',
    metavar='JSON',
    help='JSON dict of per-screen NAME_MAP overrides, e.g. \'{"primary": "#5CC8A0"}\''
  )
  return parser


def resolve_output_path(input_path, args):
  """Determine output file path based on CLI args."""
  p = Path(input_path)

  if args.output and len(args.inputs) == 1:
    return Path(args.output)

  if args.output_dir:
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir / p.name

  # Default: same dir, _processed suffix
  return p.parent / (p.stem + '_processed' + p.suffix)


def main():
  parser = build_parser()
  args = parser.parse_args()

  # Validate tokens file
  tokens_path = Path(args.tokens)
  if not tokens_path.exists():
    print(f'Error: tokens file not found: {tokens_path}', file=sys.stderr)
    sys.exit(1)

  # Validate inputs
  input_paths = []
  for pattern in args.inputs:
    p = Path(pattern)
    if p.exists():
      input_paths.append(p)
    else:
      # Glob expansion (when shell doesn't expand)
      matched = list(Path('.').glob(pattern))
      if matched:
        input_paths.extend(matched)
      else:
        print(f'Warning: no files matched: {pattern}', file=sys.stderr)

  if not input_paths:
    print('Error: no input files found', file=sys.stderr)
    sys.exit(1)

  if args.output and len(input_paths) > 1:
    print('Error: --output can only be used with a single input file', file=sys.stderr)
    sys.exit(1)

  # Parse overrides
  overrides = None
  if args.overrides:
    try:
      overrides = json.loads(args.overrides)
    except json.JSONDecodeError as e:
      print(f'Error: invalid --overrides JSON: {e}', file=sys.stderr)
      sys.exit(1)

  total_files = 0
  skipped_files = 0
  errored_files = 0

  for input_path in input_paths:
    output_path = resolve_output_path(str(input_path), args)
    total_files += 1

    try:
      stats = process_file(
        input_path=str(input_path),
        tokens_path=str(tokens_path),
        output_path=str(output_path),
        dry_run=args.dry_run,
        verbose=args.verbose,
        overrides=overrides,
      )
      print_report(input_path.name, stats, output_path, dry_run=args.dry_run)
      if stats.get('skipped'):
        skipped_files += 1
    except Exception as e:
      print(f'\n=== {input_path.name} ===')
      print(f'  ERROR: {e}')
      if args.verbose:
        import traceback
        traceback.print_exc()
      errored_files += 1

  # Summary for multi-file runs
  if total_files > 1:
    processed = total_files - skipped_files - errored_files
    print(f'\nSummary: {processed} processed, {skipped_files} skipped, {errored_files} errors (total: {total_files})')


if __name__ == '__main__':
  main()
