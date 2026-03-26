#!/usr/bin/env python3
"""Build and validate a design system from design-tokens.json.

Combines validation (structure, aliases, contrast, types, scaffold integrity)
with CSS custom properties generation. Single entry point for /design check.

Usage:
  python3 build_system.py design-tokens.json
  python3 build_system.py design-tokens.json --css output.css
  python3 build_system.py design-tokens.json --css output.css --verbose

Exit codes:
  0 — PASS (or PASS with warnings)
  1 — FAIL (errors found)
  2 — Usage error (bad args, file not found)
"""

import json
import os
import re
import sys
from argparse import ArgumentParser


# ---------------------------------------------------------------------------
# Token tree helpers (shared with validate_tokens.py)
# ---------------------------------------------------------------------------

def flatten_tokens(data, prefix="", result=None):
  """Walk JSON tree, return flat dict of {dot.path: token_object}."""
  if result is None:
    result = {}
  for key, node in data.items():
    if key.startswith("$"):
      continue
    path = f"{prefix}.{key}" if prefix else key
    if isinstance(node, dict):
      if "value" in node:
        result[path] = node
      else:
        flatten_tokens(node, path, result)
  return result


def extract_alias_paths(value):
  """Return dot-paths referenced inside {curly.braces}."""
  return re.findall(r"\{([^}]+)\}", str(value))


def resolve_alias(value, flat_tokens, visited=None):
  """Resolve {path} aliases. Raises on circular or missing refs."""
  if visited is None:
    visited = set()
  refs = extract_alias_paths(str(value))
  if not refs:
    return value
  resolved = str(value)
  for ref in refs:
    if ref in visited:
      raise ValueError(f"Circular: {' -> '.join(sorted(visited))} -> {ref}")
    if ref not in flat_tokens:
      raise KeyError(f"Missing: {{{ref}}}")
    inner = resolve_alias(
      flat_tokens[ref]["value"], flat_tokens, visited | {ref}
    )
    resolved = resolved.replace("{" + ref + "}", str(inner))
  return resolved


# ---------------------------------------------------------------------------
# Color helpers
# ---------------------------------------------------------------------------

def hex_to_rgb(hex_str):
  """#RRGGBB to (r, g, b) ints 0-255. Returns None on bad format."""
  h = hex_str.strip().lstrip("#")
  if len(h) == 3:
    h = h[0]*2 + h[1]*2 + h[2]*2
  elif len(h) == 8:
    h = h[:6]
  if len(h) != 6:
    return None
  try:
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))
  except ValueError:
    return None


def relative_luminance(r, g, b):
  """WCAG 2.0 relative luminance from sRGB 0-255."""
  def lin(c):
    c = c / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
  return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b)


def contrast_ratio(lum1, lum2):
  """WCAG contrast ratio between two luminance values."""
  return (max(lum1, lum2) + 0.05) / (min(lum1, lum2) + 0.05)


def is_hex_color(value):
  return bool(re.fullmatch(
    r"#([0-9a-fA-F]{3}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})", str(value).strip()
  ))


def is_dimension(value):
  return bool(re.fullmatch(r"-?[\d.]+(%|px|rem|em)", str(value).strip()))


# ---------------------------------------------------------------------------
# Validation phases
# ---------------------------------------------------------------------------

def validate_structure(data, flat_tokens):
  """Phase 1: $meta present with name + version."""
  errors = []
  meta = data.get("$meta", {})
  if not meta:
    errors.append("Missing $meta section")
  else:
    if "name" not in meta:
      errors.append("$meta.name is missing")
    if "version" not in meta:
      errors.append("$meta.version is missing")
  return errors


def validate_aliases(flat_tokens):
  """Phase 2: All {path} aliases resolve to existing tokens."""
  errors = []
  alias_count = 0
  for path, token in flat_tokens.items():
    refs = extract_alias_paths(str(token.get("value", "")))
    alias_count += len(refs)
    for ref in refs:
      if ref not in flat_tokens:
        errors.append(f"Unresolved alias: '{{{ref}}}' in '{path}'")
  return errors, alias_count


def validate_circular(flat_tokens):
  """Phase 3: No circular alias chains."""
  errors = []
  detected = set()
  def dfs(path, chain):
    if path in chain:
      idx = chain.index(path)
      cycle = chain[idx:] + [path]
      key = tuple(sorted(cycle))
      if key not in detected:
        detected.add(key)
        errors.append("Circular: " + " -> ".join(cycle))
      return
    if path not in flat_tokens:
      return
    for ref in extract_alias_paths(str(flat_tokens[path].get("value", ""))):
      dfs(ref, chain + [path])
  for path in flat_tokens:
    dfs(path, [])
  return errors


