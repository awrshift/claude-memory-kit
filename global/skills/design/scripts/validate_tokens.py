#!/usr/bin/env python3
"""
Design Tokens Validator
Validates a design-tokens.json file for structure, alias resolution,
circular dependencies, WCAG contrast ratios, and type correctness.
"""

import json
import re
import sys


# ---------------------------------------------------------------------------
# Token tree helpers
# ---------------------------------------------------------------------------

def flatten_tokens(data, prefix="", result=None):
  """
  Walk the JSON tree and return a flat dict of {dot.path: token_object}.

  Keys starting with "$" ($meta, $type, $value) are metadata and are skipped
  when building path segments.  A node is considered a leaf token when it
  contains a "value" key.
  """
  if result is None:
    result = {}

  for key, node in data.items():
    if key.startswith("$"):
      continue  # skip $meta, $type, $value, etc.

    path = f"{prefix}.{key}" if prefix else key

    if isinstance(node, dict):
      if "value" in node:
        # Leaf token
        result[path] = node
      else:
        # Branch — recurse
        flatten_tokens(node, path, result)

  return result


def extract_alias_paths(value):
  """
  Return a list of dot-paths referenced inside {curly.braces} in a string.

  Supports both pure aliases ({color.core.cyan-500}) and partial string
  aliases ("1px solid {color.core.slate-700}").
  """
  return re.findall(r"\{([^}]+)\}", str(value))


# ---------------------------------------------------------------------------
# Alias resolution
# ---------------------------------------------------------------------------

def resolve_alias(value, flat_tokens, visited=None):
  """
  Resolve {path} alias references in *value* using flat_tokens.

  Returns the fully-resolved string value.
  Raises ValueError on circular dependency or missing reference.
  *visited* tracks the chain of paths currently being resolved.
  """
  if visited is None:
    visited = set()

  refs = extract_alias_paths(str(value))
  if not refs:
    return value

  resolved = str(value)
  for ref in refs:
    if ref in visited:
      chain = " -> ".join(sorted(visited)) + " -> " + ref
      raise ValueError(f"Circular dependency detected: {chain}")

    if ref not in flat_tokens:
      raise KeyError(f"Alias target not found: {{{ref}}}")

    new_visited = visited | {ref}
    target_value = flat_tokens[ref]["value"]
    inner_resolved = resolve_alias(target_value, flat_tokens, new_visited)
    resolved = resolved.replace("{" + ref + "}", str(inner_resolved))

  return resolved


# ---------------------------------------------------------------------------
# Color helpers
# ---------------------------------------------------------------------------

def hex_to_rgb(hex_str):
  """
  Convert a CSS hex color string to an (r, g, b) tuple of ints 0-255.

  Accepts #RGB, #RRGGBB, #RRGGBBAA.  Returns None if the format is invalid.
  """
  hex_str = hex_str.strip()
  if not hex_str.startswith("#"):
    return None

  h = hex_str[1:]

  if len(h) == 3:
    h = h[0]*2 + h[1]*2 + h[2]*2
  elif len(h) == 6:
    pass
  elif len(h) == 8:
    h = h[:6]  # drop alpha for luminance calculation
  else:
    return None

  try:
    r = int(h[0:2], 16)
    g = int(h[2:4], 16)
    b = int(h[4:6], 16)
    return (r, g, b)
  except ValueError:
    return None


def relative_luminance(r, g, b):
  """
  Calculate WCAG 2.0 relative luminance from sRGB values (0-255).

  Formula: https://www.w3.org/TR/WCAG20/#relativeluminancedef
  """
  def linearize(c):
    c = c / 255.0
    if c <= 0.04045:
      return c / 12.92
    return ((c + 0.055) / 1.055) ** 2.4

  r_lin = linearize(r)
  g_lin = linearize(g)
  b_lin = linearize(b)
  return 0.2126 * r_lin + 0.7152 * g_lin + 0.0722 * b_lin


def contrast_ratio(lum1, lum2):
  """
  Calculate WCAG contrast ratio between two relative luminance values.

  Returns a float; the formula is (L_lighter + 0.05) / (L_darker + 0.05).
  """
  lighter = max(lum1, lum2)
  darker = min(lum1, lum2)
  return (lighter + 0.05) / (darker + 0.05)


def is_valid_hex_color(value):
  """Return True if *value* is a valid CSS hex color string."""
  return bool(re.fullmatch(r"#([0-9a-fA-F]{3}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})", str(value).strip()))


def is_valid_dimension(value):
  """Return True if *value* ends with px, rem, em, or %."""
  return bool(re.fullmatch(r"-?[\d.]+(%|px|rem|em)", str(value).strip()))


# ---------------------------------------------------------------------------
# Counting helpers
# ---------------------------------------------------------------------------

def count_tokens_by_layer(flat_tokens):
  """
  Split tokens into 'core' and 'semantic' buckets based on path depth/naming.

  Convention: paths containing '.semantic.' or starting with a category that
  has 'semantic' as a direct child are semantic; others are core.
  """
  core = 0
  semantic = 0
  for path in flat_tokens:
    parts = path.split(".")
    if "semantic" in parts:
      semantic += 1
    else:
      core += 1
  return core, semantic


