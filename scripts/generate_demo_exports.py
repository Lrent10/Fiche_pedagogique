"""Génère les trois PDF représentatifs à partir des révisions de démonstration."""
import sys
from pathlib import Path

from sqlalchemy import select

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app import models as m  # noqa: E402
from app.database import SessionLocal  # noqa: E402
from app.exporter import export_document  # noqa: E402

with SessionLocal() as db:
    teacher = db.scalar(select(m.TeacherSheetRevision).where(m.TeacherSheetRevision.status == "FINALIZED").order_by(m.TeacherSheetRevision.id))
    support = db.scalar(select(m.LearnerSupportRevision).where(m.LearnerSupportRevision.status == "FINALIZED").order_by(m.LearnerSupportRevision.id))
    if not teacher or not support:
        raise SystemExit("Les révisions finalisées de démonstration sont absentes.")
    outputs = [
        export_document(db, "TEACHER", teacher.id, "TEACHER"),
        export_document(db, "LEARNER", support.id, "LEARNER_INITIAL"),
        export_document(db, "LEARNER", support.id, "LEARNER_COMPLETED"),
    ]
    for output in outputs:
        print(output.file_path)
