from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from loguru import logger

from backend.app.config import settings
from backend.app.db import init_db
from backend.app.routers import analyze, health, history, models, species
from backend.app.services.registry import registry


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Models load once here, not per request. Loading a ResNet inside a
    # handler adds seconds to every call.
    logger.info("Starting up: initialising database and model registry")
    init_db()
    registry.load_all()
    yield
    logger.info("Shutting down")


app = FastAPI(title=settings.app_name, version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=settings.storage_dir), name="static")

app.include_router(health.router)
app.include_router(analyze.router)
app.include_router(history.router)
app.include_router(models.router)
app.include_router(species.router)


@app.get("/")
def root():
    return {"name": settings.app_name, "docs": "/docs"}