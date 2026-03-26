#!/usr/bin/env python3
"""Extract dominant colors from a screenshot using Pillow + K-means.

Visual-to-Blueprint pipeline: takes a screenshot and extracts the dominant
brand colors using OKLCH-aware clustering with vibrant/neutral separation.

Usage:
  python3 extract_colors.py --image screenshot.png --count 5
  python3 extract_colors.py --image screenshot.png --count 5 --json

Output: JSON to stdout with extracted colors, OKLCH values, and role hints.

Dependencies: Pillow (PIL). Install: pip3 install Pillow
OKLCH math: copied from compute_palette.py v2.0.0 (no shared module — KISS).
"""

import argparse
import json
import math
import random
import sys


# ---------------------------------------------------------------------------
# OKLCH Color Math — copied from compute_palette.py v2.0.0
# Keep in sync manually. If compute_palette.py changes, update here.
# ---------------------------------------------------------------------------

def _srgb_to_linear(c):
  if c <= 0.04045:
    return c / 12.92
  return ((c + 0.055) / 1.055) ** 2.4


def _linear_to_srgb(c):
  if c <= 0.0031308:
    return c * 12.92
  return 1.055 * (c ** (1 / 2.4)) - 0.055


def _cbrt(x):
  if x >= 0:
    return x ** (1 / 3)
  return -((-x) ** (1 / 3))


def hex_to_rgb(hex_str):
  h = hex_str.lstrip("#")
  return (int(h[0:2], 16) / 255, int(h[2:4], 16) / 255, int(h[4:6], 16) / 255)


def rgb_to_hex(r, g, b):
  r = max(0.0, min(1.0, r))
  g = max(0.0, min(1.0, g))
  b = max(0.0, min(1.0, b))
  return "#{:02X}{:02X}{:02X}".format(
    round(r * 255), round(g * 255), round(b * 255)
  )


def srgb_to_oklab(r, g, b):
  r_lin = _srgb_to_linear(r)
  g_lin = _srgb_to_linear(g)
  b_lin = _srgb_to_linear(b)
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


def oklab_to_oklch(L, a, b):
  C = math.sqrt(a * a + b * b)
  H = math.degrees(math.atan2(b, a)) % 360
  return (L, C, H)


def oklch_to_oklab(L, C, H):
  H_rad = math.radians(H)
  a = C * math.cos(H_rad)
  b = C * math.sin(H_rad)
  return (L, a, b)


def _is_in_gamut(L, C, H):
  lab_L, lab_a, lab_b = oklch_to_oklab(L, C, H)
  r, g, b = oklab_to_srgb(lab_L, lab_a, lab_b)
  return all(-0.002 <= v <= 1.002 for v in (r, g, b))


def oklab_to_srgb(L, a, b):
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


def oklch_to_hex(L, C, H):
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


def rgb_to_oklch(r, g, b):
  L, a, b_val = srgb_to_oklab(r, g, b)
  return oklab_to_oklch(L, a, b_val)


def hex_to_oklch(hex_str):
  r, g, b = hex_to_rgb(hex_str)
  return rgb_to_oklch(r, g, b)


# ---------------------------------------------------------------------------
# K-means Clustering — pure stdlib
# ---------------------------------------------------------------------------

def _distance_sq(a, b):
  """Squared Euclidean distance in OKLCH space (L, C, H as cartesian)."""
  return sum((x - y) ** 2 for x, y in zip(a, b))


