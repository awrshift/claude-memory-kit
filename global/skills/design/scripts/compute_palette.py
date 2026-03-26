#!/usr/bin/env python3
"""Compute a complete design palette from a single hex color.

Seed-to-System color engine: takes one hex color and produces an entire
design system color palette using OKLCH color math (perceptually uniform).

Usage:
  python3 compute_palette.py --hex "#2563EB" --theme dark --density compact
  python3 compute_palette.py --hex "#F472B6" --theme light

Output: JSON to stdout with color scales, semantic mappings, surfaces,
state layers, borders, text hierarchy, spacing, and contrast report.

Dependencies: Python stdlib only (math module for OKLCH matrices).
"""

import argparse
import json
import math
import sys


# ---------------------------------------------------------------------------
# OKLCH Color Math — Bottosson algorithm
# Reference: https://bottosson.github.io/posts/oklab/
# ---------------------------------------------------------------------------

def _srgb_to_linear(c):
  """sRGB component (0-1) to linear RGB."""
  if c <= 0.04045:
    return c / 12.92
  return ((c + 0.055) / 1.055) ** 2.4


def _linear_to_srgb(c):
  """Linear RGB component to sRGB (0-1)."""
  if c <= 0.0031308:
    return c * 12.92
  return 1.055 * (c ** (1 / 2.4)) - 0.055


def _cbrt(x):
  """Cube root that handles negative values."""
  if x >= 0:
    return x ** (1 / 3)
  return -((-x) ** (1 / 3))


def hex_to_rgb(hex_str):
  """#RRGGBB to (r, g, b) floats 0-1."""
  h = hex_str.lstrip("#")
  return (int(h[0:2], 16) / 255, int(h[2:4], 16) / 255, int(h[4:6], 16) / 255)


def rgb_to_hex(r, g, b):
  """(r, g, b) floats 0-1 to #RRGGBB. Clamps to gamut."""
  r = max(0.0, min(1.0, r))
  g = max(0.0, min(1.0, g))
  b = max(0.0, min(1.0, b))
  return "#{:02X}{:02X}{:02X}".format(
    round(r * 255), round(g * 255), round(b * 255)
  )


def srgb_to_oklab(r, g, b):
  """sRGB (0-1) to OKLab (L, a, b)."""
  r_lin = _srgb_to_linear(r)
  g_lin = _srgb_to_linear(g)
  b_lin = _srgb_to_linear(b)

  # M1: sRGB linear → LMS (exact inverse of M1_inv in oklab_to_srgb)
  l = 0.4122214708 * r_lin + 0.5363325363 * g_lin + 0.0514459929 * b_lin
  m = 0.2119034983 * r_lin + 0.6806995451 * g_lin + 0.1073969566 * b_lin
  s = 0.0883024619 * r_lin + 0.2817188376 * g_lin + 0.6299787005 * b_lin

  l_ = _cbrt(l)
  m_ = _cbrt(m)
  s_ = _cbrt(s)

  L = 0.2104542553 * l_ + 0.7936177850 * m_ - 0.0040720468 * s_
  a = 1.9779984951 * l_ - 2.4285922050 * m_ + 0.4505937099 * s_
  b_val = 0.0259040371 * l_ + 0.7827717662 * m_ - 0.8086757660 * s_

  return (L, a, b_val)


def oklab_to_srgb(L, a, b):
  """OKLab to sRGB (0-1). May return out-of-gamut values."""
  l_ = L + 0.3963377774 * a + 0.2158037573 * b
  m_ = L - 0.1055613458 * a - 0.0638541728 * b
  s_ = L - 0.0894841775 * a - 1.2914855480 * b

  l = l_ ** 3
  m = m_ ** 3
  s = s_ ** 3

  r_lin = +4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s
  g_lin = -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s
  b_lin = -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s

  return (_linear_to_srgb(r_lin), _linear_to_srgb(g_lin), _linear_to_srgb(b_lin))


