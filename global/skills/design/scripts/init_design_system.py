#!/usr/bin/env python3
"""Bootstrap a design system for a project.

Reads a starter template from the design skill resources, updates $meta.name,
writes design-tokens.json and a design-rules.md scaffold to the output directory.

Usage:
  python3 init_design_system.py --template saas-dark --name "My Project" --output-dir /path/to/project
  python3 init_design_system.py --template marketing-light --name "Acme Landing" --output-dir .
  python3 init_design_system.py --template editorial-mono --name "The Journal"
"""

import json
import os
import sys
from argparse import ArgumentParser
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = SKILL_DIR / "resources" / "starter-templates"

VALID_TEMPLATES = ["saas-dark", "marketing-light", "editorial-mono"]

DESIGN_RULES_SCAFFOLD = """\
# Design Rules — {name}

## Aesthetic Direction
[Describe the visual mood, tone, and aesthetic of the project]

## Component Behavior
[Describe how interactive elements should look and behave]

## Typography Rules
[Describe font usage, heading hierarchy, text styling preferences]

## Spacing Philosophy
[Describe spacing approach — generous vs dense, grid rules]

## Do's
[List positive design guidelines]

## Don'ts
[List things to avoid in the design]
"""


def load_template(template_name):
  template_path = TEMPLATES_DIR / f"{template_name}.json"
  if not template_path.is_file():
    print(
      f"Error: template '{template_name}' not found at {template_path}",
      file=sys.stderr,
    )
    print(f"Available templates: {', '.join(VALID_TEMPLATES)}", file=sys.stderr)
    sys.exit(1)
  with open(template_path, "r", encoding="utf-8") as f:
    return json.load(f)


def write_tokens(tokens, output_dir):
  tokens_path = output_dir / "design-tokens.json"
  with open(tokens_path, "w", encoding="utf-8") as f:
    json.dump(tokens, f, indent=2, ensure_ascii=False)
    f.write("\n")
  return tokens_path


def write_rules_scaffold(project_name, output_dir):
  rules_path = output_dir / "design-rules.md"
  content = DESIGN_RULES_SCAFFOLD.format(name=project_name)
  with open(rules_path, "w", encoding="utf-8") as f:
    f.write(content)
  return rules_path


def print_summary(project_name, template_name, tokens_path, rules_path, tokens):
  meta = tokens.get("$meta", {})
  theme = meta.get("theme", "unknown")
  description = meta.get("description", "")
  sections = [k for k in tokens if not k.startswith("$")]

  print()
  print(f"Design system initialized: {project_name}")
  print(f"  Template : {template_name} ({theme} theme)")
  if description:
    print(f"  Desc     : {description}")
  print(f"  Sections : {', '.join(sections)}")
  print()
  print("Files written:")
  print(f"  {tokens_path}")
  print(f"  {rules_path}")
  print()
  print("Next steps:")
  print("  1. Edit design-rules.md — fill in aesthetic direction and guidelines")
  print("  2. Adjust token values in design-tokens.json to match your brand")
  print("  3. Run /design sync to generate CSS variables and Tailwind config")
  print("  4. Generate screens: use /design generate with frontend-design plugin and your tokens")
  print()


def main():
  parser = ArgumentParser(
    description="Bootstrap a design system from a starter template"
  )
  parser.add_argument(
    "--template",
    required=True,
    choices=VALID_TEMPLATES,
    metavar="TEMPLATE",
    help=f"Starter template to use. Choices: {', '.join(VALID_TEMPLATES)}",
  )
  parser.add_argument(
    "--name",
    required=True,
    help="Project name to set in $meta.name (e.g. 'Acme SaaS')",
  )
  parser.add_argument(
    "--output-dir",
    default=".",
    help="Directory where design-tokens.json and design-rules.md will be written (default: current directory)",
  )
  args = parser.parse_args()

  output_dir = Path(os.path.abspath(args.output_dir))
  if not output_dir.exists():
    print(f"Error: output directory does not exist: {output_dir}", file=sys.stderr)
    sys.exit(1)
  if not output_dir.is_dir():
    print(f"Error: output path is not a directory: {output_dir}", file=sys.stderr)
    sys.exit(1)

  tokens = load_template(args.template)

  if "$meta" not in tokens:
    tokens["$meta"] = {}
  tokens["$meta"]["name"] = args.name

  tokens_path = write_tokens(tokens, output_dir)
  rules_path = write_rules_scaffold(args.name, output_dir)

  print_summary(args.name, args.template, tokens_path, rules_path, tokens)


if __name__ == "__main__":
  main()
