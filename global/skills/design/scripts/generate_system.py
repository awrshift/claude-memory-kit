#!/usr/bin/env python3
"""Generate a complete design system by merging computed palette with scaffold.

Deterministic Python hydration: Claude outputs a small config JSON,
this script merges it with compute_palette output and universal-scaffold
to produce design-tokens.json. No LLM writes the final JSON.

Usage:
  python3 generate_system.py --palette palette.json --config config.json --output ./
  python3 generate_system.py --palette palette.json --config config.json --output ./ --css

Config JSON (written by Claude, ~15 lines):
  {
    "name": "My Project",
    "description": "Dark fintech dashboard...",
    "aesthetic": "minimal",
    "project_type": "dashboard",
    "font_ui": "Inter",
    "font_data": "JetBrains Mono",
    "extra_rules": {
      "D-1": "Primary color only for CTA buttons..."
    }
  }

Dependencies: Python stdlib only.
"""

import json
import os
import re
import sys
from argparse import ArgumentParser
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
SCAFFOLD_PATH = SKILL_DIR / "resources" / "universal-scaffold.json"


def load_json(path):
  with open(path, "r", encoding="utf-8") as f:
    return json.load(f)


def hydrate_scaffold(scaffold, palette, config):
  """Replace all {{placeholder}} slots in scaffold with computed values.

  Placeholder format: {{section.key}} maps to palette[section][key].
  Config values override $meta fields.
  """
  text = json.dumps(scaffold, indent=2, ensure_ascii=False)

  # Build replacement map from palette
  replacements = {}

  # Flat palette sections
  for section in ["surfaces", "text", "borders", "state_layers", "skeleton", "spacing"]:
    if section in palette:
      for key, val in palette[section].items():
        replacements[f"{section}.{key}"] = str(val)

  # Color scales
  for prefix in ["primary", "neutral"]:
    scale_key = f"{prefix}_scale"
    if scale_key in palette:
      for step, val in palette[scale_key].items():
        replacements[f"{prefix}.{step}"] = val

  # Semantic colors
  if "semantic" in palette:
    for key, val in palette["semantic"].items():
      replacements[f"semantic.{key}"] = val

  # Overlay
  if "overlay" in palette:
    replacements["overlay"] = palette["overlay"]

  # Typography from palette
  if "typography" in palette:
    for key, val in palette["typography"].items():
      replacements[f"typography.{key}"] = str(val)

  # Config overrides for meta
  meta_map = {
    "name": "meta.name",
    "description": "meta.description",
    "aesthetic": "meta.aesthetic",
    "primary_hex": "meta.primary_hex",
  }
  if "meta" in palette:
    replacements["meta.theme"] = palette["meta"].get("theme", "dark")
    replacements["meta.density"] = palette["meta"].get("density", "comfortable")
    replacements["meta.primary_hex"] = palette["meta"].get("primary_hex", "")

  for config_key, placeholder_key in meta_map.items():
    if config_key in config:
      replacements[placeholder_key] = config[config_key]

  # Font overrides from config
  if "font_ui" in config:
    replacements["typography.font-ui"] = config["font_ui"]
  if "font_data" in config:
    replacements["typography.font-data"] = config["font_data"]

  # Replace all {{key}} patterns
  def replace_match(m):
    key = m.group(1)
    return replacements.get(key, m.group(0))

  text = re.sub(r"\{\{([^}]+)\}\}", replace_match, text)

  result = json.loads(text)

  # Add chart colors to color section
  if "chart" in palette:
    chart_section = {
      "$description": "Categorical chart palette. Series 1 = primary brand color.",
    }
    for key, val in palette["chart"].items():
      chart_section[key] = {"value": val, "description": f"Chart {key}"}
    result["color"]["chart"] = chart_section

  # Add extra rules from config
  if "extra_rules" in config:
    if "rules" not in result:
      result["rules"] = {}
    for rule_id, rule_text in config["extra_rules"].items():
      result["rules"][rule_id] = rule_text

  # Update typography scale sizes based on density
  if "typography" in palette:
    typo = palette["typography"]
    base_px = int(typo.get("base", "14px").replace("px", ""))
    ratio = float(typo.get("scale-ratio", 1.2))
    _adjust_type_scale(result, base_px, ratio)

  return result


def _adjust_type_scale(tokens, base_px, ratio):
  """Adjust typography scale based on density-driven base size and ratio.

  Recalculates: body=base, section-title=base*ratio^2, page-header=base*ratio^3,
  caption=base/ratio, etc.
  """
  scale = tokens.get("typography", {}).get("scale", {})
  ui = scale.get("ui", {})

  size_map = {
    "page-header":   round(base_px * ratio * ratio * ratio),
    "section-title": round(base_px * ratio * ratio),
    "nav-item":      round(base_px * ratio),
    "body":          base_px,
    "card-label":    max(round(base_px - 1), 11),
    "button":        base_px,
    "caption":       max(round(base_px / ratio), 11),
    "tooltip":       max(round(base_px / ratio), 11),
  }

  for key, size in size_map.items():
    if key in ui and isinstance(ui[key], dict):
      ui[key]["value"] = f"{size}px"


def write_tokens(tokens, output_dir):
  path = output_dir / "design-tokens.json"
  with open(path, "w", encoding="utf-8") as f:
    json.dump(tokens, f, indent=2, ensure_ascii=False)
    f.write("\n")
  return path


def count_tokens(data, prefix=""):
  """Count leaf tokens (nodes with 'value' key)."""
  count = 0
  for key, node in data.items():
    if key.startswith("$"):
      continue
    if isinstance(node, dict):
      if "value" in node:
        count += 1
      else:
        count += count_tokens(node, f"{prefix}.{key}")
  return count


def main():
  parser = ArgumentParser(
    description="Generate design-tokens.json from palette + scaffold + config"
  )
  parser.add_argument(
    "--palette", required=True,
    help="Path to compute_palette.py output JSON"
  )
  parser.add_argument(
    "--config", required=True,
    help="Path to project config JSON (from Claude)"
  )
  parser.add_argument(
    "--output", default=".",
    help="Output directory for design-tokens.json (default: current)"
  )
  parser.add_argument(
    "--css", action="store_true",
    help="Also generate CSS variables via build_system.py"
  )
  args = parser.parse_args()

  # Load inputs
  palette = load_json(args.palette)
  config = load_json(args.config)

  if not SCAFFOLD_PATH.is_file():
    print(f"Error: scaffold not found at {SCAFFOLD_PATH}", file=sys.stderr)
    sys.exit(2)
  scaffold = load_json(SCAFFOLD_PATH)

  # Generate
  output_dir = Path(os.path.abspath(args.output))
  if not output_dir.is_dir():
    print(f"Error: output directory not found: {output_dir}", file=sys.stderr)
    sys.exit(2)

  tokens = hydrate_scaffold(scaffold, palette, config)
  tokens_path = write_tokens(tokens, output_dir)

  total = count_tokens(tokens)
  print(f"Generated design-tokens.json: {total} tokens → {tokens_path}")

  # Optional CSS generation
  if args.css:
    build_script = Path(__file__).parent / "build_system.py"
    css_path = output_dir / "design-tokens.css"
    import subprocess
    result = subprocess.run(
      [sys.executable, str(build_script), str(tokens_path), "--css", str(css_path)],
      capture_output=True, text=True
    )
    print(result.stdout)
    if result.returncode != 0:
      print(result.stderr, file=sys.stderr)
      sys.exit(result.returncode)


if __name__ == "__main__":
  main()
