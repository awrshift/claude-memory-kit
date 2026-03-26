#!/usr/bin/env python3
"""
generate_tailwind.py — Generate Tailwind v4 @theme inline CSS from design-tokens.json.

Usage:
  python3 generate_tailwind.py path/to/design-tokens.json
  python3 generate_tailwind.py path/to/design-tokens.json --output path/to/output.css
"""

import json
import os
import re
import sys
from argparse import ArgumentParser


# Organizational tiers to strip from CSS variable names
STRIP_TIERS = {"core", "semantic", "scale"}

# Metadata keys to skip during traversal
META_PREFIX = "$"

# Mapping from token category + tier to CSS variable prefix
CATEGORY_PREFIXES = {
  "color": "color",
  "typography": None,  # handled specially per key
  "spacing": "spacing",
  "radius": "radius",
  "shadow": "shadow",
  "border": "border",
  "motion": "motion",
  "breakpoint": "breakpoint",
}

# Special typography renames
TYPOGRAPHY_FONT_SIZE_TIER = "scale"


def load_tokens(path):
  with open(path, "r", encoding="utf-8") as f:
    return json.load(f)


def is_leaf(node):
  """A leaf token has a 'value' key."""
  return isinstance(node, dict) and "value" in node


def collect_raw_tokens(data):
  """
  Walk the token tree and collect all leaf tokens as:
    { "dotted.path.key": "raw_value", ... }

  Keys starting with "$" are skipped (metadata).
  """
  result = {}

  def walk(node, path_parts):
    if not isinstance(node, dict):
      return
    for key, val in node.items():
      if key.startswith(META_PREFIX):
        continue
      current_path = path_parts + [key]
      if is_leaf(val):
        result[".".join(current_path)] = val["value"]
      elif isinstance(val, dict):
        walk(val, current_path)

  walk(data, [])
  return result


def resolve_aliases(raw_tokens):
  """
  Resolve all alias references of the form {dotted.path}.
  Performs iterative resolution until no more aliases remain or
  a cycle is detected.
  """
  resolved = dict(raw_tokens)
  alias_pattern = re.compile(r"^\{(.+)\}$")

  max_iterations = len(resolved) + 1
  for _ in range(max_iterations):
    changed = False
    for key, value in resolved.items():
      if not isinstance(value, str):
        continue
      match = alias_pattern.match(value)
      if match:
        ref_path = match.group(1)
        if ref_path in resolved:
          ref_val = resolved[ref_path]
          # Only resolve if the target is itself concrete
          if not alias_pattern.match(str(ref_val)):
            resolved[key] = ref_val
            changed = True
    if not changed:
      break

  # Warn about any unresolved aliases remaining
  for key, value in resolved.items():
    if isinstance(value, str) and alias_pattern.match(value):
      print(
        f"  Warning: unresolved alias '{value}' for token '{key}'",
        file=sys.stderr,
      )

  return resolved


def derive_css_var(dotted_path):
  """
  Convert a dotted token path to a CSS variable name, stripping
  organizational tiers and applying category-specific naming rules.

  Examples:
    color.core.cyan-500       → --color-cyan-500
    color.semantic.primary    → --color-primary
    typography.scale.base     → --font-size-base
    typography.font-primary   → --font-primary
    typography.font-mono      → --font-mono
    spacing.unit              → --spacing-unit
    spacing.max-width         → --spacing-max-width
    radius.md                 → --radius-md
  """
  parts = dotted_path.split(".")
  if not parts:
    return None

  category = parts[0]

  # Strip the category itself from the remaining parts
  rest = parts[1:]

  # Strip known organizational tiers
  rest = [p for p in rest if p not in STRIP_TIERS]

  if not rest:
    return None

  if category == "typography":
    # Detect font-size group (was under "scale" tier)
    # We identify it by checking if the original path contained "scale"
    original_parts = dotted_path.split(".")
    if TYPOGRAPHY_FONT_SIZE_TIER in original_parts:
      prefix = "font-size"
    elif rest[0].startswith("font-"):
      # e.g. font-primary, font-mono → keep as-is
      prefix = None
    else:
      prefix = "font"

    if prefix is None:
      # rest[0] already starts with "font-"
      var_name = "-".join(rest)
    else:
      var_name = prefix + "-" + "-".join(rest)
  else:
    prefix = CATEGORY_PREFIXES.get(category, category)
    var_name = prefix + "-" + "-".join(rest)

  return "--" + var_name


def format_value(css_var, raw_value):
  """
  Format a token value for CSS output.
  Font family values containing spaces are wrapped in single quotes.
  """
  value = str(raw_value)
  # Wrap font names that contain spaces in single quotes
  if css_var.startswith("--font-") and not css_var.startswith("--font-size") and " " in value:
    value = f"'{value}'"
  return value