def validate_contrast(data, flat_tokens):
  """Phase 4: WCAG contrast for text-on-surface pairs in color.semantic."""
  errors = []
  warnings = []
  semantic = {}
  color_sec = data.get("color", {}).get("semantic", {})
  for key, node in color_sec.items():
    if not isinstance(node, dict) or "value" not in node:
      continue
    try:
      resolved = resolve_alias(node["value"], flat_tokens)
    except (ValueError, KeyError):
      continue
    if is_hex_color(resolved):
      semantic[key] = resolved

  text_keys = [k for k in semantic if k.startswith("text-")]
  bg_keys = [k for k in semantic if any(
    k.startswith(p) for p in ("background", "surface", "tooltip")
  )]

  for tk in text_keys:
    rgb_t = hex_to_rgb(semantic[tk])
    if not rgb_t:
      continue
    lum_t = relative_luminance(*rgb_t)
    # Muted/disabled text: 3:1, normal text: 4.5:1
    threshold = 3.0 if "muted" in tk or "disabled" in tk else 4.5
    for bk in bg_keys:
      rgb_b = hex_to_rgb(semantic[bk])
      if not rgb_b:
        continue
      ratio = contrast_ratio(lum_t, relative_luminance(*rgb_b))
      if ratio < threshold:
        errors.append(
          f"Contrast FAIL: {tk} on {bk} = {ratio:.1f}:1 (need {threshold}:1)"
        )
      elif ratio < 4.5 and threshold < 4.5:
        warnings.append(f"Contrast low: {tk} on {bk} = {ratio:.1f}:1")

  return errors, warnings


def validate_types(data, flat_tokens):
  """Phase 5: Type validation for color and dimension sections."""
  errors = []
  def check(section_key, section_data, inherited_type=None):
    t = section_data.get("$type", inherited_type)
    for key, node in section_data.items():
      if key.startswith("$") or not isinstance(node, dict):
        continue
      path = f"{section_key}.{key}" if section_key else key
      if "value" in node:
        raw = str(node["value"])
        try:
          resolved = resolve_alias(raw, flat_tokens)
        except (ValueError, KeyError):
          resolved = raw
        if t == "color" and not raw.startswith("{") and not is_hex_color(resolved):
          # Allow rgba() and other CSS color functions
          if not resolved.startswith("rgba(") and not resolved.startswith("hsla("):
            errors.append(f"Type: '{path}' ($type=color) has invalid value '{resolved}'")
        elif t == "dimension" and not raw.startswith("{") and not is_dimension(resolved):
          errors.append(f"Type: '{path}' ($type=dimension) has invalid value '{resolved}'")
      else:
        check(path, node, t)
  for top_key, top_val in data.items():
    if top_key.startswith("$") or not isinstance(top_val, dict):
      continue
    check(top_key, top_val)
  return errors


# Scaffold integrity: required categories and semantic tokens
REQUIRED_CATEGORIES = ["color", "typography", "spacing", "radius", "effects"]
REQUIRED_SEMANTIC = [
  "background", "surface", "surface-hover",
  "border-subtle", "border-default", "border-strong",
  "text-primary", "text-secondary", "text-muted",
  "primary", "success", "warning", "error", "info",
  "state-hover", "state-focus", "state-pressed",
  "skeleton-base", "skeleton-shimmer", "overlay",
]


def validate_scaffold(data, flat_tokens):
  """Phase 6: Scaffold integrity — all required categories and tokens present."""
  errors = []
  for cat in REQUIRED_CATEGORIES:
    if cat not in data:
      errors.append(f"Missing required category: '{cat}'")

  semantic = data.get("color", {}).get("semantic", {})
  for tok in REQUIRED_SEMANTIC:
    if tok not in semantic:
      errors.append(f"Missing required semantic token: 'color.semantic.{tok}'")

  # Check elevation system: at least 3 surface levels
  surface_count = sum(1 for k in semantic if k.startswith("surface"))
  if surface_count < 2:
    errors.append(f"Elevation: only {surface_count} surface levels (need 2+)")

  # Check state layers
  state_count = sum(1 for k in semantic if k.startswith("state-"))
  if state_count < 3:
    errors.append(f"State layers: only {state_count} found (need hover/focus/pressed)")

  # Check borders hierarchy
  border_count = sum(1 for k in semantic if k.startswith("border-"))
  if border_count < 3:
    errors.append(f"Borders: only {border_count} found (need subtle/default/strong)")

  return errors


# ---------------------------------------------------------------------------
# CSS Generation
# ---------------------------------------------------------------------------

STRIP_TIERS = {"core", "semantic", "scale"}


def build_css_name(section, parts):
  """Build CSS variable name from section + path parts."""
  stripped = [p for p in parts if p not in STRIP_TIERS]
  if section == "typography":
    if stripped and stripped[0].startswith("font-"):
      return "--" + "-".join(stripped)
    if stripped:
      return "--font-size-" + "-".join(stripped)
    return "--font"
  prefix = section
  if stripped:
    return f"--{prefix}-" + "-".join(stripped)
  return f"--{prefix}"


def collect_leaves(node, parts):
  """Yield (path_parts, raw_value) for leaf tokens."""
  if isinstance(node, dict) and "value" in node:
    yield parts, node["value"]
    return
  if not isinstance(node, dict):
    return
  for key, child in node.items():
    if key.startswith("$"):
      continue
    yield from collect_leaves(child, parts + [key])


