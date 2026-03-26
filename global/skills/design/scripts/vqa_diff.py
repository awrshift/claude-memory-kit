#!/usr/bin/env python3
"""
VQA Diff — Structured comparison between reference and generated site styles.

Usage:
  python3 vqa_diff.py --reference ref.json --generated gen.json --output diff.md

Input: two JSON files from vqa-extract-styles.js
Output: structured markdown comparison with severity ratings
"""

import json
import argparse
import sys
from pathlib import Path


COMPONENT_LABELS = {
    'nav': 'Navigation Bar',
    'navLink': 'Nav Link',
    'navCTA': 'Nav CTA Button',
    'subtitle': 'Hero Subtitle',
    'h1': 'Hero Headline',
    'heroCTA': 'Hero CTA Button',
    'mockup': 'Product Mockup',
    'announcement': 'Announcement Bar',
}

# Properties that matter most for visual parity
CRITICAL_PROPS = {
    'border.radius': 'Border Radius',
    'bg': 'Background',
    'color': 'Text Color',
    'depth.boxShadow': 'Box Shadow',
    'depth.backdropFilter': 'Backdrop Filter',
    'font.family': 'Font Family',
    'font.weight': 'Font Weight',
    'font.size': 'Font Size',
    'font.textTransform': 'Text Transform',
    'font.letterSpacing': 'Letter Spacing',
    'spacing.height': 'Height',
    'spacing.padding': 'Padding',
}


def get_nested(obj, path):
    """Get nested dict value by dot path."""
    parts = path.split('.')
    current = obj
    for part in parts:
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            return None
    return current


def normalize_value(val):
    """Normalize CSS values for comparison."""
    if val is None:
        return 'none'
    val = str(val).strip()
    if val in ('', 'none', 'normal', '0px', '0', 'rgba(0, 0, 0, 0)', 'transparent'):
        return 'none'
    return val


def severity(prop_path, ref_val, gen_val):
    """Rate difference severity: critical / moderate / minor."""
    ref = normalize_value(ref_val)
    gen = normalize_value(gen_val)

    if ref == gen:
        return 'match'

    # Critical: shape-defining properties
    if prop_path in ('border.radius', 'depth.boxShadow', 'bg'):
        return 'critical'

    # Critical: font weight/transform differences
    if prop_path in ('font.weight', 'font.textTransform'):
        return 'critical'

    # Moderate: sizing and spacing
    if prop_path in ('font.size', 'spacing.height', 'spacing.padding', 'font.letterSpacing'):
        return 'moderate'

    # Minor: everything else
    return 'minor'


def compare_component(name, ref_data, gen_data):
    """Compare a single component between reference and generated."""
    if not ref_data and not gen_data:
        return None

    diffs = []
    for prop_path, prop_label in CRITICAL_PROPS.items():
        ref_val = get_nested(ref_data, prop_path) if ref_data else None
        gen_val = get_nested(gen_data, prop_path) if gen_data else None

        sev = severity(prop_path, ref_val, gen_val)
        if sev != 'match':
            diffs.append({
                'property': prop_label,
                'prop_path': prop_path,
                'reference': normalize_value(ref_val),
                'generated': normalize_value(gen_val),
                'severity': sev
            })

    return {
        'component': COMPONENT_LABELS.get(name, name),
        'diffs': sorted(diffs, key=lambda d: {'critical': 0, 'moderate': 1, 'minor': 2}[d['severity']]),
        'match_count': len(CRITICAL_PROPS) - len(diffs),
        'total_props': len(CRITICAL_PROPS),
    }


def compare_body(ref, gen):
    """Compare body-level styles."""
    diffs = []
    for key in ('fontFamily', 'fontSize', 'color', 'backgroundColor'):
        rv = normalize_value(ref.get('body', {}).get(key))
        gv = normalize_value(gen.get('body', {}).get(key))
        if rv != gv:
            diffs.append({
                'property': key,
                'reference': rv,
                'generated': gv,
                'severity': 'moderate'
            })
    return diffs


