"""P2 acceptance: real persistence, scoped choices, frozen exports and reference safety."""
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest
from sqlalchemy import create_engine, select, text
from sqlalchemy.orm import Session

from app import models as m
from app.competencies import install_catalog, suggest
from app.database import Base, SessionLocal
from app.exporter import teacher_tex, support_tex
from app.seed import seed_database


def compose(client):
    response = client.post('/api/authoring/compose', json=dict(programme_id=1, scope='SEQUENCE', scope_id=1, title='Séance P2', instruction_ids=[3, 4]))
    assert response.status_code == 201, response.text
    return response.json()


def choices(client, sheet, rows):
    return client.put(f"/api/competencies/sheets/{sheet['id']}", json={'selections': [{k: r[k] for k in ['competency_id', 'context_id', 'is_primary'] if k in r} for r in rows]})


def test_P2_T01_T02_T25_catalog_codes_and_double_seed(client):
    with SessionLocal() as db:
        before = [(c.id, c.canonical_code, c.canonical_label) for c in db.scalars(select(m.Competency))]
        install_catalog(db); install_catalog(db); db.commit()
        assert before == [(c.id, c.canonical_code, c.canonical_label) for c in db.scalars(select(m.Competency))]
        assert {c[1] for c in before} == {f'CT{i}' for i in range(1, 9)} | {f'CTD{i}' for i in range(1, 7)} | {f'CD{i}' for i in range(1, 4)}
        assert 'géométriques' in db.scalar(select(m.Competency).where(m.Competency.canonical_code == 'CD2')).canonical_label
        assert len(list(db.scalars(select(m.CompetencyContext)))) == 57
        assert all('Enoncé de la compétence' not in c.canonical_label for c in db.scalars(select(m.Competency)))


def test_P2_T03_T04_variants_are_separate(client):
    with SessionLocal() as db:
        contexts = list(db.scalars(select(m.CompetencyContext).where(m.CompetencyContext.code.in_(['P4-CD1', 'P6-CD1', 'P1-CD1']))))
        assert len({c.competency_id for c in contexts}) == 1
        assert len({c.class_level for c in contexts}) == 3
        contexts.sort(key=lambda c: ['P4-CD1', 'P6-CD1', 'P1-CD1'].index(c.code))
        assert 'langage du' in contexts[0].source_raw_label
        assert 'et du raisonnement' in contexts[2].source_raw_label
        assert 'au plus' in contexts[0].realization_context
        assert 'au moins' in contexts[2].realization_context
        assert contexts[0].source_raw_text != contexts[2].source_raw_text


def test_P2_T05_applicability_complete_path(client):
    sheet = compose(client)
    with SessionLocal() as db:
        revision = db.get(m.TeacherSheetRevision, sheet['id'])
        application = db.scalar(select(m.CompetencyApplicability).limit(1))
        application.instruction_id = 7
        db.flush()
        assert application.id not in {r['applicability_id'] for r in suggest(db, revision)}
        application.instruction_id = 3
        db.flush()
        assert application.id in {r['applicability_id'] for r in suggest(db, revision)}
        assert len(list(db.scalars(select(m.Competency)))) == 17
        other = m.ProgrammeVersion(code='OTHER', title='Other version', level='4e', status='INACTIVE')
        db.add(other); db.flush()
        application.programme_version_id = other.id
        db.flush()
        assert application.id not in {r['applicability_id'] for r in suggest(db, revision)}


def test_P2_T06_example_never_required(client):
    sheet = compose(client)
    assert {r['applicability_type'] for r in sheet['competency_selection']} == {'EXAMPLE_SELECTION'}
    assert {r['selection_origin'] for r in sheet['competency_selection']} == {'AUTO_SELECTED'}


def test_P2_T07_T08_contextual_subset(client):
    sheet = compose(client)
    assert {r['canonical_code'] for r in sheet['competency_selection']} == {'CD1', 'CD3', 'CTD2', 'CT1', 'CT6', 'CT8'}
    assert len(sheet['competency_selection']) < len(client.get('/api/competencies').json())
    assert all(r['source_page'] == '74' for r in sheet['competency_selection'])


def test_P2_T09_T10_teacher_choice_persisted(client):
    sheet = compose(client)
    catalog = client.get('/api/competencies').json()
    added = next(r for r in catalog if r['canonical_code'] == 'CT3')
    response = choices(client, sheet, [added])
    assert response.status_code == 200, response.text
    reread = client.get(f"/api/sheets/{sheet['id']}").json()
    assert len(reread['competency_selection']) == 1
    assert reread['competency_selection'][0]['canonical_code'] == 'CT3'
    assert reread['competency_selection'][0]['selection_origin'] == 'TEACHER_SELECTED'


