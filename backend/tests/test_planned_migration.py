"""T13: genuine 0004-shaped disposable DB and empty installation."""
import os
from pathlib import Path
import subprocess
import sys

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from app.database import Base
from app import models as m
from app.seed import seed_database


@pytest.mark.parametrize('existing', [False, True], ids=['empty', 'historical-0004'])
def test_T13_migration_additive(tmp_path, existing):
    url = 'sqlite:///' + (tmp_path / 'isolated.db').as_posix()
    engine = create_engine(url)
    before = {}
    if existing:
        Base.metadata.create_all(engine)
        with Session(engine) as db:
            seed_database(db)
            sheet = m.TeacherSessionSheet(code='HISTORY', title='Histoire', level='4e'); db.add(sheet); db.flush()
            revision = m.TeacherSheetRevision(sheet_id=sheet.id, revision_number=1, identification_json='{"durée":"1 h 30"}', planning_json='{"original":true}', authoring_json='{"snapshot":"original"}')
            db.add(revision); db.flush()
            segment = m.SessionCurriculumSegment(teacher_revision_id=revision.id, instruction_id=3, position=1); db.add(segment); db.flush()
            for n, status in enumerate(['DONE', 'PARTIAL', 'SKIPPED'], 1):
                event = m.TeachingSession(teacher_revision_id=revision.id, taught_on='2025-01-01', class_label='Classe historique'); db.add(event); db.flush()
                db.add(m.ExecutedCurriculumSegment(teaching_session_id=event.id, session_curriculum_segment_id=segment.id, status=status, actual_minutes=n * 10, position=1))
            revision.status = 'FINALIZED'; db.commit()
        with engine.begin() as connection:
            connection.execute(text('DROP INDEX ix_teaching_sessions_planned_session_id'))
            connection.execute(text('CREATE TABLE teaching_sessions_0004 (id INTEGER PRIMARY KEY, teacher_revision_id INTEGER NOT NULL REFERENCES teacher_sheet_revisions(id), taught_on VARCHAR(10) NOT NULL, class_label VARCHAR(80) NOT NULL, notes TEXT NOT NULL)'))
            connection.execute(text('INSERT INTO teaching_sessions_0004 SELECT id, teacher_revision_id, taught_on, class_label, notes FROM teaching_sessions'))
            connection.execute(text('DROP TABLE teaching_sessions'))
            connection.execute(text('ALTER TABLE teaching_sessions_0004 RENAME TO teaching_sessions'))
            for table in ['planned_sessions', 'sequence_plans', 'class_contexts']:
                connection.execute(text(f'DROP TABLE {table}'))
            for table in ['teacher_session_sheets', 'teacher_sheet_revisions', 'teaching_sessions', 'executed_curriculum_segments', 'session_curriculum_segments', 'source_documents', 'curriculum_attributes']:
                before[table] = [tuple(r) for r in connection.execute(text(f'SELECT * FROM {table} ORDER BY id'))]
            connection.execute(text('CREATE TABLE alembic_version (version_num VARCHAR(32) PRIMARY KEY)'))
            connection.execute(text("INSERT INTO alembic_version VALUES ('0004_curriculum_authoring')"))
    result = subprocess.run([sys.executable, '-m', 'alembic', 'upgrade', '0005_planned_sessions'], cwd=Path(__file__).resolve().parents[1], env={**os.environ, 'DATABASE_URL': url}, capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
    with engine.connect() as connection:
        assert connection.execute(text('SELECT version_num FROM alembic_version')).scalar_one() == '0005_planned_sessions'
        assert connection.execute(text('SELECT count(*) FROM planned_sessions')).scalar_one() == 0
        assert not connection.execute(text('PRAGMA foreign_key_check')).all()
        assert any(r[2] == 'planned_sessions' for r in connection.execute(text('PRAGMA foreign_key_list(teaching_sessions)')))
        for table, rows in before.items():
            after = [tuple(r) for r in connection.execute(text(f'SELECT * FROM {table} ORDER BY id'))]
            if table == 'teaching_sessions':
                assert all(r[-1] is None for r in after)
                after = [r[:-1] for r in after]
            assert after == rows
    engine.dispose()
