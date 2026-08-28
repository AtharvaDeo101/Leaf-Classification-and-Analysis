from __future__ import annotations

import cv2
import numpy as np

RADII = (1, 2, 3, 4)
EPS = 1e-9


def extract(bgr: np.ndarray, mask: np.ndarray) -> dict:
    leaf_area = float((mask > 0).sum()) + EPS
    # The green channel gives the highest vein-to-blade contrast.
    gray = bgr[:, :, 1]
    gray = cv2.equalizeHist(gray)
    gray = cv2.bitwise_and(gray, gray, mask=mask)

    feats: dict[str, float] = {}
    ratios: list[float] = []
    for r in RADII:
        k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r + 1, 2 * r + 1))
        opened = cv2.morphologyEx(gray, cv2.MORPH_OPEN, k)
        tophat = cv2.subtract(gray, opened)
        _, vein = cv2.threshold(tophat, 0, 255,
                                cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        vein = cv2.bitwise_and(vein, vein, mask=mask)
        ratio = float((vein > 0).sum()) / leaf_area
        feats[f"vein_v{r}"] = ratio
        ratios.append(ratio)

    # Ratios between scales describe how vein thickness is distributed.
    for i in range(1, len(ratios)):
        feats[f"vein_v{i + 1}_over_v1"] = ratios[i] / (ratios[0] + EPS)

    return feats