def oklab_to_oklch(L, a, b):
  """OKLab to OKLCH (L, C, H degrees)."""
  C = math.sqrt(a * a + b * b)
  H = math.degrees(math.atan2(b, a)) % 360
  return (L, C, H)


def oklch_to_oklab(L, C, H):
  """OKLCH to OKLab."""
  H_rad = math.radians(H)
  a = C * math.cos(H_rad)
  b = C * math.sin(H_rad)
  return (L, a, b)


def hex_to_oklch(hex_str):
  """Hex to OKLCH (L, C, H)."""
  r, g, b = hex_to_rgb(hex_str)
  L, a, b_val = srgb_to_oklab(r, g, b)
  return oklab_to_oklch(L, a, b_val)


def _is_in_gamut(L, C, H):
  """Check if OKLCH color is within sRGB gamut."""
  lab_L, lab_a, lab_b = oklch_to_oklab(L, C, H)
  r, g, b = oklab_to_srgb(lab_L, lab_a, lab_b)
  return all(-0.002 <= v <= 1.002 for v in (r, g, b))


def oklch_to_hex(L, C, H):
  """OKLCH to hex with gamut mapping via binary search on chroma.

  CSS Color Level 4 approach: bisect chroma until in sRGB gamut.
  Converges in ~12 iterations vs 32 for linear reduction.
  """
  if _is_in_gamut(L, C, H):
    lab_L, lab_a, lab_b = oklch_to_oklab(L, C, H)
    r, g, b = oklab_to_srgb(lab_L, lab_a, lab_b)
    return rgb_to_hex(r, g, b)

  lo, hi = 0.0, C
  for _ in range(16):
    mid = (lo + hi) / 2
    if _is_in_gamut(L, mid, H):
      lo = mid
    else:
      hi = mid
  lab_L, lab_a, lab_b = oklch_to_oklab(L, lo, H)
  r, g, b = oklab_to_srgb(lab_L, lab_a, lab_b)
  return rgb_to_hex(r, g, b)


# ---------------------------------------------------------------------------
# WCAG Contrast
# ---------------------------------------------------------------------------

def _relative_luminance(hex_str):
  """WCAG 2.0 relative luminance from hex color."""
  r, g, b = hex_to_rgb(hex_str)
  def lin(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
  return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b)


def contrast_ratio(hex1, hex2):
  """WCAG contrast ratio between two hex colors."""
  l1 = _relative_luminance(hex1)
  l2 = _relative_luminance(hex2)
  lighter = max(l1, l2)
  darker = min(l1, l2)
  return (lighter + 0.05) / (darker + 0.05)


# ---------------------------------------------------------------------------
# Scale Generation
# ---------------------------------------------------------------------------

# 11-step scale (Tailwind naming, Radix Step 9 anchor logic)
SCALE_STEPS = [50, 100, 200, 300, 400, 500, 600, 700, 800, 900, 950]

# Chroma multiplier per step: peaks at 500 (= Radix Step 9, brand anchor).
# Reduces toward both ends to prevent oversaturated pastels and muddy darks.
SCALE_CHROMA = {
  50:  0.20,
  100: 0.35,
  200: 0.55,
  300: 0.80,
  400: 0.95,
  500: 1.00,
  600: 0.95,
  700: 0.85,
  800: 0.70,
  900: 0.55,
  950: 0.40,
}

# Interpolation fractions: how far each step is from anchor (500) toward
# the light end (0.97) or dark end (0.14). 1.0 = at the endpoint.
_LIGHT_FRACS = {50: 1.0, 100: 0.85, 200: 0.65, 300: 0.45, 400: 0.20}
_DARK_FRACS = {600: 0.20, 700: 0.40, 800: 0.60, 900: 0.80, 950: 0.95}
_L_LIGHT_END = 0.97
_L_DARK_END = 0.14
# Anchor L clamped to this range so very dark/light inputs still produce
# a usable scale (extremes compress one side too much).
_ANCHOR_L_MIN = 0.35
_ANCHOR_L_MAX = 0.85


