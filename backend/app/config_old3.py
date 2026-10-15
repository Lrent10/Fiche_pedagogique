from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


# Répertoire backend (racine de l'application)
BACKEND_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BACKEND_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

db_file = DATA_DIR / "app.db"
DEFAULT_DB_URL = f"sqlite:///{db_file.as_posix()}"

EXPORT_DIR = BACKEND_DIR / "exports"
EXPORT_DIR.mkdir(parents=True, exist_ok=True)


class Settings(BaseSettings):
    app_name: str = "Générateur de fiches pédagogiques — 4e"
    database_url: str = DEFAULT_DB_URL
    export_dir: Path = EXPORT_DIR
    cors_origins: str = "http://127.0.0.1:5173,http://localhost:5173,https://fiche-pedagogique-benin.vercel.app"
    package_import_key: str = ""
    package_max_compressed_bytes: int = 20 * 1024 * 1024
    package_max_uncompressed_bytes: int = 50 * 1024 * 1024
    package_max_member_bytes: int = 10 * 1024 * 1024
    package_max_members: int = 200
    package_max_compression_ratio: float = 100.0
    model_config = SettingsConfigDict(env_file=BACKEND_DIR / ".env", extra="ignore")


settings = Settings()
