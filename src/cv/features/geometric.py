from __future__ import annotations

import cv2
import numpy as np

EPS = 1e-9


def extract(contour: np.ndarray, mask: np.ndarray) -> dict:
    area = float(cv2.contourArea(contour))
    perimeter = float(cv2.arcLength(contour, True))
    if area < EPS or perimeter < EPS:
        raise ValueError("Degenerate contour: zero area or perimeter.")

    hull = cv2.convexHull(contour)
    hull_area = float(cv2.contourArea(hull))
    hull_perimeter = float(cv2.arcLength(hull, True))

    x, y, bw, bh = cv2.boundingRect(contour)
    (_, _), (rw, rh), _ = cv2.minAreaRect(contour)
    major_r, minor_r = max(rw, rh), min(rw, rh)

    if len(contour) >= 5:
        (_, _), (ax1, ax2), _ = cv2.fitEllipse(contour)
        major, minor = max(ax1, ax2), min(ax1, ax2)
    else:
        major, minor = major_r, minor_r

    _, circum_r = cv2.minEnclosingCircle(contour)
    inscribed_r = float(cv2.distanceTransform(mask, cv2.DIST_L2, 5).max())
    eq_diameter = float(np.sqrt(4.0 * area / np.pi))

    return {
        "geo_area": area,
        "geo_perimeter": perimeter,
        "geo_aspect_ratio": major_r / (minor_r + EPS),
        "geo_extent": area / (bw * bh + EPS),
        "geo_rectangularity": area / (rw * rh + EPS),
        "geo_solidity": area / (hull_area + EPS),
        "geo_convexity": hull_perimeter / (perimeter + EPS),
        "geo_circularity": 4.0 * np.pi * area / (perimeter ** 2 + EPS),
        "geo_sphericity": inscribed_r / (circum_r + EPS),
        "geo_eccentricity": float(np.sqrt(max(0.0, 1.0 - (minor / (major + EPS)) ** 2))),
        "geo_elongation": 1.0 - minor / (major + EPS),
        "geo_eq_diameter": eq_diameter,
        "geo_narrow_factor": eq_diameter / (major + EPS),
        "geo_perim_over_diameter": perimeter / (eq_diameter + EPS),
        "geo_perim_over_axes": perimeter / (major + minor + EPS),
        "geo_hull_area_ratio": hull_area / (bw * bh + EPS),
        "geo_bbox_ratio": bw / (bh + EPS),
    }