def generate_css(data, output_path):
  """Generate CSS custom properties file from tokens."""
  meta = data.get("$meta", {})
  name = meta.get("name", "Design System")
  version = meta.get("version", "")
  header = f"{name} v{version}" if version else name

  # Build lookup for alias resolution
  all_vars = {}
  sections = [k for k in data if not k.startswith("$")]
  for section in sections:
    if section == "rules":
      continue
    for parts, _ in collect_leaves(data[section], []):
      full_path = tuple([section] + parts)
      css_name = build_css_name(section, parts)
      all_vars[full_path] = css_name

  lines = [
    f"/* {header}",
    " * Generated by /design build (build_system.py)",
    " * DO NOT EDIT — regenerate with: /design sync */",
    "",
    ":root {",
  ]

  total = 0
  last_section = None

  for section in sections:
    if section == "rules":
      continue
    for parts, raw_value in collect_leaves(data[section], []):
      if section != last_section:
        if last_section is not None:
          lines.append("")
        lines.append(f"  /* {section.title()} */")
        last_section = section

      css_name = build_css_name(section, parts)

      # Resolve alias to var() reference
      alias_match = re.fullmatch(r"\{([^}]+)\}", raw_value.strip())
      if alias_match:
        alias_path = tuple(alias_match.group(1).split("."))
        if alias_path in all_vars:
          css_value = f"var({all_vars[alias_path]})"
        else:
          ref_name = build_css_name(alias_path[0], list(alias_path[1:]))
          css_value = f"var({ref_name})"
      else:
        css_value = raw_value
        if section == "typography" and " " in raw_value:
          css_value = f"'{raw_value}'"

      lines.append(f"  {css_name}: {css_value};")
      total += 1

  lines.append("}")
  lines.append("")

  with open(output_path, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

  return total


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
  parser = ArgumentParser(description="Build and validate a design system")
  parser.add_argument("input", help="Path to design-tokens.json")
  parser.add_argument("--css", help="Output CSS file (optional)", default=None)
  parser.add_argument("--verbose", action="store_true", help="Show all checks")
  args = parser.parse_args()

  input_path = os.path.abspath(args.input)
  if not os.path.isfile(input_path):
    print(f"Error: file not found: {input_path}", file=sys.stderr)
    sys.exit(2)

  try:
    with open(input_path, "r", encoding="utf-8") as f:
      data = json.load(f)
  except json.JSONDecodeError as e:
    print(f"Error: invalid JSON — {e}", file=sys.stderr)
    sys.exit(2)

  flat = flatten_tokens(data)
  core = sum(1 for p in flat if "semantic" not in p.split("."))
  semantic = len(flat) - core

  print("=== Design System Build ===")
  print(f"File: {input_path}")
  print(f"Tokens: {len(flat)} total ({core} core, {semantic} semantic)")
  print()

  all_errors = []
  all_warnings = []

  # Phase 1: Structure
  errs = validate_structure(data, flat)
  all_errors.extend(errs)
  _report("Structure", errs, [], args.verbose)

  # Phase 2: Aliases
  errs, alias_count = validate_aliases(flat)
  all_errors.extend(errs)
  _report(f"Aliases ({alias_count} refs)", errs, [], args.verbose)

  # Phase 3: Circular deps
  errs = validate_circular(flat)
  all_errors.extend(errs)
  _report("Circular deps", errs, [], args.verbose)

  # Phase 4: Contrast
  errs, warns = validate_contrast(data, flat)
  all_errors.extend(errs)
  all_warnings.extend(warns)
  _report("WCAG contrast", errs, warns, args.verbose)

  # Phase 5: Types
  errs = validate_types(data, flat)
  all_errors.extend(errs)
  _report("Type validation", errs, [], args.verbose)

  # Phase 6: Scaffold integrity
  errs = validate_scaffold(data, flat)
  all_errors.extend(errs)
  _report("Scaffold integrity", errs, [], args.verbose)

  # CSS generation
  if args.css:
    css_path = os.path.abspath(args.css)
    css_count = generate_css(data, css_path)
    print(f"[CSS]  Generated {css_count} variables → {css_path}")

  # Summary
  print()
  n_err = len(all_errors)
  n_warn = len(all_warnings)
  if n_err > 0:
    print(f"Result: FAIL ({n_err} errors, {n_warn} warnings)")
    sys.exit(1)
  elif n_warn > 0:
    print(f"Result: PASS ({n_warn} warnings, 0 errors)")
  else:
    print("Result: PASS (0 warnings, 0 errors)")
  sys.exit(0)


def _report(label, errors, warnings, verbose):
  """Print single validation phase result."""
  if errors:
    for e in errors:
      print(f"[FAIL] {e}")
  elif warnings:
    for w in warnings:
      print(f"[WARN] {w}")
  else:
    print(f"[PASS] {label}")
  if verbose and not errors and not warnings:
    pass


if __name__ == "__main__":
  main()
