#!/usr/bin/env python3
"""
compile_stitch_context.py — Compile design tokens + rules into .stitch-context.md
for Google Stitch MCP (DESIGN.md Section 6 format).

Usage:
  python3 compile_stitch_context.py design-tokens.json [--rules path/to/design-rules.md] [--output path/to/.stitch-context.md]
"""

import sys
import json
import re
import argparse
from pathlib import Path


def load_tokens(path):
  with open(path, encoding="utf-8") as f:
    return json.load(f)


def is_metadata_key(key):
  return key.startswith("$")


def is_leaf(node):
  """A token leaf has a 'value' key (and optionally 'description')."""
  return isinstance(node, dict) and "value" in node


def collect_leaves(node, path=None):
  """
  Walk token tree, yield (dot_path, leaf_dict) for every leaf.
  Skips keys starting with '$' (metadata).
  """
  if path is None:
    path = []
  if is_metadata_key(path[-1] if path else ""):
    return
  if is_leaf(node):
    yield ".".join(path), node
    return
  if isinstance(node, dict):
    for key, child in node.items():
      if is_metadata_key(key):
        continue
      yield from collect_leaves(child, path + [key])


def build_lookup(tokens):
  """Build a flat dict: dot_path -> leaf_dict, skipping top-level metadata."""
  lookup = {}
  for top_key, top_val in tokens.items():
    if is_metadata_key(top_key):
      continue
    for dot_path, leaf in collect_leaves(top_val, [top_key]):
      lookup[dot_path] = leaf
  return lookup


def resolve_alias(value, lookup, depth=0):
  """
  Resolve {path.to.token} aliases recursively.
  Returns the concrete value string, or the original string if no alias.
  """
  if depth > 20:
    return value  # guard against circular refs
  pattern = re.compile(r"\{([^}]+)\}")
  match = pattern.fullmatch(value.strip())
  if match:
    ref_path = match.group(1)
    if ref_path in lookup:
      inner_val = lookup[ref_path].get("value", value)
      return resolve_alias(inner_val, lookup, depth + 1)
  return value


def resolve_all(lookup):
  """Return a new lookup with all alias values resolved to concrete values."""
  resolved = {}
  for path, leaf in lookup.items():
    raw_val = leaf.get("value", "")
    resolved[path] = {
      **leaf,
      "value": resolve_alias(raw_val, lookup),
    }
  return resolved


def get_subtree_leaves(lookup, prefix):
  """Return ordered list of (path, leaf) where path starts with prefix."""
  return [(p, v) for p, v in lookup.items() if p == prefix or p.startswith(prefix + ".")]


# ---------------------------------------------------------------------------
# Section builders
# ---------------------------------------------------------------------------

def build_core_colors(resolved):
  """
  Format core color tokens.
  Output: "- Description: #hex — description field text"
  """
  prefix = "color.core"
  leaves = get_subtree_leaves(resolved, prefix)
  if not leaves:
    return None
  lines = []
  for path, leaf in leaves:
    hex_val = leaf["value"]
    description = leaf.get("description", path.split(".")[-1])
    lines.append(f"- {description}: {hex_val}")
  return "\n".join(lines)


def build_semantic_colors(resolved):
  """
  Format semantic color tokens.
  Output: "- Description (role note): #hex"
  """
  prefix = "color.semantic"
  leaves = get_subtree_leaves(resolved, prefix)
  if not leaves:
    return None
  lines = []
  for path, leaf in leaves:
    hex_val = leaf["value"]
    description = leaf.get("description", path.split(".")[-1])
    # Capitalise the token name as the label
    token_name = path.split(".")[-1]
    label = token_name_to_label(token_name)
    lines.append(f"- {label} ({description}): {hex_val}")
  return "\n".join(lines)


def token_name_to_label(name):
  """Convert kebab-case token name to Title Case label."""
  return " ".join(word.capitalize() for word in name.replace("-", " ").split())


def build_typography(resolved):
  """
  Format typography tokens.
  Returns multi-line string with font families and optional type scale.
  """
  lines = []
  font_primary = resolved.get("typography.font-primary")
  font_mono = resolved.get("typography.font-mono")
  if font_primary:
    desc = font_primary.get("description", "")
    lines.append(f"- Primary Font: {font_primary['value']}" + (f" ({desc})" if desc else ""))
  if font_mono:
    desc = font_mono.get("description", "")
    lines.append(f"- Monospace Font: {font_mono['value']}" + (f" ({desc})" if desc else ""))

  # Type scale — look for any leaf under typography.scale
  scale_leaves = get_subtree_leaves(resolved, "typography.scale")
  # Find base size for the "Base size" line
  base_leaf = resolved.get("typography.scale.base")
  if base_leaf:
    lines.append(f"- Base size: {base_leaf['value']}")

  if not lines:
    return None
  return "\n".join(lines)