def _build_lightness_targets(anchor_L):
  """Build per-step L targets relative to anchor at step 500.

  Steps above 500 interpolate from anchor toward _L_LIGHT_END (0.97).
  Steps below 500 interpolate from anchor toward _L_DARK_END (0.14).
  This preserves the input color's natural lightness instead of forcing
  a fixed L=0.55 that makes golds/ambers muddy.
  """
  targets = {500: anchor_L}
  for step, frac in _LIGHT_FRACS.items():
    targets[step] = anchor_L + frac * (_L_LIGHT_END - anchor_L)
  for step, frac in _DARK_FRACS.items():
    targets[step] = anchor_L - frac * (anchor_L - _L_DARK_END)
  return targets


def generate_scale(base_hex, hue_override=None):
  """Generate 11-step color scale using Radix Step 9 anchor logic.

  Step 500 = brand anchor at the input color's natural L and C.
  Other steps are derived relative to anchor — lighter above, darker below.
  Returns dict like {"50": "#...", "100": "#...", ...}.
  """
  base_L, base_C, base_H = hex_to_oklch(base_hex)
  H = hue_override if hue_override is not None else base_H

  if hue_override is not None:
    # Semantic overrides: no natural anchor, use moderate defaults
    anchor_L = 0.55
    peak_C = 0.15
  else:
    # Brand color: anchor at natural L (clamped), natural C (capped)
    anchor_L = max(_ANCHOR_L_MIN, min(_ANCHOR_L_MAX, base_L))
    peak_C = max(min(base_C, 0.25), 0.08)

  L_targets = _build_lightness_targets(anchor_L)

  scale = {}
  for step in SCALE_STEPS:
    L = L_targets[step]
    C = peak_C * SCALE_CHROMA[step]
    scale[str(step)] = oklch_to_hex(L, C, H)

  return scale


def _neutral_hue(primary_hue):
  """Determine neutral hue from primary, with yellow/green shift.

  Yellow (60-110°) and lime-green hues produce sickly-looking neutrals.
  Shift these toward warm brown (40°) or cool blue-grey (250°).
  """
  if 55 <= primary_hue <= 120:
    # Yellow/lime zone (OKLCH: gold≈110°, lime≈120°) → warm brown
    return 40.0
  return primary_hue


def generate_neutral_scale(primary_hue):
  """Generate neutral scale with subtle hue tint from primary.

  Neutral chroma is very low (0.01-0.015) — just enough to feel
  warm or cool, not enough to look colored.
  Uses fixed L targets (no brand anchor — neutrals span full range).
  """
  NEUTRAL_CHROMA = 0.012
  NEUTRAL_L = {
    50: 0.97, 100: 0.93, 200: 0.87, 300: 0.77, 400: 0.66,
    500: 0.55, 600: 0.45, 700: 0.37, 800: 0.29, 900: 0.21, 950: 0.14,
  }
  hue = _neutral_hue(primary_hue)

  scale = {}
  for step in SCALE_STEPS:
    L = NEUTRAL_L[step]
    c = NEUTRAL_CHROMA * SCALE_CHROMA[step]
    scale[str(step)] = oklch_to_hex(L, c, hue)

  return scale


# ---------------------------------------------------------------------------
# Semantic Colors — fixed hues, adapted to primary
# ---------------------------------------------------------------------------

# Semantic hue config: default hue + fallback when it collides with primary.
# Fallback hues are chosen to stay recognizable (orange for warning, not green).
SEMANTIC_HUES = {
  "success": {"hue": 145.0, "fallback": 160.0},  # green → teal-green
  "warning": {"hue": 85.0,  "fallback": 55.0},    # amber → orange
  "error":   {"hue": 25.0,  "fallback": 355.0},   # red → red-pink
  "info":    {"hue": 230.0, "fallback": 260.0},    # blue → indigo
}

