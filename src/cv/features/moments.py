"""Hu and Zernike moments — translation, scale and rotation invariant."""
from __future__ import annotations

import cv2
import mahotas
import numpy as np

ZERNIKE_DEGREE = 8
N_ZERNIKE = 25  # number of coefficients mahotas returns at degree 8


def extract(contour: np.ndarray, mask: np.ndarray) -> dict:
    feats: dict[str, float] = {}

    hu = cv2.HuMoments(cv2.moments(contour)).flatten()
    # Raw Hu values span many orders of magnitude; the signed log makes them
    # usable by distance-based and linear models.
    for i, h in enumerate(hu):
        feats[f"hu_{i + 1}"] = float(-np.sign(h) * np.log10(abs(h) + 1e-30))

    binary = (mask > 0).astype(np.uint8)
    radius = float(np.sqrt((binary.sum()) / np.pi)) * 1.6
    try:
        z = mahotas.features.zernike_moments(binary, max(radius, 1.0),
                                             degree=ZERNIKE_DEGREE)
    except Exception:
        z = np.zeros(N_ZERNIKE)
    z = np.asarray(z, dtype=float)
    if z.shape[0] < N_ZERNIKE:
        z = np.pad(z, (0, N_ZERNIKE - z.shape[0]))
    for i, v in enumerate(z[:N_ZERNIKE]):
        feats[f"zernike_{i:02d}"] = float(v)

    return feats