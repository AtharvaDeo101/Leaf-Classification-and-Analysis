
from __future__ import annotations

import numpy as np
from pyefd import elliptic_fourier_descriptors

EFD_ORDER = 10
CCD_SAMPLES = 128
CCD_HARMONICS = 16


def _resample(points: np.ndarray, n: int) -> np.ndarray:
    """Arc-length resample so the signature is independent of contour density."""
    closed = np.vstack([points, points[:1]])
    seg = np.sqrt(((np.diff(closed, axis=0)) ** 2).sum(axis=1))
    cum = np.concatenate([[0.0], np.cumsum(seg)])
    if cum[-1] <= 0:
        return np.repeat(points[:1], n, axis=0)
    target = np.linspace(0, cum[-1], n, endpoint=False)
    xs = np.interp(target, cum, closed[:, 0])
    ys = np.interp(target, cum, closed[:, 1])
    return np.column_stack([xs, ys])


def extract(contour: np.ndarray) -> dict:
    pts = contour.reshape(-1, 2).astype(np.float64)
    feats: dict[str, float] = {}

    coeffs = elliptic_fourier_descriptors(pts, order=EFD_ORDER, normalize=True)
    # After normalisation coeffs[0] is fixed to (1, 0, 0, a) and carries no
    # discriminative information, so it is dropped.
    flat = coeffs[1:].flatten()
    for i, v in enumerate(flat):
        feats[f"efd_{i:02d}"] = float(v)

    sampled = _resample(pts, CCD_SAMPLES)
    centroid = sampled.mean(axis=0)
    dist = np.linalg.norm(sampled - centroid, axis=1)
    feats["ccd_mean_over_max"] = float(dist.mean() / (dist.max() + 1e-9))
    feats["ccd_std_norm"] = float(dist.std() / (dist.mean() + 1e-9))

    spectrum = np.abs(np.fft.fft(dist))
    dc = spectrum[0] + 1e-9
    for i in range(1, CCD_HARMONICS + 1):
        feats[f"ccd_fft_{i:02d}"] = float(spectrum[i] / dc)

    return feats