def _kmeans(points, k, max_iter=20):
  """K-means clustering on list of (L, a, b) tuples.

  Works in OKLab space (cartesian) for meaningful distances.
  Returns list of (centroid, member_indices) tuples sorted by cluster size desc.
  """
  if len(points) <= k:
    return [(p, [i]) for i, p in enumerate(points)]

  # Init: k-means++ seeding for better convergence
  n = len(points)
  dim = len(points[0])
  centroids = [points[random.randint(0, n - 1)]]
  for _ in range(1, k):
    dists = []
    for p in points:
      min_d = min(_distance_sq(p, c) for c in centroids)
      dists.append(min_d)
    total = sum(dists)
    if total == 0:
      centroids.append(points[random.randint(0, n - 1)])
      continue
    r = random.random() * total
    cumulative = 0
    for i, d in enumerate(dists):
      cumulative += d
      if cumulative >= r:
        centroids.append(points[i])
        break

  # Iterate
  assignments = [0] * n
  for _ in range(max_iter):
    changed = False
    # Assign
    for i, p in enumerate(points):
      best_k = 0
      best_d = _distance_sq(p, centroids[0])
      for ki in range(1, k):
        d = _distance_sq(p, centroids[ki])
        if d < best_d:
          best_d = d
          best_k = ki
      if assignments[i] != best_k:
        changed = True
        assignments[i] = best_k

    if not changed:
      break

    # Update centroids
    for ki in range(k):
      members = [points[i] for i in range(n) if assignments[i] == ki]
      if members:
        centroids[ki] = tuple(
          sum(m[d] for m in members) / len(members) for d in range(dim)
        )

  # Collect results
  clusters = []
  for ki in range(k):
    members = [i for i in range(n) if assignments[i] == ki]
    if members:
      clusters.append((centroids[ki], members))

  clusters.sort(key=lambda x: -len(x[1]))
  return clusters


# ---------------------------------------------------------------------------
# Color Extraction Pipeline
# ---------------------------------------------------------------------------

VIBRANT_CHROMA_THRESHOLD = 0.04


def _pixels_to_oklab(pixels):
  """Convert list of (r, g, b) 0-255 tuples to OKLab (L, a, b) list.

  Also returns OKLCH for each pixel (for filtering).
  """
  oklab_points = []
  oklch_points = []
  for r, g, b in pixels:
    rf, gf, bf = r / 255.0, g / 255.0, b / 255.0
    L, a, b_val = srgb_to_oklab(rf, gf, bf)
    oklab_points.append((L, a, b_val))
    C = math.sqrt(a * a + b_val * b_val)
    H = math.degrees(math.atan2(b_val, a)) % 360
    oklch_points.append((L, C, H))
  return oklab_points, oklch_points


def _hue_distance(h1, h2):
  d = abs(h1 - h2) % 360
  return min(d, 360 - d)


def _assign_roles(colors):
  """Assign role hints based on chroma ranking and hue distance.

  Highest chroma vibrant cluster = primary_candidate.
  Second vibrant with hue distance > 30 from primary = accent_candidate.
  Rest = supporting.
  Neutrals get background_candidate or text_candidate based on lightness.
  """
  if not colors:
    return colors

  for c in colors:
    if c["_is_neutral"]:
      if c["oklch"]["L"] > 0.60:
        c["role_hint"] = "background_candidate"
      else:
        c["role_hint"] = "text_candidate"
    else:
      c["role_hint"] = "supporting"

  vibrant = [c for c in colors if not c["_is_neutral"]]
  vibrant.sort(key=lambda c: -c["oklch"]["C"])

  if vibrant:
    vibrant[0]["role_hint"] = "primary_candidate"
    primary_hue = vibrant[0]["oklch"]["H"]
    for c in vibrant[1:]:
      if _hue_distance(c["oklch"]["H"], primary_hue) > 30:
        c["role_hint"] = "accent_candidate"
        break

  return colors


