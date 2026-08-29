from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np

from backend.app.config import settings


def save_stages(analysis_id: str, stages: dict[str, np.ndarray]) -> dict[str, str]:
    """Write stage images to storage/images/<id>/ and return public URLs."""
    folder = settings.images_dir / analysis_id
    folder.mkdir(parents=True, exist_ok=True)
    urls: dict[str, str] = {}
    for name, img in stages.items():
        path = folder / f"{name}.png"
        cv2.imwrite(str(path), img, [cv2.IMWRITE_PNG_COMPRESSION, 6])
        urls[name] = f"/static/images/{analysis_id}/{name}.png"
    return urls


def save_upload(analysis_id: str, raw: bytes, filename: str) -> str:
    folder = settings.images_dir / analysis_id
    folder.mkdir(parents=True, exist_ok=True)
    suffix = Path(filename).suffix.lower() or ".jpg"
    path = folder / f"upload{suffix}"
    path.write_bytes(raw)
    return f"/static/images/{analysis_id}/upload{suffix}"