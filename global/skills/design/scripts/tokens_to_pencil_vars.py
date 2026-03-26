#!/usr/bin/env python3
"""Convert design-tokens.json to Pencil MCP variables format.

Usage:
  python3 tokens_to_pencil_vars.py <tokens_path> [--json] [--dry-run]

Output: JSON dict ready for Pencil set_variables call.

Maps:
  color.semantic.*  → color variables  (resolve aliases to hex)
  color.chart.*     → color variables  (chart-series-N)
  spacing.*         → number variables (strip px)
  radius.*          → number variables (strip px)
  typography.font-* → string variables (font names)

Known limitations:
  - fontFamily does NOT support $variable refs in Pencil. Use literal strings.
  - Font variables are included for reference but must be used as literals in batch_design.
  - No "dimension" type — px values stored as numbers.
"""

import json
import sys
import re


def resolve_alias(value, tokens):
    """Resolve {path.to.token} aliases to actual values."""
    if not isinstance(value, str) or not value.startswith("{"):
        return value

    seen = set()
    while isinstance(value, str) and value.startswith("{") and value.endswith("}"):
        path = value[1:-1]
        if path in seen:
            raise ValueError(f"Circular alias: {path}")
        seen.add(path)

        parts = path.split(".")
        node = tokens
        for part in parts:
            if isinstance(node, dict) and part in node:
                node = node[part]
            else:
                raise ValueError(f"Unresolved alias: {path}")

        if isinstance(node, dict) and "value" in node:
            value = node["value"]
        elif isinstance(node, str):
            value = node
        else:
            raise ValueError(f"Alias target is not a value: {path}")

    return value


def px_to_number(value):
    """Convert '24px' to 24, '4px' to 4."""
    if isinstance(value, str):
        m = re.match(r'^(\d+(?:\.\d+)?)px$', value)
        if m:
            n = float(m.group(1))
            return int(n) if n == int(n) else n
    return value


def tokens_to_pencil_vars(tokens_path):
    """Convert design-tokens.json to Pencil variables dict."""
    with open(tokens_path) as f:
        tokens = json.load(f)

    variables = {}

    # 1. Semantic colors → Pencil color vars
    semantic = tokens.get("color", {}).get("semantic", {})
    for name, token in semantic.items():
        if name.startswith("$"):
            continue
        raw = token.get("value", "") if isinstance(token, dict) else token
        hex_val = resolve_alias(raw, tokens)
        variables[name] = {"type": "color", "value": hex_val}

    # 2. Chart colors → chart-series-N
    chart = tokens.get("color", {}).get("chart", {})
    for name, token in chart.items():
        if name.startswith("$"):
            continue
        raw = token.get("value", "") if isinstance(token, dict) else token
        hex_val = resolve_alias(raw, tokens)
        variables[f"chart-{name}"] = {"type": "color", "value": hex_val}

    # 3. Spacing → number vars (strip px)
    spacing = tokens.get("spacing", {})
    for name, token in spacing.items():
        if name.startswith("$"):
            continue
        raw = token.get("value", "") if isinstance(token, dict) else token
        num = px_to_number(resolve_alias(raw, tokens))
        if isinstance(num, (int, float)):
            variables[f"spacing-{name}"] = {"type": "number", "value": num}

    # 4. Radius → number vars (strip px)
    radius = tokens.get("radius", {})
    for name, token in radius.items():
        if name.startswith("$"):
            continue
        raw = token.get("value", "") if isinstance(token, dict) else token
        num = px_to_number(resolve_alias(raw, tokens))
        if isinstance(num, (int, float)):
            variables[f"radius-{name}"] = {"type": "number", "value": num}

    # 5. Typography fonts → string vars
    typo = tokens.get("typography", {})
    for name, token in typo.items():
        if name.startswith("$") or not name.startswith("font-"):
            continue
        if isinstance(token, dict) and "value" in token:
            variables[name] = {"type": "string", "value": token["value"]}

    return variables


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 tokens_to_pencil_vars.py <tokens_path> [--json] [--dry-run]")
        sys.exit(1)

    tokens_path = sys.argv[1]
    as_json = "--json" in sys.argv
    dry_run = "--dry-run" in sys.argv

    variables = tokens_to_pencil_vars(tokens_path)

    # Stats
    colors = sum(1 for v in variables.values() if v["type"] == "color")
    numbers = sum(1 for v in variables.values() if v["type"] == "number")
    strings = sum(1 for v in variables.values() if v["type"] == "string")

    if as_json or dry_run:
        print(json.dumps(variables, indent=2))

    print(f"\n--- Stats ---", file=sys.stderr)
    print(f"Total: {len(variables)} variables", file=sys.stderr)
    print(f"  Colors:  {colors}", file=sys.stderr)
    print(f"  Numbers: {numbers}", file=sys.stderr)
    print(f"  Strings: {strings}", file=sys.stderr)

    if dry_run:
        print("\n[DRY RUN] No Pencil call made.", file=sys.stderr)
    else:
        print("\nReady for set_variables call.", file=sys.stderr)

    return variables


if __name__ == "__main__":
    main()