def extract_colors(image_path, count=5):
  """Extract dominant colors from image.

  Pipeline: load → resize 150x150 → convert to OKLab → split vibrant/neutral
  → K-means on each bucket → merge → rank → assign roles.
  """
  try:
    from PIL import Image
  except ImportError:
    return {"error": "Pillow required. Install: pip3 install Pillow"}

  try:
    img = Image.open(image_path).convert("RGB")
  except Exception as e:
    return {"error": f"Cannot open image: {e}"}

  original_size = img.size
  img = img.resize((150, 150), Image.LANCZOS)
  pixels = list(img.getdata())
  total_pixels = len(pixels)

  oklab_points, oklch_points = _pixels_to_oklab(pixels)

  # Split into vibrant and neutral buckets
  vibrant_indices = []
  neutral_indices = []
  for i, (L, C, H) in enumerate(oklch_points):
    if C >= VIBRANT_CHROMA_THRESHOLD and 0.10 <= L <= 0.90:
      vibrant_indices.append(i)
    else:
      neutral_indices.append(i)

  # Determine cluster counts: allocate more to vibrant (brand colors matter more)
  vibrant_k = min(max(count - 1, 2), len(vibrant_indices)) if vibrant_indices else 0
  neutral_k = min(max(count - vibrant_k, 1), len(neutral_indices)) if neutral_indices else 0

  # Fallback: if no vibrant pixels, all clusters from neutral
  if vibrant_k == 0:
    neutral_k = min(count, len(neutral_indices))

  colors = []

  # Cluster vibrant pixels
  if vibrant_k > 0 and vibrant_indices:
    vibrant_points = [oklab_points[i] for i in vibrant_indices]
    clusters = _kmeans(vibrant_points, vibrant_k)
    for centroid, members in clusters:
      L, a, b = centroid
      C_val = math.sqrt(a * a + b * b)
      H_val = math.degrees(math.atan2(b, a)) % 360
      r, g, b_rgb = oklab_to_srgb(L, a, b)
      hex_val = rgb_to_hex(r, g, b_rgb)
      pct = round(len(members) / total_pixels * 100, 1)
      colors.append({
        "hex": hex_val,
        "oklch": {"L": round(L, 3), "C": round(C_val, 4), "H": round(H_val, 1)},
        "percentage": pct,
        "_is_neutral": False,
      })

  # Cluster neutral pixels
  if neutral_k > 0 and neutral_indices:
    neutral_points = [oklab_points[i] for i in neutral_indices]
    clusters = _kmeans(neutral_points, neutral_k)
    for centroid, members in clusters:
      L, a, b = centroid
      C_val = math.sqrt(a * a + b * b)
      H_val = math.degrees(math.atan2(b, a)) % 360
      r, g, b_rgb = oklab_to_srgb(L, a, b)
      hex_val = rgb_to_hex(r, g, b_rgb)
      pct = round(len(members) / total_pixels * 100, 1)
      colors.append({
        "hex": hex_val,
        "oklch": {"L": round(L, 3), "C": round(C_val, 4), "H": round(H_val, 1)},
        "percentage": pct,
        "_is_neutral": True,
      })

  # Sort: vibrant first (by chroma desc), then neutral (by percentage desc)
  vibrant_colors = sorted(
    [c for c in colors if not c["_is_neutral"]],
    key=lambda c: -c["oklch"]["C"]
  )
  neutral_colors = sorted(
    [c for c in colors if c["_is_neutral"]],
    key=lambda c: -c["percentage"]
  )
  colors = vibrant_colors + neutral_colors

  # Trim to requested count
  colors = colors[:count]

  # Assign role hints
  colors = _assign_roles(colors)

  # Remove internal flag
  for c in colors:
    del c["_is_neutral"]

  return {
    "colors": colors,
    "meta": {
      "source": image_path,
      "original_size": f"{original_size[0]}x{original_size[1]}",
      "pixels_analyzed": total_pixels,
      "vibrant_pixels": len(vibrant_indices),
      "neutral_pixels": len(neutral_indices),
    },
  }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
  parser = argparse.ArgumentParser(
    description="Extract dominant colors from screenshot (Pillow + K-means)"
  )
  parser.add_argument(
    "--image", required=True,
    help="Path to screenshot image (PNG, JPG, etc.)"
  )
  parser.add_argument(
    "--count", type=int, default=5,
    help="Number of colors to extract (default: 5)"
  )
  args = parser.parse_args()

  random.seed(42)  # Deterministic clustering
  result = extract_colors(args.image, args.count)

  if "error" in result:
    print(f"Error: {result['error']}", file=sys.stderr)
    sys.exit(1)

  json.dump(result, sys.stdout, indent=2)
  print()


if __name__ == "__main__":
  main()