HUE_COLLISION_THRESHOLD = 25.0


def _hue_distance(h1, h2):
  """Shortest angular distance between two hues (0-180)."""
  d = abs(h1 - h2) % 360
  return min(d, 360 - d)


def _resolve_semantic_hues(primary_hue):
  """Resolve semantic hues with collision avoidance.

  If primary hue is too close to a semantic hue, use that color's
  pre-defined fallback hue (chosen to stay visually recognizable).
  """
  resolved = {}
  for name, config in SEMANTIC_HUES.items():
    default_hue = config["hue"]
    if _hue_distance(primary_hue, default_hue) < HUE_COLLISION_THRESHOLD:
      resolved[name] = config["fallback"]
    else:
      resolved[name] = default_hue
  return resolved


def generate_semantic_colors(primary_hue, theme):
  """Generate semantic status colors with collision avoidance.

  Dark theme: lighter base (L~0.70), light theme: darker base (L~0.50).
  """
  base_L = 0.70 if theme == "dark" else 0.50
  base_C = 0.15
  hues = _resolve_semantic_hues(primary_hue)

  colors = {}
  for name, hue in hues.items():
    colors[name] = oklch_to_hex(base_L, base_C, hue)
  return colors


# ---------------------------------------------------------------------------
# Surfaces, Text, Borders — derived from neutral scale + theme
# ---------------------------------------------------------------------------

def generate_surfaces(neutral_scale, theme):
  """4-level surface system (Carbon-inspired for dark, standard for light)."""
  if theme == "dark":
    return {
      "background":   neutral_scale["950"],
      "surface":      neutral_scale["900"],
      "surface-hover": neutral_scale["800"],
      "tooltip-bg":   neutral_scale["700"],
    }
  else:
    return {
      "background":   neutral_scale["50"],
      "surface":      "#FFFFFF",
      "surface-hover": neutral_scale["100"],
      "tooltip-bg":   neutral_scale["200"],
    }


def generate_text(neutral_scale, theme):
  """3-level text hierarchy.

  Dark mode uses neutral-400 for muted (not 500) to guarantee 3:1+
  contrast on elevated surfaces (surface-hover, tooltip-bg).
  """
  if theme == "dark":
    return {
      "primary":   neutral_scale["50"],
      "secondary": neutral_scale["300"],
      "muted":     neutral_scale["400"],
    }
  else:
    return {
      "primary":   neutral_scale["900"],
      "secondary": neutral_scale["700"],
      "muted":     neutral_scale["500"],
    }


def generate_borders(neutral_scale, theme):
  """3-level border hierarchy (subtle/default/strong)."""
  if theme == "dark":
    return {
      "subtle":  "rgba(255,255,255,0.06)",
      "default": neutral_scale["700"],
      "strong":  neutral_scale["600"],
    }
  else:
    return {
      "subtle":  "rgba(0,0,0,0.06)",
      "default": neutral_scale["300"],
      "strong":  neutral_scale["400"],
    }


def generate_state_layers(theme):
  """M3-standard state layer opacities."""
  if theme == "dark":
    return {
      "hover":   "#FFFFFF14",   # white 8%
      "focus":   "#FFFFFF1A",   # white 10%
      "pressed": "#FFFFFF29",   # white 16%
    }
  else:
    return {
      "hover":   "#00000014",   # black 8%
      "focus":   "#0000001A",   # black 10%
      "pressed": "#00000029",   # black 16%
    }


def generate_skeleton(neutral_scale, theme):
  """Skeleton loader colors (surface+1 rule)."""
  if theme == "dark":
    return {
      "base":    neutral_scale["800"],
      "shimmer": neutral_scale["700"],
    }
  else:
    return {
      "base":    neutral_scale["200"],
      "shimmer": neutral_scale["100"],
    }


def generate_overlay(theme):
  """Modal/dialog backdrop scrim."""
  if theme == "dark":
    return "#00000099"   # 60% black
  else:
    return "#00000066"   # 40% black


