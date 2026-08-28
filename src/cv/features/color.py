
from __future__ import annotations

import cv2
import numpy as np


def extract(bgr: np.ndarray, mask: np.ndarray) -> dict:
    idx = mask > 0
    feats: dict[str, float] = {}
    if idx.sum() == 0:
        return feats

    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    lab = cv2.cvtColor(bgr, cv2.COLOR_BGR2LAB)

    for space, img, names in (("hsv", hsv, "hsv"), ("lab", lab, "lab")):
        for c, ch in enumerate(names):
            vals = img[:, :, c][idx].astype(np.float32)
            feats[f"color_{space}_{ch}_mean"] = float(vals.mean())
            feats[f"color_{space}_{ch}_std"] = float(vals.std())
            centred = vals - vals.mean()
            skew = float(np.cbrt((centred ** 3).mean()))
            feats[f"color_{space}_{ch}_skew"] = skew

    return feats