"""Leaf/background separation, petiole removal, orientation normalisation."""
from __future__ import annotations

import cv2
import numpy as np


def _border_is_background(mask: np.ndarray, frac: float = 0.75) -> bool:
    """A correct mask has mostly-zero borders. Used to detect polarity flips."""
    border = np.concatenate([mask[0], mask[-1], mask[:, 0], mask[:, -1]])
    return float((border == 0).mean()) >= frac


def _mask_from_lab_a(bgr: np.ndarray) -> np.ndarray:
    """Otsu on the a* channel. Green pixels sit low in a*, white paper near 128,
    so the split is far cleaner than grayscale Otsu."""
    a = cv2.cvtColor(bgr, cv2.COLOR_BGR2LAB)[:, :, 1]
    _, mask = cv2.threshold(a, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    return mask


def _mask_from_exg(bgr: np.ndarray) -> np.ndarray:
    """Excess Green index: 2G - R - B, rescaled then Otsu."""
    b, g, r = cv2.split(bgr.astype(np.float32))
    exg = 2 * g - r - b
    exg = cv2.normalize(exg, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    _, mask = cv2.threshold(exg, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return mask


def _clean(mask: np.ndarray) -> np.ndarray:
    """Close holes, then open away specks."""
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, k, iterations=2)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, k, iterations=1)
    # Flood-fill holes from outside, then invert the unreachable region.
    ff = mask.copy()
    h, w = mask.shape
    cv2.floodFill(ff, np.zeros((h + 2, w + 2), np.uint8), (0, 0), 255)
    return mask | cv2.bitwise_not(ff)


def largest_component(mask: np.ndarray) -> np.ndarray:
    n, labels, stats, _ = cv2.connectedComponentsWithStats(mask, connectivity=8)
    if n <= 1:
        raise ValueError("Segmentation produced no foreground region.")
    idx = 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))
    return ((labels == idx).astype(np.uint8)) * 255


def segment(bgr: np.ndarray) -> dict:
    """Try both candidate masks, keep whichever has a cleaner background border
    and a plausible foreground fraction."""
    candidates = []
    for name, fn in (("lab_a", _mask_from_lab_a), ("exg", _mask_from_exg)):
        try:
            m = _clean(fn(bgr))
            if not _border_is_background(m):
                m = cv2.bitwise_not(m)
            frac = float((m > 0).mean())
            if 0.02 < frac < 0.95:
                candidates.append((name, m, frac))
        except cv2.error:
            continue

    if not candidates:
        raise ValueError("Segmentation failed. Use a plain, high-contrast background.")

    # Prefer the mask whose border is cleanest; break ties on larger foreground.
    def score(item):
        _, m, frac = item
        border = np.concatenate([m[0], m[-1], m[:, 0], m[:, -1]])
        return (float((border == 0).mean()), frac)

    method, mask, _ = max(candidates, key=score)
    mask = largest_component(mask)
    return {"mask": mask, "method": method}


def remove_petiole(mask: np.ndarray) -> dict:
    """Strip the leaf stalk.

    The petiole inflates perimeter and destroys solidity, circularity and every
    ratio derived from them. Opening with a disk wider than the stalk removes
    it. If opening costs more than 30% of the area the leaf itself was narrow
    (needle-like), so we revert rather than mutilate it.
    """
    area_before = float((mask > 0).sum())
    if area_before == 0:
        return {"mask": mask, "removed": False, "kernel_radius": 0}

    radius = max(3, int(0.035 * np.sqrt(area_before)))
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * radius + 1, 2 * radius + 1))
    opened = cv2.morphologyEx(mask, cv2.MORPH_OPEN, k)

    if (opened > 0).sum() == 0:
        return {"mask": mask, "removed": False, "kernel_radius": radius}

    opened = largest_component(opened)
    kept = float((opened > 0).sum()) / area_before
    if kept < 0.70:
        return {"mask": mask, "removed": False, "kernel_radius": radius}

    # Dilate back so the blade regains the width the opening shaved off,
    # then intersect with the original to stay inside the true boundary.
    restored = cv2.dilate(opened, k) & mask
    restored = largest_component(restored)
    return {"mask": restored, "removed": True, "kernel_radius": radius}


def normalise_orientation(mask: np.ndarray, bgr: np.ndarray) -> dict:
    """Rotate so the leaf's major axis is horizontal.

    Run this before any descriptor that is not rotation invariant.
    """
    pts = cv2.findNonZero(mask)
    if pts is None or len(pts) < 5:
        return {"mask": mask, "bgr": bgr, "angle": 0.0}

    data = pts.reshape(-1, 2).astype(np.float64)
    mean, eigvec, _ = cv2.PCACompute2(data, mean=None)
    angle = float(np.degrees(np.arctan2(eigvec[0, 1], eigvec[0, 0])))

    h, w = mask.shape
    centre = (float(mean[0, 0]), float(mean[0, 1]))
    M = cv2.getRotationMatrix2D(centre, angle, 1.0)

    # Expand the canvas so rotation cannot clip the leaf.
    cos, sin = abs(M[0, 0]), abs(M[0, 1])
    nw, nh = int(h * sin + w * cos), int(h * cos + w * sin)
    M[0, 2] += nw / 2 - centre[0]
    M[1, 2] += nh / 2 - centre[1]

    rot_mask = cv2.warpAffine(mask, M, (nw, nh), flags=cv2.INTER_NEAREST,
                              borderValue=0)
    rot_bgr = cv2.warpAffine(bgr, M, (nw, nh), flags=cv2.INTER_LINEAR,
                             borderValue=(255, 255, 255))
    _, rot_mask = cv2.threshold(rot_mask, 127, 255, cv2.THRESH_BINARY)
    return {"mask": rot_mask, "bgr": rot_bgr, "angle": angle}


def main_contour(mask: np.ndarray) -> np.ndarray:
    """Outer contour as int32 (N, 1, 2) — the dtype convexityDefects requires."""
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    if not contours:
        raise ValueError("No contour found in mask.")
    return max(contours, key=cv2.contourArea)