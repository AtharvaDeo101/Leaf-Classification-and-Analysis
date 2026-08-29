"""Run the CV pipeline over the whole dataset and write a feature CSV.

Run once, then freeze the output. Re-running after editing descriptor code
produces a CSV that is not comparable with earlier experiments, so bump the
version in the filename when you deliberately change features.

Usage (defaults point at archive/Leaves):
    python -m src.training.extract_dataset
    python -m src.training.extract_dataset --limit 20   # smoke test
"""
from __future__ import annotations

import argparse
import csv
import sys
import time
from pathlib import Path

import pandas as pd

from src.cv.pipeline import PIPELINE_VERSION, analyse

IMAGE_SUFFIXES = (".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff")


def index_images(images_dir: Path) -> dict[str, Path]:

    index: dict[str, Path] = {}
    for path in images_dir.rglob("*"):
        if path.suffix.lower() in IMAGE_SUFFIXES:
            index.setdefault(path.stem, path)
    return index


def resolve(raw_id, index: dict[str, Path]) -> Path | None:
    """Match a CSV id against the image index.

    Handles '1001', '1001.jpg', and floats like 1001.0 that pandas produces
    when a column has any missing value.
    """
    text = str(raw_id).strip()
    if text.endswith(".0"):
        text = text[:-2]
    stem = Path(text).stem
    return index.get(stem) or index.get(text)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--images", type=Path, default=Path("archive/Leaves"))
    ap.add_argument("--labels", type=Path,
                    default=Path("archive/Leaves/all.csv"))
    ap.add_argument("--out", type=Path,
                    default=Path("data/processed/features_v1.csv"))
    ap.add_argument("--id-col", default="id")
    ap.add_argument("--label-col", default="y")
    ap.add_argument("--work-size", type=int, default=800)
    ap.add_argument("--limit", type=int, default=0,
                    help="Process only the first N rows. Use 20 for a smoke test.")
    args = ap.parse_args()

    df = pd.read_csv(args.labels)
    df.columns = [c.strip() for c in df.columns]
    for col in (args.id_col, args.label_col):
        if col not in df.columns:
            print(f"Column '{col}' not in CSV. Found: {list(df.columns)}")
            return 1
    if args.limit:
        df = df.head(args.limit)

    index = index_images(args.images)
    print(f"Indexed {len(index)} images under {args.images}")
    print(f"Read {len(df)} label rows from {args.labels}")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    failures: list[tuple[str, str]] = []
    writer = None
    handle = None
    feature_names: list[str] = []
    written = 0
    started = time.time()

    try:
        for i, row in enumerate(df.itertuples(index=False), start=1):
            raw_id = getattr(row, args.id_col)
            label = getattr(row, args.label_col)
            path = resolve(raw_id, index)

            if path is None:
                failures.append((str(raw_id), "image file not found"))
                continue

            try:
                result = analyse(path.read_bytes(), work_size=args.work_size,
                                 want_stages=False)
            except Exception as exc:
                failures.append((str(raw_id), f"{type(exc).__name__}: {exc}"))
                continue

            features = result["features"]

            if writer is None:

                feature_names = sorted(features)
                handle = args.out.open("w", newline="", encoding="utf-8")
                writer = csv.writer(handle)
                writer.writerow(["image_id", "label", "margin_type", "seg_method"]
                                + feature_names)

            writer.writerow([
                path.stem, label,
                result["meta"].get("margin_type", ""),
                result["meta"].get("segmentation_method", ""),
            ] + [features.get(name, 0.0) for name in feature_names])
            written += 1

            if i % 50 == 0:
                rate = i / (time.time() - started)
                remaining = (len(df) - i) / max(rate, 1e-6)
                print(f"  {i}/{len(df)}  ok={written}  failed={len(failures)}  "
                      f"~{remaining/60:.1f} min left", flush=True)
    finally:
        if handle is not None:
            handle.close()

    if written == 0:
        print("\nNo images processed. Check --images and --id-col.")
        return 1

    elapsed = time.time() - started
    print(f"\nWrote {written} rows x {len(feature_names)} features to {args.out}")
    print(f"Pipeline version {PIPELINE_VERSION}, {elapsed/60:.1f} min elapsed")
    print(f"Classes: {df[args.label_col].nunique()}")

    if failures:
        log = args.out.with_suffix(".failures.csv")
        with log.open("w", newline="", encoding="utf-8") as fh:
            csv.writer(fh).writerows([("image_id", "reason"), *failures])
        print(f"\n{len(failures)} failed. Details: {log}")
        for image_id, reason in failures[:5]:
            print(f"  {image_id}: {reason}")

    return 0


if __name__ == "__main__":
    sys.exit(main())