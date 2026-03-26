#!/usr/bin/env python3
"""Generate CSS custom properties (:root block) from design-tokens.json.

Usage:
  python3 generate_css_vars.py path/to/design-tokens.json
  python3 generate_css_vars.py path/to/design-tokens.json --output path/to/output.css
"""

import json
import os
import re
import sys
from argparse import ArgumentParser

# Organizational tiers that are stripped from variable names.
STRIP_TIERS = {"core", "semantic", "scale"}

# Top-level sections that map to specific CSS variable prefixes.
# Keys are JSON top-level keys; values are the CSS prefix fragment.
SECTION_PREFIX = {
  "color": "color",
  "typography": None,   # handled specially: font-* vs --font-size-*
  "spacing": "spacing",
  "radius": "radius",
}

# The "scale" tier under typography maps to font-size.
TYPOGRAPHY_SCALE_PREFIX = "font-size"
TYPOGRAPHY_FONT_PREFIX = "font"


def load_tokens(path):
  with open(path, "r", encoding="utf-8") as f:
    return json.load(f)


def is_leaf(node):
  """A token leaf has a 'value' key."""
  return isinstance(node, dict) and "value" in node


def collect_leaves(node, path_parts):
  """Recursively yield (path_parts, value) for every leaf token.

  path_parts is a list of string keys (excluding $meta/$type).
  """
  if is_leaf(node):
    yield path_parts, node["value"]
    return
  if not isinstance(node, dict):
    return
  for key, child in node.items():
    if key.startswith("$"):
      continue
    yield from collect_leaves(child, path_parts + [key])


def strip_tiers(parts):
  """Remove organizational tier names from path parts."""
  return [p for p in parts if p not in STRIP_TIERS]


def resolve_alias(value, all_vars):
  """Convert {path.to.token} alias syntax to a CSS var() reference.

  Resolves the alias path to the CSS variable name that was already computed
  for the referenced token.  Returns var(--name) if found, otherwise the
  raw value unchanged.
  """
  match = re.fullmatch(r"\{([^}]+)\}", value.strip())
  if not match:
    return value, False
  alias_path = match.group(1).split(".")
  key = tuple(alias_path)
  if key in all_vars:
    return f"var({all_vars[key]})", True
  # Fallback: construct variable name from alias path using the same rules
  css_name = alias_to_css_name(alias_path)
  return f"var({css_name})", True


def alias_to_css_name(alias_parts):
  """Derive a CSS variable name from an alias path like color.core.cyan-500."""
  section = alias_parts[0] if alias_parts else ""
  rest = alias_parts[1:]
  rest_stripped = strip_tiers(rest)
  return build_css_name(section, rest_stripped)


def build_css_name(section, stripped_parts):
  """Build the CSS variable name (with -- prefix) for a section + stripped parts."""
  if section == "typography":
    if stripped_parts and stripped_parts[0] == "font-primary":
      return "--font-primary"
    if stripped_parts and stripped_parts[0] == "font-mono":
      return "--font-mono"
    # Anything from the scale tier has already been stripped to just the scale key
    # Detect whether this came from scale by looking at the token being processed —
    # callers pass already-stripped parts, so we check if it looks like a size token.
    # Convention: typography font-* keys at top level → --font-*
    #             typography non-font top-level keys → --font-size-*
    if stripped_parts:
      first = stripped_parts[0]
      if first.startswith("font-"):
        suffix = "-".join(stripped_parts)
        return f"--{suffix}"
      else:
        suffix = "-".join(stripped_parts)
        return f"--{TYPOGRAPHY_SCALE_PREFIX}-{suffix}"
    return "--font"
  if section and stripped_parts:
    prefix = SECTION_PREFIX.get(section, section)
    suffix = "-".join(stripped_parts)
    return f"--{prefix}-{suffix}"
  if section and not stripped_parts:
    prefix = SECTION_PREFIX.get(section, section)
    return f"--{prefix}"
  return "--" + "-".join(stripped_parts)


def quote_font_value(value):
  """Wrap font family values that contain spaces in single quotes."""
  if " " in value:
    return f"'{value}'"
  return value