def build_spacing(resolved):
  """Format spacing tokens as natural language bullets."""
  prefix = "spacing"
  leaves = get_subtree_leaves(resolved, prefix)
  if not leaves:
    return None
  lines = []
  for path, leaf in leaves:
    token_name = path.split(".")[-1]
    label = token_name_to_label(token_name)
    desc = leaf.get("description", "")
    val = leaf["value"]
    if desc:
      lines.append(f"- {label}: {val} ({desc})")
    else:
      lines.append(f"- {label}: {val}")
  return "\n".join(lines)


def build_radius(resolved):
  """Format border-radius tokens as natural language bullets."""
  prefix = "radius"
  leaves = get_subtree_leaves(resolved, prefix)
  if not leaves:
    return None
  lines = []
  for path, leaf in leaves:
    token_name = path.split(".")[-1]
    label = token_name_to_label(token_name)
    desc = leaf.get("description", "")
    val = leaf["value"]
    if desc:
      lines.append(f"- {label} ({desc}): {val}")
    else:
      lines.append(f"- {label}: {val}")
  return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main compiler
# ---------------------------------------------------------------------------

def compile_context(tokens_path, rules_path, output_path):
  tokens = load_tokens(tokens_path)
  lookup = build_lookup(tokens)
  resolved = resolve_all(lookup)

  total_tokens = len(resolved)

  # Build sections
  core_colors = build_core_colors(resolved)
  semantic_colors = build_semantic_colors(resolved)
  typography = build_typography(resolved)
  spacing = build_spacing(resolved)
  radius = build_radius(resolved)

  # Read design rules if exists
  rules_text = None
  if rules_path and Path(rules_path).exists():
    rules_text = Path(rules_path).read_text(encoding="utf-8").strip()

  # Compose output
  parts = ["## 6. Design System"]

  # --- Color Palette ---
  if core_colors or semantic_colors:
    parts.append("\n### Color Palette")
    parts.append("Use ONLY these colors. Do not use any Tailwind default colors.")
    if core_colors:
      parts.append("\n**Core Colors:**")
      parts.append(core_colors)
    if semantic_colors:
      parts.append("\n**Semantic Mapping:**")
      parts.append(semantic_colors)

  # --- Typography ---
  if typography:
    parts.append("\n### Typography")
    parts.append(typography)

  # --- Spacing & Layout ---
  if spacing:
    parts.append("\n### Spacing & Layout")
    parts.append(spacing)

  # --- Border Radius ---
  if radius:
    parts.append("\n### Border Radius")
    parts.append(radius)

  # --- Design Rules ---
  if rules_text:
    parts.append("\n### Design Rules")
    parts.append(rules_text)

  # --- Constraints ---
  parts.append("\n### Constraints")
  parts.append("- Use ONLY the colors listed above")
  parts.append("- Prefer semantic color names in Tailwind classes")
  parts.append("- All text must meet WCAG AA contrast requirements")
  parts.append("- Maintain consistent spacing using the base unit multiples")

  output = "\n".join(parts) + "\n"
  Path(output_path).write_text(output, encoding="utf-8")

  rules_note = f" + rules" if rules_text else ""
  print(f"Compiled {total_tokens} tokens{rules_note} to {output_path}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
  parser = argparse.ArgumentParser(
    description="Compile design-tokens.json + design-rules.md into .stitch-context.md"
  )
  parser.add_argument("tokens", help="Path to design-tokens.json")
  parser.add_argument(
    "--rules",
    default=None,
    help="Path to design-rules.md (default: design-rules.md in same dir as tokens)",
  )
  parser.add_argument(
    "--output",
    default=None,
    help="Output path (default: .stitch-context.md in same dir as tokens)",
  )
  args = parser.parse_args()

  tokens_path = Path(args.tokens).resolve()
  if not tokens_path.exists():
    print(f"Error: tokens file not found: {tokens_path}", file=sys.stderr)
    sys.exit(1)

  tokens_dir = tokens_path.parent

  rules_path = Path(args.rules).resolve() if args.rules else tokens_dir / "design-rules.md"
  output_path = Path(args.output).resolve() if args.output else tokens_dir / ".stitch-context.md"

  compile_context(tokens_path, rules_path, output_path)


if __name__ == "__main__":
  main()