# ---------------------------------------------------------------------------
# Chart Palette — equally-spaced hues for data visualization
# ---------------------------------------------------------------------------

def generate_chart_palette(primary_hue, theme):
  """Generate 8-color categorical chart palette.

  Series 1 = primary hue. Series 2-8 = equally spaced around the wheel,
  skipping hues too close to primary. All at medium-high chroma.
  """
  base_L = 0.65 if theme == "dark" else 0.55
  base_C = 0.15

  # Start with primary, then distribute 7 more hues evenly
  hues = [primary_hue]
  for i in range(1, 8):
    hues.append((primary_hue + i * 45) % 360)  # 360/8 = 45° spacing

  palette = {}
  for i, hue in enumerate(hues):
    palette[f"series-{i+1}"] = oklch_to_hex(base_L, base_C, hue)

  return palette


# ---------------------------------------------------------------------------
# Spacing — density-driven
# ---------------------------------------------------------------------------

DENSITY_SPACING = {
  "compact": {
    "unit": "4px",
    "grid-gap": "16px",
    "section-y": "16px",
    "card-padding": "16px",
  },
  "comfortable": {
    "unit": "8px",
    "grid-gap": "24px",
    "section-y": "24px",
    "card-padding": "24px",
  },
  "spacious": {
    "unit": "12px",
    "grid-gap": "32px",
    "section-y": "32px",
    "card-padding": "32px",
  },
}


# ---------------------------------------------------------------------------
# Typography — density-adaptive base sizes
# ---------------------------------------------------------------------------

DENSITY_TYPOGRAPHY = {
  "compact": {
    "base": "13px",
    "scale-ratio": 1.150,
  },
  "comfortable": {
    "base": "14px",
    "scale-ratio": 1.200,
  },
  "spacious": {
    "base": "16px",
    "scale-ratio": 1.250,
  },
}


# ---------------------------------------------------------------------------
# Contrast Report
# ---------------------------------------------------------------------------