def build_section_comment(section, tier):
  """Return a CSS comment header for a section/tier group."""
  labels = {
    "color": "Colors",
    "typography": "Typography",
    "spacing": "Spacing",
    "radius": "Border Radius",
  }
  tier_labels = {
    "core": "Core",
    "semantic": "Semantic",
    "scale": "Font Sizes",
    None: "",
  }
  section_label = labels.get(section, section.title())
  tier_label = tier_labels.get(tier, tier.title() if tier else "")
  if tier_label:
    return f"  /* {section_label} — {tier_label} */"
  return f"  /* {section_label} */"


def detect_tier(parts):
  """Return the first part of a path if it is a known organisational tier, else None."""
  if parts and parts[0] in STRIP_TIERS:
    return parts[0]
  return None


def format_value(section, stripped_parts, raw_value):
  """Format the raw token value for CSS output."""
  if section == "typography":
    if stripped_parts and stripped_parts[0].startswith("font-"):
      return quote_font_value(raw_value)
  return raw_value


def generate(tokens_path, output_path):
  tokens = load_tokens(tokens_path)

  meta = tokens.get("$meta", {})
  name = meta.get("name", "Design System")
  version = meta.get("version", "")
  header_name = f"{name} v{version}" if version else name

  # First pass: collect every (section, sub_parts, raw_value) without resolving aliases,
  # and build a mapping from original alias path tuple → css variable name.
  # This is needed so alias resolution can look up names of sibling tokens.
  all_vars = {}  # (alias_path_tuple) → css_var_name

  top_level_sections = [k for k in tokens if not k.startswith("$")]

  for section in top_level_sections:
    section_node = tokens[section]
    for path_parts, raw_value in collect_leaves(section_node, []):
      stripped = strip_tiers(path_parts)
      css_name = build_css_name(section, stripped)
      # Store under the full original path for alias lookup
      full_path = tuple([section] + path_parts)
      all_vars[full_path] = css_name

  # Second pass: produce output lines grouped by section and tier.
  lines = []
  lines.append(f"/* Design System: {header_name}")
  lines.append(" * Generated by /design sync")
  lines.append(" * DO NOT EDIT — regenerate with: /design sync */")
  lines.append("")
  lines.append(":root {")

  total_vars = 0
  last_group = None  # (section, tier) tuple for blank-line separation

  for section in top_level_sections:
    section_node = tokens[section]
    leaves = list(collect_leaves(section_node, []))

    # Determine grouping: separate core/semantic tiers for color,
    # scale tier for typography, etc.
    for path_parts, raw_value in leaves:
      tier = detect_tier(path_parts)
      group = (section, tier)

      if group != last_group:
        if last_group is not None:
          lines.append("")
        lines.append(build_section_comment(section, tier))
        last_group = group

      stripped = strip_tiers(path_parts)
      css_name = build_css_name(section, stripped)

      # Resolve alias or format raw value
      is_alias = re.fullmatch(r"\{[^}]+\}", raw_value.strip()) is not None
      if is_alias:
        css_value, _ = resolve_alias(raw_value, all_vars)
      else:
        css_value = format_value(section, stripped, raw_value)

      lines.append(f"  {css_name}: {css_value};")
      total_vars += 1

  lines.append("}")
  lines.append("")

  css_content = "\n".join(lines)

  with open(output_path, "w", encoding="utf-8") as f:
    f.write(css_content)

  print(f"Generated {total_vars} variables to {output_path}")


def main():
  parser = ArgumentParser(
    description="Generate CSS custom properties from design-tokens.json"
  )
  parser.add_argument("input", help="Path to design-tokens.json")
  parser.add_argument(
    "--output",
    help="Output CSS file path (default: design-tokens.css next to input)",
    default=None,
  )
  args = parser.parse_args()

  input_path = os.path.abspath(args.input)
  if not os.path.isfile(input_path):
    print(f"Error: file not found: {input_path}", file=sys.stderr)
    sys.exit(1)

  if args.output:
    output_path = os.path.abspath(args.output)
  else:
    input_dir = os.path.dirname(input_path)
    output_path = os.path.join(input_dir, "design-tokens.css")

  generate(input_path, output_path)


if __name__ == "__main__":
  main()