# ---------------------------------------------------------------------------
# Validation phases
# ---------------------------------------------------------------------------

def validate_structure(data, flat_tokens, verbose):
  """
  Phase 1: JSON schema validation.

  Checks:
  - $meta present with name + version
  - Every leaf token has a "value" key (already enforced by flatten_tokens
    which only collects nodes with "value", so we verify no branch node was
    silently dropped)
  """
  errors = []
  warnings = []

  meta = data.get("$meta", {})
  if not meta:
    errors.append("Missing $meta section")
  else:
    if "name" not in meta:
      errors.append("$meta.name is missing")
    if "version" not in meta:
      errors.append("$meta.version is missing")

  if verbose:
    for path, token in flat_tokens.items():
      if "value" not in token:
        errors.append(f"Token '{path}' has no 'value' key")

  return errors, warnings


def validate_aliases(flat_tokens, verbose):
  """
  Phase 2: Verify all {path} alias references resolve to existing tokens.

  Returns (errors, warnings, alias_count, circular_paths).
  """
  errors = []
  warnings = []
  alias_count = 0
  circular_paths = []

  for path, token in flat_tokens.items():
    value = str(token.get("value", ""))
    refs = extract_alias_paths(value)
    if not refs:
      continue

    alias_count += len(refs)

    for ref in refs:
      if ref not in flat_tokens:
        errors.append(f"Unresolved alias: '{{{ref}}}' in token '{path}'")

  return errors, warnings, alias_count, circular_paths


def validate_circular_deps(flat_tokens, verbose):
  """
  Phase 3: Detect circular alias chains using DFS with a visited stack.

  Returns (errors, detected_cycles).
  """
  errors = []
  detected = set()

  def _dfs(path, chain):
    """DFS from *path*; *chain* is the current resolution stack (list)."""
    if path in chain:
      cycle_start = chain.index(path)
      cycle = chain[cycle_start:] + [path]
      cycle_key = tuple(sorted(cycle))
      if cycle_key not in detected:
        detected.add(cycle_key)
        errors.append("Circular dependency: " + " -> ".join(cycle))
      return

    if path not in flat_tokens:
      return  # missing ref already caught in phase 2

    value = str(flat_tokens[path].get("value", ""))
    refs = extract_alias_paths(value)
    for ref in refs:
      _dfs(ref, chain + [path])

  for path in flat_tokens:
    _dfs(path, [])

  return errors


def validate_contrast(data, flat_tokens, verbose):
  """
  Phase 4: WCAG contrast ratio checks for semantic color tokens.

  Pairs text-* tokens against background-* / surface-* tokens within the
  semantic color group.  Warns if ratio < 4.5:1 (AA), errors if < 3:1.
  """
  errors = []
  warnings = []

  # Collect resolved values for semantic color tokens
  semantic_colors = {}  # path -> resolved hex value

  color_section = data.get("color", {})
  if not color_section:
    return errors, warnings

  # Find the $type; default to "color" for the color section
  for top_key, top_val in data.items():
    if top_key.startswith("$"):
      continue
    if not isinstance(top_val, dict):
      continue
    section_type = top_val.get("$type", "")
    if section_type != "color" and top_key != "color":
      continue

    # Look inside for a "semantic" sub-section
    semantic_section = top_val.get("semantic", {})
    for key, node in semantic_section.items():
      if not isinstance(node, dict) or "value" not in node:
        continue
      token_path = f"{top_key}.semantic.{key}"
      raw_value = node["value"]

      try:
        resolved = resolve_alias(raw_value, flat_tokens)
      except (ValueError, KeyError):
        continue  # alias issues are reported in phases 2-3

      if is_valid_hex_color(resolved):
        semantic_colors[key] = resolved

  if not semantic_colors:
    return errors, warnings

  # Identify text tokens and background/surface tokens
  text_keys = [k for k in semantic_colors if "text" in k]
  bg_keys = [k for k in semantic_colors if "background" in k or "surface" in k or "bg" in k]

  if verbose and (text_keys or bg_keys):
    pass  # pairs will be printed when contrast is checked

  for text_key in text_keys:
    text_hex = semantic_colors[text_key]
    text_rgb = hex_to_rgb(text_hex)
    if not text_rgb:
      continue
    text_lum = relative_luminance(*text_rgb)

    for bg_key in bg_keys:
      bg_hex = semantic_colors[bg_key]
      bg_rgb = hex_to_rgb(bg_hex)
      if not bg_rgb:
        continue
      bg_lum = relative_luminance(*bg_rgb)

      ratio = contrast_ratio(text_lum, bg_lum)
      label = f"{text_key} on {bg_key} = {ratio:.1f}:1"

      if ratio < 3.0:
        errors.append(f"Contrast ratio FAIL (< 3:1): {label}")
      elif ratio < 4.5:
        warnings.append(f"Contrast ratio: {label} (AA requires 4.5:1)")

  return errors, warnings


