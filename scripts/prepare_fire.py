#!/usr/bin/env python3
"""Prepare the locally extracted FIRE retinal benchmark for CPU experiments.

The benchmark archive is deliberately kept under ``data/raw``.  This script
creates a compact, reproducible grayscale representation and maps the supplied
landmarks to the requested experiment resolution without changing pair IDs.
"""
from pathlib import Path
import argparse
import json

import numpy as np
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/raw/fire/FIRE"
OUT = ROOT / "data/processed/fire"


def representation(rgb: np.ndarray) -> np.ndarray:
    """Contrast-normalized green channel, standard for retinal vasculature."""
    image = np.asarray(rgb, dtype=float)
    green = image[..., 1] if image.ndim == 3 else image
    # Resize before CLAHE: the registration solver operates at this resolution
    # and this avoids doing an expensive local histogram calculation at 3K².
    # Input JPEGs are about 3K square.  Pillow's decoder/resizer avoids an
    # unnecessary full floating-point image during bounded batch preparation.
    # ``green`` is already resized by the caller.
    # Black camera surround must not determine the contrast transform.
    foreground = green > np.percentile(green, 15)
    lo, hi = np.quantile(green[foreground], [0.01, 0.99])
    normalized = np.clip((green - lo) / (hi - lo + 1e-12), 0.0, 1.0)
    # Global normalization is intentional here.  CLAHE at original camera
    # resolution made preprocessing dominate the measured registration time.
    return normalized


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--size", type=int, default=256)
    parser.add_argument("--output", type=Path, default=OUT,
                        help="Prepared-data directory (keeps resolutions separate).")
    parser.add_argument("--image-start", type=int, default=0)
    parser.add_argument("--image-count", type=int, default=None)
    parser.add_argument("--landmarks-only", action="store_true")
    args = parser.parse_args()
    output = args.output
    if not (SOURCE / "Images").is_dir():
        raise FileNotFoundError(f"FIRE not extracted at {SOURCE}")
    output.mkdir(parents=True, exist_ok=True)
    image_paths = sorted((SOURCE / "Images").glob("*.jpg"))
    selected = image_paths[args.image_start:]
    if args.image_count is not None:
        selected = selected[:args.image_count]
    if args.landmarks_only:
        selected = []
    metadata = []
    for path in selected:
        with Image.open(path) as source_image:
            w, h = source_image.size
            resized = source_image.resize((args.size, args.size), Image.Resampling.LANCZOS)
            rgb = np.asarray(resized)
        prepared = representation(rgb).astype(np.float32)
        np.save(output / f"{path.stem}.npy", prepared)
        metadata.append({"name": path.stem, "source_shape": [h, w],
                         "prepared_shape": [args.size, args.size],
                         "scale_xy": [args.size / w, args.size / h]})
    if not args.landmarks_only:
        print(json.dumps({"prepared_images": len(metadata), "start": args.image_start}, indent=2))
        if args.image_start != 0 or len(selected) != len(image_paths):
            return
    # Reading JPEG headers only makes the final metadata/landmark pass cheap.
    metadata = []
    for path in image_paths:
        with Image.open(path) as image:
            w, h = image.size
        metadata.append({"name": path.stem, "source_shape": [h, w],
                         "prepared_shape": [args.size, args.size],
                         "scale_xy": [args.size / w, args.size / h]})
    pairs = []
    source_shapes = {item["name"]: item["source_shape"] for item in metadata}
    for points_path in sorted((SOURCE / "Ground Truth").glob("control_points_*_1_2.txt")):
        stem = points_path.stem.removeprefix("control_points_").removesuffix("_1_2")
        points = np.loadtxt(points_path, dtype=float).reshape(-1, 4)
        name1, name2 = f"{stem}_1", f"{stem}_2"
        # FIRE points are x1 y1 x2 y2 in original-image coordinates.
        p1, p2 = points[:, :2].copy(), points[:, 2:].copy()
        h1, w1 = source_shapes[name1]
        h2, w2 = source_shapes[name2]
        p1 *= args.size / np.array([w1, h1])
        p2 *= args.size / np.array([w2, h2])
        np.savez(output / f"control_points_{stem}.npz", fixed=p1, moving=p2)
        pairs.append({"pair": stem, "fixed": name1, "moving": name2,
                      "group": stem[0], "landmarks": int(len(p1))})
    (output / "metadata.json").write_text(json.dumps({
        "source": "FIRE archive extracted from data/downloads/FIRE.7z",
        "prepared_size": args.size,
        "preprocessing": "green channel and foreground percentile normalization",
        "landmark_convention": "x1,y1,x2,y2; fixed image is *_1 and moving image is *_2",
        "images": metadata, "pairs": pairs,
    }, indent=2) + "\n")
    print(json.dumps({"images": len(metadata), "pairs": len(pairs), "output": str(output)}, indent=2))


if __name__ == "__main__":
    main()