def build_contrast_report(text_colors, surfaces, semantic_colors, primary_500):
  """Check WCAG AA (4.5:1) for all text-on-surface pairs.

  Returns list of dicts with pair, ratio, wcag_aa, wcag_aaa.
  """
  report = []
  bg_pairs = list(surfaces.items())

  # Text on surfaces
  # "muted" text (placeholders, disabled) only needs 3:1 per WCAG AA
  # for UI components / large text. Normal text needs 4.5:1.
  for text_name, text_hex in text_colors.items():
    threshold = 3.0 if text_name == "muted" else 4.5
    for surf_name, surf_hex in bg_pairs:
      # Skip non-hex values (like rgba)
      if not surf_hex.startswith("#"):
        continue
      ratio = contrast_ratio(text_hex, surf_hex)
      report.append({
        "pair": f"text-{text_name} on {surf_name}",
        "ratio": round(ratio, 2),
        "wcag_aa": ratio >= threshold,
        "wcag_aaa": ratio >= 7.0,
        "threshold": f"{threshold}:1",
      })

  # Primary on surfaces
  for surf_name, surf_hex in bg_pairs:
    if not surf_hex.startswith("#"):
      continue
    ratio = contrast_ratio(primary_500, surf_hex)
    report.append({
      "pair": f"primary on {surf_name}",
      "ratio": round(ratio, 2),
      "wcag_aa": ratio >= 3.0,
      "wcag_aaa": ratio >= 4.5,
      "threshold": "3:1",
    })

  # Semantic on background
  bg_hex = surfaces.get("background", surfaces.get("surface", "#000000"))
  if bg_hex.startswith("#"):
    for name, color_hex in semantic_colors.items():
      ratio = contrast_ratio(color_hex, bg_hex)
      report.append({
        "pair": f"{name} on background",
        "ratio": round(ratio, 2),
        "wcag_aa": ratio >= 3.0,
        "wcag_aaa": ratio >= 4.5,
        "threshold": "3:1",
      })

  return report


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def compute_palette(primary_hex, theme, density):
  """Compute full palette from primary hex + theme + density.

  Returns a dict ready for JSON serialization.
  """
  primary_L, primary_C, primary_H = hex_to_oklch(primary_hex)

  # Handle achromatic inputs (white, black, grays): default to blue-grey hue
  if primary_C < 0.005:
    primary_H = 250.0  # blue-grey default for achromatic

  # 1. Color scales
  primary_scale = generate_scale(primary_hex)
  neutral_scale = generate_neutral_scale(primary_H)

  # 2. Semantic status colors (with hue collision avoidance)
  semantic = generate_semantic_colors(primary_H, theme)

  # 3. Surfaces (from neutral scale)
  surfaces = generate_surfaces(neutral_scale, theme)

  # 4. Text hierarchy
  text = generate_text(neutral_scale, theme)

  # 5. Borders
  borders = generate_borders(neutral_scale, theme)

  # 6. State layers (M3)
  state_layers = generate_state_layers(theme)

  # 7. Skeleton
  skeleton = generate_skeleton(neutral_scale, theme)

  # 8. Overlay
  overlay = generate_overlay(theme)

  # 9. Chart palette (8 categorical colors)
  chart = generate_chart_palette(primary_H, theme)

  # 10. Spacing
  spacing = DENSITY_SPACING[density]

  # 11. Typography density
  typography = DENSITY_TYPOGRAPHY[density]

  # 12. Contrast report
  report = build_contrast_report(
    text, surfaces, semantic, primary_scale["500"]
  )

  # Count failures
  aa_failures = [r for r in report if not r["wcag_aa"]]

  return {
    "primary_scale": primary_scale,
    "neutral_scale": neutral_scale,
    "semantic": semantic,
    "surfaces": surfaces,
    "text": text,
    "borders": borders,
    "state_layers": state_layers,
    "skeleton": skeleton,
    "overlay": overlay,
    "chart": chart,
    "spacing": spacing,
    "typography": typography,
    "contrast_report": report,
    "contrast_summary": {
      "total_pairs": len(report),
      "aa_pass": len(report) - len(aa_failures),
      "aa_fail": len(aa_failures),
      "failures": [r["pair"] for r in aa_failures],
    },
    "meta": {
      "primary_hex": primary_hex,
      "primary_oklch": {
        "L": round(primary_L, 4),
        "C": round(primary_C, 4),
        "H": round(primary_H, 1),
      },
      "neutral_hue": round(_neutral_hue(primary_H), 1),
      "theme": theme,
      "density": density,
      "generator": "compute_palette.py v2.0.0",
    },
  }


def main():
  parser = argparse.ArgumentParser(
    description="Compute design palette from a single hex color using OKLCH math"
  )
  parser.add_argument(
    "--hex", required=True,
    help="Primary brand color as #RRGGBB (e.g. #2563EB)"
  )
  parser.add_argument(
    "--theme", default="dark", choices=["dark", "light"],
    help="Color theme direction (default: dark)"
  )
  parser.add_argument(
    "--density", default="comfortable",
    choices=["compact", "comfortable", "spacious"],
    help="Spacing density (default: comfortable)"
  )
  args = parser.parse_args()

  # Validate hex
  hex_str = args.hex.strip().upper()
  if not hex_str.startswith("#"):
    hex_str = "#" + hex_str
  if len(hex_str) != 7:
    print("Error: --hex must be #RRGGBB format (6 hex digits)", file=sys.stderr)
    sys.exit(1)
  try:
    int(hex_str[1:], 16)
  except ValueError:
    print("Error: --hex contains invalid hex characters", file=sys.stderr)
    sys.exit(1)

  result = compute_palette(hex_str, args.theme, args.density)
  json.dump(result, sys.stdout, indent=2)
  print()


if __name__ == "__main__":
  main()
