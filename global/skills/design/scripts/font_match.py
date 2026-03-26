#!/usr/bin/env python3
"""
Font Match — Find closest Google Font from a screenshot.

Uses Storia AI's font-classify ONNX model (3473 Google Fonts).
No albumentations dependency — pure PIL + numpy.

Usage:
  python3 font_match.py --image screenshot.png [--top 5]

Prerequisites:
  pip install onnxruntime pillow huggingface_hub pyyaml numpy

First run downloads ~50MB model from HuggingFace.
"""

import argparse
import sys
import numpy as np
from pathlib import Path

try:
    import onnxruntime as ort
    from PIL import Image
    import yaml
    from huggingface_hub import hf_hub_download
except ImportError as e:
    print(f"Missing dependency: {e}")
    print("Install: pip install onnxruntime pillow huggingface_hub pyyaml numpy")
    sys.exit(1)


REPO_ID = "storia/font-classify-onnx"
INPUT_SIZE = 320
IMAGENET_MEAN = np.array([0.485, 0.456, 0.406])
IMAGENET_STD = np.array([0.229, 0.224, 0.225])


def download_model():
    """Download ONNX model and config from HuggingFace."""
    model_path = hf_hub_download(repo_id=REPO_ID, filename="model.onnx")
    config_path = hf_hub_download(repo_id=REPO_ID, filename="model_config.yaml")
    return model_path, config_path


def resize_with_pad(image, target_size):
    """Resize image preserving aspect ratio, pad to square."""
    w, h = image.size
    scale = min(target_size / w, target_size / h)
    new_w, new_h = int(w * scale), int(h * scale)
    image = image.resize((new_w, new_h), Image.LANCZOS)

    padded = Image.new("RGB", (target_size, target_size), (255, 255, 255))
    offset_x = (target_size - new_w) // 2
    offset_y = (target_size - new_h) // 2
    padded.paste(image, (offset_x, offset_y))
    return padded


def preprocess(image_path, size=INPUT_SIZE):
    """Load and preprocess image for ONNX inference."""
    img = Image.open(image_path).convert("RGB")

    # Crop to max 1024px on longest side
    w, h = img.size
    if max(w, h) > 1024:
        scale = 1024 / max(w, h)
        img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)

    # Resize with padding to square
    img = resize_with_pad(img, size)

    # Normalize (ImageNet stats)
    arr = np.array(img, dtype=np.float32) / 255.0
    arr = (arr - IMAGENET_MEAN) / IMAGENET_STD

    # HWC -> CHW, add batch dim
    arr = np.transpose(arr, (2, 0, 1))
    arr = np.expand_dims(arr, 0).astype(np.float32)
    return arr


def softmax(x):
    e_x = np.exp(x - np.max(x))
    return e_x / e_x.sum()


def classname_to_font_name(classname):
    """Convert model classname (e.g. 'PlayfairDisplay-Bold') to readable name."""
    # Remove file extension patterns
    name = classname.replace('.ttf', '').replace('.otf', '')
    # Remove weight/style suffixes for grouping
    for suffix in ['-Regular', '-Bold', '-Italic', '-Light', '-Medium',
                   '-SemiBold', '-ExtraBold', '-Black', '-Thin',
                   '-BoldItalic', '-LightItalic', '-MediumItalic']:
        if name.endswith(suffix):
            name = name[:-len(suffix)]
            break
    # Remove variable font axis notation
    if '[' in name:
        name = name[:name.index('[')]
    # Split CamelCase
    result = name[0]
    for c in name[1:]:
        if c.isupper() and result[-1].islower():
            result += ' '
        result += c
    return result


def main():
    parser = argparse.ArgumentParser(description="Find closest Google Font from screenshot")
    parser.add_argument("--image", "-i", required=True, help="Path to screenshot with text")
    parser.add_argument("--top", "-t", type=int, default=5, help="Number of top matches (default: 5)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    if not Path(args.image).exists():
        print(f"Error: {args.image} not found")
        sys.exit(1)

    # Download model
    model_path, config_path = download_model()

    # Load config
    with open(config_path) as f:
        config = yaml.safe_load(f)
    classnames = config["classnames"]

    # Run inference
    session = ort.InferenceSession(model_path)
    image = preprocess(args.image, config.get("size", INPUT_SIZE))
    logits = session.run(None, {"input": image})[0][0]
    probs = softmax(logits)

    # Get top N
    top_indices = np.argsort(probs)[::-1][:args.top * 3]  # get more to dedupe families

    # Deduplicate by font family
    seen_families = set()
    results = []
    for idx in top_indices:
        classname = classnames[idx]
        family = classname_to_font_name(classname)
        confidence = float(probs[idx])

        if family not in seen_families:
            seen_families.add(family)
            results.append({
                "rank": len(results) + 1,
                "family": family,
                "classname": classname,
                "confidence": round(confidence * 100, 2),
                "google_fonts_url": f"https://fonts.google.com/specimen/{family.replace(' ', '+')}"
            })

        if len(results) >= args.top:
            break

    if args.json:
        import json
        print(json.dumps(results, indent=2))
    else:
        print(f"\nFont matching results for: {args.image}")
        print(f"{'='*60}")
        for r in results:
            bar = "█" * int(r["confidence"] * 2) if r["confidence"] > 1 else "▏"
            print(f"  #{r['rank']}  {r['family']:<25} {r['confidence']:>6.2f}%  {bar}")
        print(f"\nTop match: {results[0]['family']} ({results[0]['confidence']}%)")
        print(f"Google Fonts: {results[0]['google_fonts_url']}")


if __name__ == "__main__":
    main()