def format_markdown(ref, gen, results, body_diffs):
    """Format comparison results as markdown."""
    lines = []
    lines.append('# VQA Comparison Report')
    lines.append('')
    lines.append(f'**Reference:** {ref.get("url", "unknown")}')
    lines.append(f'**Generated:** {gen.get("url", "unknown")}')
    lines.append(f'**Viewport:** {ref.get("viewport", {}).get("w", "?")}x{ref.get("viewport", {}).get("h", "?")}')
    lines.append('')

    # Summary
    total_critical = sum(len([d for d in r['diffs'] if d['severity'] == 'critical']) for r in results if r)
    total_moderate = sum(len([d for d in r['diffs'] if d['severity'] == 'moderate']) for r in results if r)
    total_minor = sum(len([d for d in r['diffs'] if d['severity'] == 'minor']) for r in results if r)
    total_match = sum(r['match_count'] for r in results if r)
    total_props = sum(r['total_props'] for r in results if r)

    lines.append('## Summary')
    lines.append('')
    lines.append(f'| Metric | Count |')
    lines.append(f'|--------|-------|')
    lines.append(f'| Matching properties | {total_match}/{total_props} |')
    lines.append(f'| Critical differences | {total_critical} |')
    lines.append(f'| Moderate differences | {total_moderate} |')
    lines.append(f'| Minor differences | {total_minor} |')
    lines.append(f'| **Visual parity score** | **{round(total_match/max(total_props,1)*100)}%** |')
    lines.append('')

    # Body-level
    if body_diffs:
        lines.append('## Body / Global Styles')
        lines.append('')
        lines.append('| Property | Reference | Generated | Severity |')
        lines.append('|----------|-----------|-----------|----------|')
        for d in body_diffs:
            lines.append(f'| {d["property"]} | `{d["reference"]}` | `{d["generated"]}` | {d["severity"]} |')
        lines.append('')

    # Per-component
    lines.append('## Component Differences')
    lines.append('')

    for result in results:
        if not result or not result['diffs']:
            continue

        lines.append(f'### {result["component"]} ({result["match_count"]}/{result["total_props"]} match)')
        lines.append('')
        lines.append('| Property | Reference | Generated | Severity |')
        lines.append('|----------|-----------|-----------|----------|')
        for d in result['diffs']:
            sev_icon = {'critical': 'CRITICAL', 'moderate': 'MODERATE', 'minor': 'minor'}[d['severity']]
            lines.append(f'| {d["property"]} | `{d["reference"]}` | `{d["generated"]}` | {sev_icon} |')
        lines.append('')

    # CSS patch hints
    lines.append('## Suggested Token Updates')
    lines.append('')
    lines.append('Based on critical differences, update these design tokens:')
    lines.append('')
    lines.append('```json')
    suggestions = {}
    for result in results:
        if not result:
            continue
        for d in result['diffs']:
            if d['severity'] == 'critical':
                key = f"{result['component']}.{d['prop_path']}"
                suggestions[key] = {
                    'current': d['generated'],
                    'target': d['reference'],
                    'property': d['property']
                }
    lines.append(json.dumps(suggestions, indent=2))
    lines.append('```')
    lines.append('')

    # Gemini prompt template
    lines.append('## Gemini CSS Patch Prompt')
    lines.append('')
    lines.append('Use this prompt with `gemini second-opinion` to get CSS patches:')
    lines.append('')
    lines.append('```')
    lines.append('Based on this VQA comparison between a reference site and our generated site,')
    lines.append('provide SPECIFIC CSS overrides to close the visual gap.')
    lines.append('Focus on CRITICAL differences first.')
    lines.append('Output as a CSS patch file with exact selectors and values.')
    lines.append('Include design token update suggestions.')
    lines.append('```')

    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description='VQA Diff — compare reference vs generated styles')
    parser.add_argument('--reference', '-r', required=True, help='Reference site styles JSON')
    parser.add_argument('--generated', '-g', required=True, help='Generated site styles JSON')
    parser.add_argument('--output', '-o', default=None, help='Output markdown file (default: stdout)')
    args = parser.parse_args()

    with open(args.reference) as f:
        ref = json.load(f)
    with open(args.generated) as f:
        gen = json.load(f)

    # Compare each component
    components = ['nav', 'navLink', 'navCTA', 'subtitle', 'h1', 'heroCTA', 'mockup', 'announcement']
    results = []
    for comp in components:
        result = compare_component(comp, ref.get(comp), gen.get(comp))
        results.append(result)

    body_diffs = compare_body(ref, gen)
    markdown = format_markdown(ref, gen, results, body_diffs)

    if args.output:
        Path(args.output).write_text(markdown)
        print(f'VQA report written to {args.output}')
        # Print summary to stderr
        total_critical = sum(len([d for d in r['diffs'] if d['severity'] == 'critical']) for r in results if r)
        total_match = sum(r['match_count'] for r in results if r)
        total_props = sum(r['total_props'] for r in results if r)
        score = round(total_match / max(total_props, 1) * 100)
        print(f'Score: {score}% | Critical: {total_critical}', file=sys.stderr)
    else:
        print(markdown)


if __name__ == '__main__':
    main()
