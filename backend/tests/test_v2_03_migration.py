"""Exercise real Alembic upgrades, independently of the ORM test bootstrap."""
import os
from pathlib import Path
import subprocess
import sys

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from app.database import Base
from app import models as m


@pytest.mark.parametrize("existing", [False, True], ids=["empty-install", "preserve-0003"])
def test_migration_to_0004(tmp_path, existing):
    database = tmp_path / "migration.db"
    url = "sqlite:///" + database.as_posix()
    engine = create_engine(url)
    expected = None
    if existing:
        Base.metadata.create_all(engine)
        with Session(engine) as db:
            sheet = m.TeacherSessionSheet(code="HISTORICAL", title="Fiche préexistante", level="4e")
            db.add(sheet)
            db.flush()
            db.add(m.TeacherSheetRevision(sheet_id=sheet.id, revision_number=1, status="FINALIZED", identification_json='{"classe":"4e"}', planning_json='{"contenu":"à conserver"}'))
            resource = m.PedagogicalResource(code="HISTORICAL", title="Ressource préexistante", level="4e", resource_type="PROPERTY", provenance_kind="SOURCED", structure_kind="ATOMIC")
            db.add(resource)
            db.flush()
            db.add(m.PedagogicalResourceVersion(resource_id=resource.id, title="Propriété préexistante"))
            db.commit()
        # This disposable fixture represents exactly the pre-0004 surface.
        with engine.begin() as connection:
            connection.execute(text("DROP TABLE curriculum_attributes"))
            connection.execute(text("ALTER TABLE teacher_sheet_revisions DROP COLUMN authoring_json"))
            connection.execute(text("ALTER TABLE pedagogical_resource_versions DROP COLUMN provenance_json"))
            expected = tuple(connection.execute(text("SELECT * FROM teacher_sheet_revisions")).one())
            connection.execute(text("CREATE TABLE alembic_version (version_num VARCHAR(32) NOT NULL PRIMARY KEY)"))
            connection.execute(text("INSERT INTO alembic_version VALUES ('0003_final_document_editor')"))
    env = {**os.environ, "DATABASE_URL": url}
    result = subprocess.run([sys.executable, "-m", "alembic", "upgrade", "0004_curriculum_authoring"], cwd=Path(__file__).resolve().parents[1], env=env, capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
    with engine.connect() as connection:
        assert connection.execute(text("SELECT version_num FROM alembic_version")).scalar_one() == "0004_curriculum_authoring"
        assert connection.execute(text("SELECT COUNT(*) FROM curriculum_attributes")).scalar_one() == 0
        if existing:
            row = tuple(connection.execute(text("SELECT * FROM teacher_sheet_revisions")).one())
            assert row[:-1] == expected and row[-1] == "{}"
            assert connection.execute(text("SELECT title, provenance_json FROM pedagogical_resource_versions")).one() == ("Propriété préexistante", "{}")
    engine.dispose()
