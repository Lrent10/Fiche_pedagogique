import os
import shutil
import tempfile
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


# Répertoire temporaire universel garanti 100% accessible en écriture (sur Render Linux /tmp et Windows)
TEMP_DIR = Path(tempfile.gettempdir())
db_file = TEMP_DIR / "app.db"

# Si une base existante data/app.db existe dans le repo, la copier
backend_root = Path(__file__).resolve().parents[2]
candidate_sources = [
    backend_root / "data" / "app.db",
    Path(__file__).resolve().parents[1] / "data" / "app.db",
]
for src in candidate_sources:
    if src.exists() and not db_file.exists():
        try:
            shutil.copy2(src, db_file)
            break
        except Exception:
            pass

DEFAULT_DB_URL = f"sqlite:///{db_file.as_posix()}"

EXPORT_DIR = TEMP_DIR / "exports"
EXPORT_DIR.mkdir(parents=True, exist_ok=True)


class Settings(BaseSettings):
    app_name: str = "Générateur de fiches pédagogiques — 4e"
    database_url: str = DEFAULT_DB_URL
    export_dir: Path = EXPORT_DIR
    cors_origins: str = "http://127.0.0.1:5173,http://localhost:5173,https://fiche-pedagogique-benin.vercel.app,*"
    package_import_key: str = ""
    package_max_compressed_bytes: int = 20 * 1024 * 1024
    package_max_uncompressed_bytes: int = 50 * 1024 * 1024
    package_max_member_bytes: int = 10 * 1024 * 1024
    package_max_members: int = 200
    package_max_compression_ratio: float = 100.0
    model_config = SettingsConfigDict(extra="ignore")


settings = Settings()
