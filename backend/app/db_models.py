from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import JSON, DateTime, Float, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.db import Base


def _uuid() -> str:
    return uuid.uuid4().hex


class Analysis(Base):
    __tablename__ = "analyses"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=_uuid)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc), index=True)

    filename: Mapped[str] = mapped_column(String(255))
    model_key: Mapped[str | None] = mapped_column(String(64), nullable=True)
    predicted_label: Mapped[str | None] = mapped_column(String(128), nullable=True,
                                                        index=True)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    margin_type: Mapped[str | None] = mapped_column(String(32), nullable=True)

    features: Mapped[dict] = mapped_column(JSON, default=dict)
    top_k: Mapped[list] = mapped_column(JSON, default=list)
    meta: Mapped[dict] = mapped_column(JSON, default=dict)
    stage_urls: Mapped[dict] = mapped_column(JSON, default=dict)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)