def test_P2_T11_revision_and_catalog_changes_leave_finalized_snapshot(client):
    sheet = compose(client)
    client.post(f"/api/sheets/{sheet['id']}/finalize")
    frozen = client.get(f"/api/sheets/{sheet['id']}").json()
    new = client.post(f"/api/sheets/{sheet['id']}/new-revision").json()
    assert new['competency_selection'] == frozen['competency_selection']
    assert choices(client, new, []).status_code == 200
    assert choices(client, frozen, []).status_code == 409
    with SessionLocal() as db:
        ctx = db.get(m.CompetencyContext, frozen['competency_selection'][0]['context_id'])
        ctx.normalized_display_label = 'New display wording for future choices'
        db.commit()
    assert client.get(f"/api/sheets/{sheet['id']}").json() == frozen
    with SessionLocal() as db:
        row = db.scalar(select(m.TeacherSheetCompetencySelection).where(m.TeacherSheetCompetencySelection.teacher_revision_id == sheet['id']))
        row.snapshot_json = '{}'
        with pytest.raises(ValueError, match='immuable'): db.flush()


@pytest.mark.parametrize('count', [0, 2, 6], ids=['P2-T12-zero-CTD', 'P2-T13-two-CTD', 'P2-T13-six-manual-CTD'])
def test_cardinality_open(client, count):
    sheet = compose(client)
    rows = [r for r in client.get('/api/competencies').json() if r['competency_type'] == 'TRANSDISCIPLINARY'][:count]
    result = choices(client, sheet, rows)
    assert result.status_code == 200, result.text
    assert len(result.json()['competency_selection']) == count


@pytest.mark.parametrize('kind,cap', [('TRANSDISCIPLINARY', 1), ('TRANSVERSAL', 3), ('DISCIPLINARY', 2)], ids=['P2-T14', 'P2-T15', 'P2-T16'])
def test_automatic_bounds_even_when_all_are_applicable(client, kind, cap):
    with SessionLocal() as db:
        contexts = list(db.scalars(select(m.CompetencyContext).join(m.Competency).where(m.CompetencyContext.class_level == '4e', m.CompetencyContext.authority_class == 'OFFICIAL_PROGRAM', m.Competency.competency_type == kind)))
        for c in contexts:
            db.add(m.CompetencyApplicability(code='TEST-'+c.code, competency_context_id=c.id, class_level='4e', sequence_id=1, applicability_type='REQUIRED', source_document_id=c.source_document_id, source_version=c.curriculum_version))
        db.commit()
    sheet = compose(client)
    assert len([r for r in sheet['competency_selection'] if r['competency_type'] == kind]) == cap
    with SessionLocal() as db:
        assert suggest(db, instruction_ids=[]) == []


def test_P2_T17_CT8_anomaly_preserved(client):
    with SessionLocal() as db:
        ctx = db.scalar(select(m.CompetencyContext).where(m.CompetencyContext.code == 'P6-CT8'))
        assert 'troisième' in ctx.source_raw_text and 'troisième' in ctx.realization_context
        assert db.get(m.SourceIssue, ctx.source_issue_id).status == 'OPEN'
        assert 'sixième' not in ctx.realization_context


@pytest.mark.parametrize('level', ['6e', '1ère C'], ids=['P2-T18', 'P2-T19'])
def test_inactive_product_levels(client, level):
    assert {p['level'] for p in client.get('/api/authoring/curriculum').json()} == {'4e'}
    assert {c['class_level'] for c in client.get('/api/competencies').json()} == {'4e'}
    sheet = compose(client)
    with SessionLocal() as db:
        ctx = db.scalar(select(m.CompetencyContext).where(m.CompetencyContext.class_level == level))
        row = dict(competency_id=ctx.competency_id, context_id=ctx.id)
    assert choices(client, sheet, [row]).status_code == 422


def test_P2_T20_teacher_export_only_persisted_selection(client):
    sheet = compose(client)
    one = [r for r in sheet['competency_selection'] if r['canonical_code'] == 'CT6']
    updated = choices(client, sheet, one).json()
    tex = teacher_tex(updated)
    assert 'Travailler en coopération' in tex
    assert 'Communiquer de façon précise' not in tex
    assert 'Agir individuellement' not in tex
    empty = choices(client, updated, []).json()
    assert 'Travailler en coopération' not in teacher_tex(empty)


def test_P2_T21_learner_unchanged(client):
    sheet = compose(client)
    for kind, content in [('INSTRUCTION', 'Consigne visible'), ('PROPERTY', 'Propriété visible'), ('FIGURE', 'Figure visible'), ('EXPECTED_RESPONSE', 'Réponse privée')]:
        response = client.post(f"/api/sheets/{sheet['id']}/resources/local", json=dict(title=kind, block_type=kind, content_latex=content))
        assert response.status_code == 201
    learner = client.post(f"/api/authoring/sheets/{sheet['id']}/learner-support").json()
    blocks = [b for r in learner['resources'] for b in r['blocks']]
    assert {b['block_type'] for b in blocks} == {'INSTRUCTION', 'PROPERTY', 'FIGURE'}
    assert all('Réponse privée' not in b['content_latex'] for b in blocks)
    assert 'competency_selection' not in learner


