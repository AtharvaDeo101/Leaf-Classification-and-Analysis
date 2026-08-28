from __future__ import annotations

import cv2
import numpy as np
from skimage.feature import graycomatrix, graycoprops, local_binary_pattern

GLCM_LEVELS = 32
GLCM_DISTANCES = (1, 3)
GLCM_ANGLES = (0, np.pi / 4, np.pi / 2, 3 * np.pi / 4)
GLCM_PROPS = ("contrast", "dissimilarity", "homogeneity", "energy", "correlation")
LBP_P, LBP_R = 8, 1


def extract(bgr: np.ndarray, mask: np.ndarray) -> dict:
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    x, y, w, h = cv2.boundingRect(mask)
    gray_c, mask_c = gray[y:y + h, x:x + w], mask[y:y + h, x:x + w]

    feats: dict[str, float] = {}

    # Quantise to GLCM_LEVELS. Background is forced to 0 and shares that bin,
    # which adds a constant offset rather than class-dependent bias.
    q = (gray_c.astype(np.uint16) * (GLCM_LEVELS - 1) // 255).astype(np.uint8)
    q[mask_c == 0] = 0
    glcm = graycomatrix(q, distances=list(GLCM_DISTANCES),
                        angles=list(GLCM_ANGLES), levels=GLCM_LEVELS,
                        symmetric=True, normed=True)
    for prop in GLCM_PROPS:
        vals = graycoprops(glcm, prop)
        feats[f"glcm_{prop}_mean"] = float(np.nanmean(vals))
        feats[f"glcm_{prop}_range"] = float(np.nanmax(vals) - np.nanmin(vals))

    p = glcm.copy()
    feats["glcm_entropy"] = float(-np.sum(p * np.log2(p + 1e-12)) / p.shape[-1] /
                                  p.shape[-2])

    lbp = local_binary_pattern(gray_c, LBP_P, LBP_R, method="uniform")
    inside = lbp[mask_c > 0]
    n_bins = LBP_P + 2
    if inside.size:
        hist, _ = np.histogram(inside, bins=n_bins, range=(0, n_bins))
        hist = hist.astype(float) / (hist.sum() + 1e-9)
    else:
        hist = np.zeros(n_bins)
    for i, v in enumerate(hist):
        feats[f"lbp_{i:02d}"] = float(v)

    return feats