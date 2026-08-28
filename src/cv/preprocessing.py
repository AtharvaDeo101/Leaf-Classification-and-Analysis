
from __future__ import annotations

import cv2
import numpy as np


def decode_image(raw: bytes) -> np.ndarray:
    """Decode raw upload bytes into a BGR uint8 array."""
    buf = np.frombuffer(raw, dtype=np.uint8)
    img = cv2.imdecode(buf, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Could not decode image. Supported: jpg, png, bmp, tif.")
    return img


def resize_longest(img: np.ndarray, target: int = 800) -> np.ndarray:

    h, w = img.shape[:2]
    longest = max(h, w)
    if longest == target:
        return img
    scale = target / float(longest)
    interp = cv2.INTER_AREA if scale < 1 else cv2.INTER_CUBIC
    return cv2.resize(img, (int(round(w * scale)), int(round(h * scale))),
                      interpolation=interp)


def denoise(img: np.ndarray) -> np.ndarray:

    return cv2.bilateralFilter(img, d=7, sigmaColor=50, sigmaSpace=50)


def correct_illumination(img: np.ndarray) -> np.ndarray:
    """CLAHE on the L channel of LAB to flatten uneven lighting."""
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    lab = cv2.merge([clahe.apply(l), a, b])
    return cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)


def preprocess(raw: bytes, work_size: int = 800) -> dict:
    original = decode_image(raw)
    resized = resize_longest(original, work_size)
    corrected = correct_illumination(resized)
    smoothed = denoise(corrected)
    return {
        "original": original,
        "resized": resized,
        "preprocessed": smoothed,
        "original_shape": original.shape[:2],
        "work_shape": resized.shape[:2],
    }