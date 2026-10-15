from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


REPO_ROOT = Path(__file__).resolve().parents[2]

# Assure la création automatique du dossier data pour SQLite (sur Linux / Render)
(REPO_ROOT / "data").mkdir(parents=True, exist_ok=True)


class Settings(BaseSettings):
    app_name: str = "Générateur de fiches pédagogiques — 4e"
    database_url: str = f"sqlite:///{(REPO_ROOT / 'data' / 'app.db').as_posix()}"
    export_dir: Path = REPO_ROOT / "exports"
    cors_origins: str = "http://127.0.0.1:5173,http://localhost:5173,https://fiche-pedagogique-benin.vercel.app"
    package_import_key: str = ""
    package_max_compressed_bytes: int = 20 * 1024 * 1024
    package_max_uncompressed_bytes: int = 50 * 1024 * 1024
    package_max_member_bytes: int = 10 * 1024 * 1024
    package_max_members: int = 200
    package_max_compression_ratio: float = 100.0
    model_config = SettingsConfigDict(env_file=REPO_ROOT / ".env", extra="ignore")


settings = Settings()