def validate_types(data, flat_tokens, verbose):
  """
  Phase 5: Type validation.

  For tokens in sections typed as "color", hex format is required.
  For tokens in sections typed as "dimension", a unit suffix is required.
  """
  errors = []
  warnings = []

  def _check_section(section_key, section_data, inherited_type=None):
    section_type = section_data.get("$type", inherited_type)
    for key, node in section_data.items():
      if key.startswith("$"):
        continue
      if not isinstance(node, dict):
        continue

      path = f"{section_key}.{key}" if section_key else key

      if "value" in node:
        raw = str(node["value"])
        # If it's an alias, resolve it first
        try:
          resolved = resolve_alias(raw, flat_tokens)
        except (ValueError, KeyError):
          resolved = raw  # let alias validator handle it

        if section_type == "color":
          if not raw.startswith("{") and not is_valid_hex_color(resolved):
            errors.append(f"Type error: '{path}' has $type=color but value '{resolved}' is not a valid hex color")
        elif section_type == "dimension":
          if not raw.startswith("{") and not is_valid_dimension(resolved):
            errors.append(f"Type error: '{path}' has $type=dimension but value '{resolved}' has no valid unit (px/rem/em/%)")
      else:
        _check_section(path, node, section_type)

  for top_key, top_val in data.items():
    if top_key.startswith("$"):
      continue
    if isinstance(top_val, dict):
      _check_section(top_key, top_val)

  return errors, warnings


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
  """Entry point: parse args, run validations, print report, exit."""
  args = sys.argv[1:]
  if not args:
    print("Usage: validate_tokens.py <design-tokens.json> [--verbose]")
    sys.exit(2)

  verbose = "--verbose" in args
  file_args = [a for a in args if not a.startswith("--")]
  if not file_args:
    print("Error: no file path provided")
    sys.exit(2)

  token_file = file_args[0]

  # Load file
  try:
    with open(token_file, "r", encoding="utf-8") as fh:
      data = json.load(fh)
  except FileNotFoundError:
    print(f"Error: file not found: {token_file}")
    sys.exit(2)
  except json.JSONDecodeError as exc:
    print(f"Error: invalid JSON — {exc}")
    sys.exit(2)

  flat_tokens = flatten_tokens(data)
  total_tokens = len(flat_tokens)
  core_count, semantic_count = count_tokens_by_layer(flat_tokens)

  print("=== Design Tokens Validation ===")
  print(f"File: {token_file}")
  print(f"Tokens: {total_tokens} total ({core_count} core, {semantic_count} semantic)")
  print()

  all_errors = []
  all_warnings = []

  # Phase 1: structure
  errs, warns = validate_structure(data, flat_tokens, verbose)
  all_errors.extend(errs)
  all_warnings.extend(warns)
  _print_phase("JSON structure valid", errs, warns, verbose)

  # Phase 2: alias resolution
  errs, warns, alias_count, _ = validate_aliases(flat_tokens, verbose)
  all_errors.extend(errs)
  all_warnings.extend(warns)
  _print_phase(f"All aliases resolved ({alias_count} aliases)", errs, warns, verbose)

  # Phase 3: circular deps
  errs = validate_circular_deps(flat_tokens, verbose)
  all_errors.extend(errs)
  _print_phase("No circular dependencies", errs, [], verbose)

  # Phase 4: contrast
  errs, warns = validate_contrast(data, flat_tokens, verbose)
  all_errors.extend(errs)
  all_warnings.extend(warns)
  _print_phase_contrast(errs, warns, verbose)

  # Phase 5: type validation
  errs, warns = validate_types(data, flat_tokens, verbose)
  all_errors.extend(errs)
  all_warnings.extend(warns)
  _print_phase("Type validation", errs, warns, verbose)

  # Final result
  print()
  n_err = len(all_errors)
  n_warn = len(all_warnings)

  if n_err > 0:
    print(f"Result: ERROR ({n_warn} warning{'s' if n_warn != 1 else ''}, {n_err} error{'s' if n_err != 1 else ''})")
    sys.exit(1)
  elif n_warn > 0:
    print(f"Result: WARNING ({n_warn} warning{'s' if n_warn != 1 else ''}, 0 errors)")
    sys.exit(0)
  else:
    print("Result: PASS (0 warnings, 0 errors)")
    sys.exit(0)


def _print_phase(pass_label, errors, warnings, verbose):
  """Print a single validation phase result line."""
  if errors:
    for msg in errors:
      print(f"[ERROR] {msg}")
  elif warnings:
    for msg in warnings:
      print(f"[WARN] {msg}")
  else:
    print(f"[PASS] {pass_label}")

  if verbose and errors:
    pass  # errors already printed above with detail


def _print_phase_contrast(errors, warnings, verbose):
  """Print contrast phase results; handle mixed pass/warn/error states."""
  if errors:
    for msg in errors:
      print(f"[ERROR] {msg}")
  if warnings:
    for msg in warnings:
      print(f"[WARN] {msg}")
  if not errors and not warnings:
    print("[PASS] Contrast ratios (WCAG AA)")


if __name__ == "__main__":
  main()