def group_variables(css_vars):
  """
  Group CSS variables into sections for readable output.
  Returns an ordered list of (section_label, [(var, value), ...]).
  """
  sections = {
    "Colors — Core": [],
    "Colors — Semantic": [],
    "Typography": [],
    "Font Sizes": [],
    "Spacing": [],
    "Border Radius": [],
    "Other": [],
  }

  for css_var, value in css_vars:
    if css_var.startswith("--color-"):
      # Distinguish core vs semantic by checking if var appears in both
      # We track this separately during build; for grouping, use heuristic:
      # semantic vars are typically single-word concept names
      sections["Other"].append((css_var, value))  # placeholder, regrouped below
    elif css_var.startswith("--font-size"):
      sections["Font Sizes"].append((css_var, value))
    elif css_var.startswith("--font-"):
      sections["Typography"].append((css_var, value))
    elif css_var.startswith("--spacing-"):
      sections["Spacing"].append((css_var, value))
    elif css_var.startswith("--radius-"):
      sections["Border Radius"].append((css_var, value))
    else:
      sections["Other"].append((css_var, value))

  return sections


def build_css_vars(data):
  """
  Main pipeline: collect → resolve → derive CSS var names → group.
  Returns (ordered_sections, meta) where ordered_sections is a list of
  (label, [(css_var, formatted_value), ...]).
  """
  meta = data.get("$meta", {})
  raw_tokens = collect_raw_tokens(data)
  resolved = resolve_aliases(raw_tokens)

  # Build two structures:
  # 1. dotted_path → css_var (for categorization)
  # 2. dotted_path → (css_var, formatted_value)
  path_to_css = {}
  for dotted_path in resolved:
    css_var = derive_css_var(dotted_path)
    if css_var:
      path_to_css[dotted_path] = css_var

  # Determine which css_vars are "core" colors vs "semantic" colors
  # by checking if "semantic" appears in the original dotted path
  core_color_vars = set()
  semantic_color_vars = set()
  for dotted_path, css_var in path_to_css.items():
    if css_var.startswith("--color-"):
      parts = dotted_path.split(".")
      if "semantic" in parts:
        semantic_color_vars.add(css_var)
      elif "core" in parts:
        core_color_vars.add(css_var)

  # Build the output sections in order
  sections_ordered = [
    ("Colors — Core", []),
    ("Colors — Semantic", []),
    ("Typography", []),
    ("Font Sizes", []),
    ("Spacing", []),
    ("Border Radius", []),
    ("Other", []),
  ]
  section_map = {label: lst for label, lst in sections_ordered}

  seen_vars = set()  # deduplicate (multiple paths can map to same var)

  for dotted_path, css_var in path_to_css.items():
    if css_var in seen_vars:
      continue
    seen_vars.add(css_var)

    raw_value = resolved[dotted_path]
    formatted = format_value(css_var, raw_value)

    if css_var.startswith("--color-"):
      if css_var in semantic_color_vars:
        section_map["Colors — Semantic"].append((css_var, formatted))
      else:
        section_map["Colors — Core"].append((css_var, formatted))
    elif css_var.startswith("--font-size"):
      section_map["Font Sizes"].append((css_var, formatted))
    elif css_var.startswith("--font-"):
      section_map["Typography"].append((css_var, formatted))
    elif css_var.startswith("--spacing-"):
      section_map["Spacing"].append((css_var, formatted))
    elif css_var.startswith("--radius-"):
      section_map["Border Radius"].append((css_var, formatted))
    else:
      section_map["Other"].append((css_var, formatted))

  # Sort each section alphabetically by var name for consistency
  for _, lst in sections_ordered:
    lst.sort(key=lambda x: x[0])

  return sections_ordered, meta


def render_css(sections_ordered, meta):
  """Render the final CSS string."""
  name = meta.get("name", "Design System")
  version = meta.get("version", "")
  header_name = f"{name} {version}".strip()

  lines = [
    f"/* Design System: {header_name}",
    " * Generated by /design sync",
    " * DO NOT EDIT — regenerate with: /design sync */",
    "",
    "@theme inline {",
  ]

  total_vars = 0
  for label, entries in sections_ordered:
    if not entries:
      continue
    lines.append(f"  /* {label} */")
    for css_var, value in entries:
      lines.append(f"  {css_var}: {value};")
      total_vars += 1
    lines.append("")

  # Remove trailing blank line inside block if present
  if lines and lines[-1] == "":
    lines.pop()

  lines.append("}")
  lines.append("")

  return "\n".join(lines), total_vars


def parse_args():
  parser = ArgumentParser(
    description="Generate Tailwind v4 @theme inline CSS from design-tokens.json"
  )
  parser.add_argument("input", help="Path to design-tokens.json")
  parser.add_argument(
    "--output",
    help="Output CSS file path (default: <input-dir>/design-tokens.tailwind.css)",
  )
  return parser.parse_args()


def main():
  args = parse_args()

  input_path = os.path.abspath(args.input)
  if not os.path.isfile(input_path):
    print(f"Error: file not found: {input_path}", file=sys.stderr)
    sys.exit(1)

  if args.output:
    output_path = os.path.abspath(args.output)
  else:
    input_dir = os.path.dirname(input_path)
    output_path = os.path.join(input_dir, "design-tokens.tailwind.css")

  data = load_tokens(input_path)
  sections_ordered, meta = build_css_vars(data)
  css_content, total_vars = render_css(sections_ordered, meta)

  with open(output_path, "w", encoding="utf-8") as f:
    f.write(css_content)

  print(f"Generated {total_vars} variables to {output_path}")


if __name__ == "__main__":
  main()
