"""Charge de façon idempotente le référentiel pilote 4e et ses occurrences sourcées."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.database import SessionLocal  # noqa: E402
from app.seed import seed_database  # noqa: E402

with SessionLocal() as session:
    print("Seed créé." if seed_database(session) else "Seed déjà présent.")

