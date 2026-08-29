from __future__ import annotations

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from sqlalchemy.orm import Session

from backend.app.config import settings
from backend.app.db import get_db
from backend.app.schemas import AnalysisResult, SegmentResult
from backend.app.services.analysis import run_analysis, to_result_dict

router = APIRouter(prefix="/api", tags=["analysis"])

ALLOWED = {"image/jpeg", "image/png", "image/bmp", "image/tiff", "image/webp"}


def _read_upload(file: UploadFile) -> bytes:
    if file.content_type not in ALLOWED:
        raise HTTPException(415, f"Unsupported type '{file.content_type}'. "
                                 f"Allowed: {', '.join(sorted(ALLOWED))}")
    raw = file.file.read()
    if not raw:
        raise HTTPException(400, "Empty file.")
    if len(raw) > settings.max_upload_mb * 1024 * 1024:
        raise HTTPException(413, f"File exceeds {settings.max_upload_mb} MB.")
    return raw


# Deliberately sync `def`: FastAPI runs these in a threadpool, which is right
# for CPU-bound OpenCV work. An `async def` here would block the event loop.
@router.post("/analyze", response_model=AnalysisResult)
def analyze(file: UploadFile = File(...),
            model: str | None = Query(None, description="Model key; omit for default"),
            top_k: int = Query(5, ge=1, le=20),
            db: Session = Depends(get_db)):
    raw = _read_upload(file)
    try:
        record = run_analysis(db, raw, file.filename or "upload.jpg",
                              model_key=model, top_k=top_k, with_stages=True)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
    return to_result_dict(record)


@router.post("/segment", response_model=SegmentResult)
def segment_only(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Segmentation stages without classification — powers the pipeline viewer."""
    raw = _read_upload(file)
    try:
        record = run_analysis(db, raw, file.filename or "upload.jpg",
                              model_key=None, with_stages=True)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
    return {"id": record.id, "stage_urls": record.stage_urls, "meta": record.meta}


@router.post("/features")
def features_only(file: UploadFile = File(...), db: Session = Depends(get_db)):
    raw = _read_upload(file)
    try:
        record = run_analysis(db, raw, file.filename or "upload.jpg",
                              model_key=None, with_stages=False)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
    return {"id": record.id, "features": record.features,
            "count": len(record.features), "meta": record.meta}


@router.post("/batch")
def batch(files: list[UploadFile] = File(...),
          model: str | None = Query(None),
          db: Session = Depends(get_db)):
    if len(files) > 25:
        raise HTTPException(413, "Maximum 25 files per batch.")
    results, errors = [], []
    for f in files:
        try:
            raw = _read_upload(f)
            record = run_analysis(db, raw, f.filename or "upload.jpg",
                                  model_key=model, with_stages=False)
            results.append({"id": record.id, "filename": record.filename,
                            "prediction": (record.top_k or [None])[0]})
        except (HTTPException, ValueError) as exc:
            errors.append({"filename": f.filename, "error": str(exc)})
    return {"processed": len(results), "failed": len(errors),
            "results": results, "errors": errors}