@pytest.mark.parametrize('existing', [True, False], ids=['P2-T22-from-0005', 'P2-T23-empty'])
def test_migration_and_P2_T24_history(tmp_path, existing):
    url = 'sqlite:///' + (tmp_path / 'migration.db').as_posix()
    engine = create_engine(url)
    before = {}
    new_tables = ['teacher_sheet_competency_selections', 'competency_applicabilities', 'competency_contexts', 'competencies']
    if existing:
        Base.metadata.create_all(engine)
        with Session(engine) as db: seed_database(db)
        with engine.begin() as connection:
            for table in new_tables: connection.execute(text(f'DROP TABLE {table}'))
            names = [r[0] for r in connection.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"))]
            for table in names: before[table] = list(connection.execute(text(f'SELECT * FROM {table} ORDER BY id')))
            connection.execute(text('CREATE TABLE alembic_version(version_num VARCHAR(32) PRIMARY KEY)'))
            connection.execute(text("INSERT INTO alembic_version VALUES ('0005_planned_sessions')"))
    result = subprocess.run([sys.executable, '-m', 'alembic', 'upgrade', 'head'], cwd=Path(__file__).resolve().parents[1], env={**os.environ, 'DATABASE_URL': url, 'EXPORT_DIR': str(tmp_path / 'exports')}, capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
    with engine.connect() as connection:
        assert connection.execute(text('SELECT version_num FROM alembic_version')).scalar_one() == '0006_competency_catalog'
        assert not connection.execute(text('PRAGMA foreign_key_check')).all()
        for table in new_tables: assert connection.execute(text(f'SELECT count(*) FROM {table}')).scalar_one() == 0
        for table, rows in before.items(): assert rows == list(connection.execute(text(f'SELECT * FROM {table} ORDER BY id')))
    engine.dispose()


def test_P2_T26_legacy_ambiguous_unchanged(client):
    with SessionLocal() as db:
        legacy = [(r.id, r.planning_json, r.authoring_json) for r in db.scalars(select(m.TeacherSheetRevision))]
        attrs = [(r.id, r.code, r.value) for r in db.scalars(select(m.CurriculumAttribute))]
        install_catalog(db); db.commit()
        assert legacy == [(r.id, r.planning_json, r.authoring_json) for r in db.scalars(select(m.TeacherSheetRevision))]
        assert attrs == [(r.id, r.code, r.value) for r in db.scalars(select(m.CurriculumAttribute))]
    assert client.get('/api/sheets/1').json()['competency_selection'] is None


def test_P2_T27_provenance_available(client):
    sheet = compose(client)
    data = client.get(f"/api/competencies/sheets/{sheet['id']}").json()
    assert len(data['catalog']) == 17 and data['applicable'] and data['suggestions']
    for row in data['selected']:
        assert all(row[k] for k in ['source_document', 'source_version', 'source_page', 'source_raw_text', 'source_raw_label', 'curriculum_version', 'authority_class', 'source_status'])


def test_P2_T28_T29_deterministic_and_editable(client):
    a = compose(client); b = compose(client)
    assert a['competency_selection'] == b['competency_selection']
    assert a['status'] == 'DRAFT'
    assert all(r['selection_origin'] == 'AUTO_SELECTED' for r in a['competency_selection'])
    assert choices(client, a, []).status_code == 200


def test_P2_T30_protected_test_destinations():
    from app.config import settings
    root = Path(__file__).resolve().parents[2]
    assert str(root / 'data') not in settings.database_url
    assert not settings.export_dir.resolve().is_relative_to(root / 'exports')


def test_reference_drift_rejected_without_overwrite():
    with SessionLocal() as db:
        row = db.scalar(select(m.Competency))
        row.canonical_label = 'Existing alternate label'
        db.commit()
        with pytest.raises(ValueError, match='divergente'): install_catalog(db)
        assert row.canonical_label == 'Existing alternate label'


def test_forged_metadata_cannot_replace_selection(client):
    sheet = compose(client)
    plan = {**sheet['planning'], 'compétences disciplinaires': 'Forged value'}
    response = client.put(f"/api/sheets/{sheet['id']}/metadata", json=dict(identification=sheet['identification'], planning=plan, override_fields=['planning.compétences disciplinaires']))
    assert response.status_code == 422
    assert client.get(f"/api/sheets/{sheet['id']}").json()['competency_selection'] == sheet['competency_selection']
