from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Leaf Shape Analysis API"
    database_url: str = f"sqlite:///{ROOT / 'storage' / 'leaf.db'}"
    storage_dir: Path = ROOT / "storage"
    artifacts_dir: Path = ROOT / "artifacts"
    max_upload_mb: int = 10
    work_size: int = 800
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    @property
    def images_dir(self) -> Path:
        return self.storage_dir / "images"


settings = Settings()
settings.images_dir.mkdir(parents=True, exist_ok=True)
settings.artifacts_dir.mkdir(parents=True, exist_ok=True)