from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


REPO_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    app_name: str = "Générateur de fiches pédagogiques — 4e"
    database_url: str = f"sqlite:///{(REPO_ROOT / 'data' / 'app.db').as_posix()}"
    export_dir: Path = REPO_ROOT / "exports"
    cors_origins: str = "http://127.0.0.1:5173,http://localhost:5173"
    model_config = SettingsConfigDict(env_file=REPO_ROOT / ".env", extra="ignore")


settings = Settings()

