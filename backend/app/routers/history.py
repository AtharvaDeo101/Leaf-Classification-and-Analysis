from __future__ import annotations

import shutil

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.app.config import settings
from backend.app.db import get_db
from backend.app.db_models import Analysis
from backend.app.schemas import AnalysisResult, HistoryPage
from backend.app.services.analysis import to_result_dict

router = APIRouter(prefix="/api", tags=["history"])


@router.get("/history", response_model=HistoryPage)
def list_history(limit: int = Query(20, ge=1, le=100), offset: int = Query(0, ge=0),
                 db: Session = Depends(get_db)):
    total = db.scalar(select(func.count()).select_from(Analysis)) or 0
    items = db.scalars(
        select(Analysis).order_by(Analysis.created_at.desc())
        .limit(limit).offset(offset)
    ).all()
    return {"total": total, "items": items}


@router.get("/history/{analysis_id}", response_model=AnalysisResult)
def get_analysis(analysis_id: str, db: Session = Depends(get_db)):
    record = db.get(Analysis, analysis_id)
    if record is None:
        raise HTTPException(404, "Analysis not found.")
    return to_result_dict(record)


@router.delete("/history/{analysis_id}", status_code=204)
def delete_analysis(analysis_id: str, db: Session = Depends(get_db)):
    record = db.get(Analysis, analysis_id)
    if record is None:
        raise HTTPException(404, "Analysis not found.")
    shutil.rmtree(settings.images_dir / analysis_id, ignore_errors=True)
    db.delete(record)
    db.commit()