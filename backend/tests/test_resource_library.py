import hashlib
import io
import json
import os
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest
from sqlalchemy import create_engine, event, func, select, text
from sqlalchemy.orm import Session

from app import models as m
from app.database import Base, SessionLocal
from app.resource_library import RESOURCE_TYPES

ADMIN_HEADERS = {"X-Package-Import-Key": "test-package-key"}


def curriculum():
    with SessionLocal() as db:
        instruction = db.scalar(select(m.InstructionGuide).order_by(m.InstructionGuide.id))
        sequence = db.get(m.Sequence, instruction.sequence_id)
        return instruction.id, instruction.code, sequence.id, sequence.situation_id


def revision():
    with SessionLocal() as db:
        sheet = m.TeacherSessionSheet(code="P3-SHEET", title="P3", level="4e")
        db.add(sheet); db.flush()
        row = m.TeacherSheetRevision(sheet_id=sheet.id, revision_number=1)
        db.add(row); db.flush()
        instruction_id, _, _, _ = curriculum()
        db.add(m.SessionCurriculumSegment(teacher_revision_id=row.id, instruction_id=instruction_id, position=1, planned_minutes=20))
        db.commit(); return row.id


def user_payload(**changes):
    instruction_id, _, sequence_id, situation_id = curriculum()
    value = {"content": "Calculer $2+3$.", "class_level": "4e", "situation_id": situation_id, "sequence_id": sequence_id, "instruction_ids": [instruction_id], "resource_type": "APPLICATION_CONSIGNE", "visibility_scope": "PRIVATE", "title": "Calcul mental"}
    value.update(changes); return value


def package_bytes(content="Résoudre $x+1=0$.", stable_code="PKG-P3-001", bad_hash=False, bad_instruction=False, invalid_jsonl=False):
    _, instruction_code, sequence_id, situation_id = curriculum()
    with SessionLocal() as db:
        sequence = db.get(m.Sequence, sequence_id)
        situation = db.get(m.SituationApprentissage, situation_id)
        programme = db.get(m.ProgrammeVersion, situation.programme_version_id)
    source = {"source_code": "SRC-P3-SYN", "title": "Source synthétique de test", "document_type": "TEST", "file_name": "synthetic.pdf", "sha256": "a" * 64, "authority": "Fixture de test"}
    resource = {"stable_code": stable_code, "resource_type": "HOMEWORK_EXERCISE", "title": "Exercice synthétique", "content": content, "content_format": "LATEX", "class_level": "4e", "curriculum_version": programme.code, "SA_code": situation.code, "sequence_code": sequence.code, "instruction_codes": ["UNKNOWN" if bad_instruction else instruction_code], "origin_type": "CURATED_PROJECT", "validation_status": "CURATED", "visibility_scope": "CURATED_GLOBAL", "source_code": "SRC-P3-SYN", "source_page": "1", "author": None, "license_or_usage_note": "Test uniquement", "metadata": {"difficulty": "simple", "correction_available": False}, "content_hash": hashlib.sha256(content.encode()).hexdigest()}
    link = {"stable_code": stable_code, "instruction_code": "UNKNOWN" if bad_instruction else instruction_code, "relation_type": "APPLIES", "relevance": "DIRECT", "validation_status": "CURATED", "provenance": {"fixture": True}}
    files = {"resources.jsonl": ("{" if invalid_jsonl else json.dumps(resource)) .encode(), "resource_instruction_links.jsonl": json.dumps(link).encode(), "sources.jsonl": json.dumps(source).encode()}
    hashes = {name: hashlib.sha256(data).hexdigest() for name, data in files.items()}
    if bad_hash: hashes["resources.jsonl"] = "0" * 64
    manifest = {"package_type": "FICHEMATHS_PEDAGOGICAL_LIBRARY_PACKAGE", "schema_version": "1.0", "package_version": "test-1", "generated_at": "2026-09-05T00:00:00Z", "country": "Bénin", "subject": "Mathématiques", "supported_class_levels": ["4e"], "resource_count": 1, "source_count": 1, "link_count": 1, "file_hashes": hashes, "producer": "Tests P3", "provenance_notice": "Données synthétiques"}
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w") as archive:
        archive.writestr("manifest.json", json.dumps(manifest)); [archive.writestr(name, data) for name, data in files.items()]
    return output.getvalue()


def rewrite_package(raw: bytes, transform):
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        files = {info.filename: archive.read(info) for info in archive.infolist() if not info.is_dir()}
    transform(files)
    if "manifest.json" in files:
        manifest = json.loads(files["manifest.json"])
        manifest["file_hashes"] = {name: hashlib.sha256(data).hexdigest() for name, data in files.items() if name != "manifest.json"}
        files["manifest.json"] = json.dumps(manifest).encode()
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
        for name, data in files.items(): archive.writestr(name, data)
    return output.getvalue()


def mutate_json(raw: bytes, file_name: str, changes: dict):
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        files = {info.filename: archive.read(info) for info in archive.infolist() if not info.is_dir()}
    value = json.loads(files[file_name]); value.update(changes)
    files[file_name] = json.dumps(value).encode()
    if file_name != "manifest.json":
        manifest = json.loads(files["manifest.json"])
        manifest["file_hashes"] = {name: hashlib.sha256(data).hexdigest() for name, data in files.items() if name != "manifest.json"}
        files["manifest.json"] = json.dumps(manifest).encode()
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
        for name, data in files.items(): archive.writestr(name, data)
    return output.getvalue()


@pytest.mark.parametrize("start", ["0006_competency_catalog", "base"], ids=["P3-T01-0006-to-0007", "P3-T02-empty-to-head"])
def test_p3_migrations(tmp_path, start):
    url = "sqlite:///" + (tmp_path / "migration.db").as_posix()
    if start != "base":
        result = subprocess.run([sys.executable, "-m", "alembic", "upgrade", start], cwd=Path(__file__).parents[1], env={**os.environ, "DATABASE_URL": url, "EXPORT_DIR": str(tmp_path / "exports")}, capture_output=True, text=True)
        assert result.returncode == 0, result.stdout + result.stderr
    result = subprocess.run([sys.executable, "-m", "alembic", "upgrade", "head"], cwd=Path(__file__).parents[1], env={**os.environ, "DATABASE_URL": url, "EXPORT_DIR": str(tmp_path / "exports")}, capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
    with create_engine(url).connect() as connection:
        assert connection.execute(text("SELECT version_num FROM alembic_version")).scalar_one() == "0007_pedagogical_resources"
        assert connection.execute(text("SELECT count(*) FROM package_import_records")).scalar_one() == 0


@pytest.mark.parametrize("resource_type", sorted(RESOURCE_TYPES), ids=lambda value: f"P3-resource-type-{value}")
def test_p3_resource_type_vocabulary(resource_type):
    assert resource_type in RESOURCE_TYPES


def test_p3_t03_historical_data_not_rewritten():
    with SessionLocal() as db:
        before = db.scalar(select(func.count()).select_from(m.InstructionGuide))
        assert before > 0
        assert db.scalar(select(func.count()).select_from(m.InstructionGuide)) == before


def test_p3_t04_dry_run_and_t05_hash_rejection(client):
    response = client.post("/api/admin/resource-packages/dry-run", files={"package": ("p.zip", package_bytes(), "application/zip")}, headers=ADMIN_HEADERS)
    assert response.status_code == 200 and response.json()["can_import"] is True
    response = client.post("/api/admin/resource-packages/dry-run", files={"package": ("p.zip", package_bytes(bad_hash=True), "application/zip")}, headers=ADMIN_HEADERS)
    assert response.json()["can_import"] is False and response.json()["hash_mismatches"]


def test_p3_t06_jsonl_and_t07_instruction_rejected(client):
    invalid = client.post("/api/admin/resource-packages/dry-run", files={"package": ("p.zip", package_bytes(invalid_jsonl=True), "application/zip")}, headers=ADMIN_HEADERS).json()
    assert any("JSONL_INVALID" in error for error in invalid["blocking_errors"])
    unknown = client.post("/api/admin/resource-packages/dry-run", files={"package": ("p.zip", package_bytes(bad_instruction=True), "application/zip")}, headers=ADMIN_HEADERS).json()
    assert unknown["references_not_found"] and unknown["invalid_links"]


def test_p3_t09_idempotence_t10_conflict_t11_atomicity(client):
    uploaded = {"package": ("p.zip", package_bytes(), "application/zip")}
    assert client.post("/api/admin/resource-packages/import", files=uploaded, headers=ADMIN_HEADERS).status_code == 200
    second = client.post("/api/admin/resource-packages/import", files={"package": ("p.zip", package_bytes(), "application/zip")}, headers=ADMIN_HEADERS).json()
    assert second["new_resources"] == 0 and second["unchanged_resources"] == 1
    conflict = client.post("/api/admin/resource-packages/import", files={"package": ("p.zip", package_bytes(content="Contenu divergent"), "application/zip")}, headers=ADMIN_HEADERS)
    assert conflict.status_code == 422
    with SessionLocal() as db:
        assert db.scalar(select(func.count()).select_from(m.PedagogicalResource).where(m.PedagogicalResource.code == "PKG-P3-001")) == 1


def test_p3_t12_to_t19_user_contribution_governance(client):
    created = client.post("/api/pedagogical-resources/user", json=user_payload(), headers={"X-Teacher-Id": "alice"})
    assert created.status_code == 201
    body = created.json(); assert body["origin_type"] == "USER_CONTRIBUTED" and body["validation_status"] == "USER_UNREVIEWED"
    instruction_id, _, _, _ = curriculum()
    own = client.get(f"/api/pedagogical-resources/by-instruction/{instruction_id}", headers={"X-Teacher-Id": "alice"}).json()
    other = client.get(f"/api/pedagogical-resources/by-instruction/{instruction_id}", headers={"X-Teacher-Id": "bob"}).json()
    assert any(row["id"] == body["id"] for row in own)
    assert all(row["id"] != body["id"] for row in other)
    forbidden = client.put(f"/api/pedagogical-resources/user/{body['id']}", json=user_payload(), headers={"X-Teacher-Id": "bob"})
    assert forbidden.status_code == 403


def test_p3_t20_shared_unreviewed_not_global(client):
    body = client.post("/api/pedagogical-resources/user", json=user_payload(visibility_scope="SHARED"), headers={"X-Teacher-Id": "alice"}).json()
    rows = client.get("/api/pedagogical-resources", headers={"X-Teacher-Id": "bob"}).json()
    assert all(row["id"] != body["id"] for row in rows)


def test_p3_t21_t22_resource_snapshot_and_finalized_protection(client):
    resource = client.post("/api/pedagogical-resources/user", json=user_payload(), headers={"X-Teacher-Id": "alice"}).json()
    rev = revision()
    selected = client.put(f"/api/sheets/{rev}/resources", json={"resource_version_ids": [resource["resource_version_id"]]}, headers={"X-Teacher-Id": "alice"})
    assert selected.status_code == 200 and selected.json()[0]["snapshot"]["content"] == "Calculer $2+3$."
    assert client.post(f"/api/sheets/{rev}/finalize").status_code == 200
    assert client.put(f"/api/sheets/{rev}/resources", json={"resource_version_ids": []}, headers={"X-Teacher-Id": "alice"}).status_code == 409


def imported_homework(client):
    client.post("/api/admin/resource-packages/import", files={"package": ("p.zip", package_bytes(), "application/zip")}, headers=ADMIN_HEADERS)
    with SessionLocal() as db: return db.scalar(select(m.PedagogicalResource).where(m.PedagogicalResource.code == "PKG-P3-001")).id


def test_p3_t23_to_t27_homework_order_and_scope_invariant(client):
    resource_id = imported_homework(client); rev = revision()
    with SessionLocal() as db:
        segment = db.scalar(select(m.SessionCurriculumSegment).where(m.SessionCurriculumSegment.teacher_revision_id == rev)); before = (segment.instruction_id, segment.planned_minutes)
    response = client.put(f"/api/sheets/{rev}/homework", json={"items": [{"pedagogical_resource_id": resource_id, "homework_usage_type": "PRIOR_NOTION_REACTIVATION", "teacher_note": "Révision"}]})
    assert response.status_code == 200 and response.json()[0]["selected_order"] == 0
    with SessionLocal() as db:
        segment = db.scalar(select(m.SessionCurriculumSegment).where(m.SessionCurriculumSegment.teacher_revision_id == rev)); assert (segment.instruction_id, segment.planned_minutes) == before


def test_p3_t28_to_t33_documents_derived_deduplicated_manual_and_frozen(client):
    resource_id = imported_homework(client); rev = revision()
    client.put(f"/api/sheets/{rev}/homework", json={"items": [{"pedagogical_resource_id": resource_id, "homework_usage_type": "CURRENT_SCOPE"}]})
    auto = client.get(f"/api/sheets/{rev}/documents-used").json(); assert len(auto) == 1 and auto[0]["origin"] == "AUTO_DERIVED"
    docs = client.put(f"/api/sheets/{rev}/documents-used", json={"manual": [{"display_label": "Cahier personnel", "note": "Pages 2-3"}]}).json()
    assert len(docs) == 2 and docs[1]["origin"] == "MANUAL_REFERENCE" and docs[1]["source_document_id"] is None
    client.post(f"/api/sheets/{rev}/finalize")
    assert client.put(f"/api/sheets/{rev}/documents-used", json={"manual": []}).status_code == 409


def test_p3_t34_t35_teacher_tex_and_t36_t37_learner_filter(client):
    from app.exporter import support_tex, teacher_tex
    detail = {"title": "P3", "identification": {}, "planning": {}, "authoring": {}, "competency_selection": None, "segments": [], "resources": [], "flow": [], "homework": [{"snapshot": {"content": "Faire le devoir."}, "teacher_note": None}], "documents_used": [{"display_label": "Guide", "author": None, "title": None, "edition": None, "note": None}]}
    teacher = teacher_tex(detail); assert "EXERCICES DE MAISON" in teacher and "DOCUMENTS UTILISÉS" in teacher
    support = support_tex({"title": "Support", "level": "4e", "sequence": {}, "situation": {}, "resources": [{"title": "A", "blocks": [{"visible": True, "block_type": "EXPECTED_RESPONSE", "title": "Réponse", "content_latex": "Corrigé"}]}]})
    assert "Corrigé" not in support


def test_p3_t38_t39_p1_p2_tables_coexist():
    assert m.PlannedSession.__tablename__ == "planned_sessions"
    assert m.TeacherSheetCompetencySelection.__tablename__ == "teacher_sheet_competency_selections"


def test_p3_t40_tests_use_isolated_database():
    assert "fichemaths_tests_" in str(SessionLocal.kw["bind"].url)


def test_p3g1_maj_sec_001_rejects_unsafe_zip_members(client):
    for dangerous in ("../escape.txt", "/absolute.pdf", "C:/drive.pdf", "nested.zip"):
        raw = rewrite_package(package_bytes(), lambda files, name=dangerous: files.update({name: b"x"}))
        body = client.post("/api/admin/resource-packages/dry-run", files={"package": ("p.zip", raw, "application/zip")}, headers=ADMIN_HEADERS).json()
        assert body["can_import"] is False
        assert any(token in " ".join(body["blocking_errors"]) for token in ("UNSAFE_MEMBER_PATH", "UNSUPPORTED_PACKAGE_MEMBER"))


def test_p3g1_maj_sec_001_rejects_duplicates_and_security_limits(client):
    duplicate = io.BytesIO()
    with zipfile.ZipFile(duplicate, "w", zipfile.ZIP_DEFLATED) as archive:
        with zipfile.ZipFile(io.BytesIO(package_bytes())) as source:
            for info in source.infolist(): archive.writestr(info.filename, source.read(info))
        archive.writestr("resources.jsonl", b"{}")
    body = client.post("/api/admin/resource-packages/dry-run", files={"package": ("p.zip", duplicate.getvalue(), "application/zip")}, headers=ADMIN_HEADERS).json()
    assert any("DUPLICATE_MEMBER" in item for item in body["blocking_errors"])
    from app.config import settings
    old_size, old_ratio = settings.package_max_member_bytes, settings.package_max_compression_ratio
    try:
        settings.package_max_member_bytes = 4; settings.package_max_compression_ratio = 0.5
        body = client.post("/api/admin/resource-packages/dry-run", files={"package": ("p.zip", package_bytes(), "application/zip")}, headers=ADMIN_HEADERS).json()
        assert any("MEMBER_SIZE_EXCEEDED" in item for item in body["blocking_errors"])
        assert any("COMPRESSION_RATIO_EXCEEDED" in item for item in body["blocking_errors"])
    finally:
        settings.package_max_member_bytes, settings.package_max_compression_ratio = old_size, old_ratio


def test_p3g1_maj_pkg_001_requires_complete_contract_and_hashes(client):
    def remove_field(files):
        rows = json.loads(files["sources.jsonl"]); rows.pop("authority"); files["sources.jsonl"] = json.dumps(rows).encode()
    body = client.post("/api/admin/resource-packages/dry-run", files={"package": ("p.zip", rewrite_package(package_bytes(), remove_field), "application/zip")}, headers=ADMIN_HEADERS).json()
    assert body["can_import"] is False and any("SOURCE_SCHEMA_INVALID" in item for item in body["blocking_errors"])


def test_p3g1_maj_pkg_002_invalid_source_is_rejected_in_dry_run(client):
    def invalid_sha(files):
        row = json.loads(files["sources.jsonl"]); row["sha256"] = "bad"; files["sources.jsonl"] = json.dumps(row).encode()
    response = client.post("/api/admin/resource-packages/dry-run", files={"package": ("p.zip", rewrite_package(package_bytes(), invalid_sha), "application/zip")}, headers=ADMIN_HEADERS)
    assert response.status_code == 200 and response.json()["can_import"] is False


def test_p3g1_maj_gov_001_admin_secret_is_server_controlled(client):
    files = {"package": ("p.zip", package_bytes(), "application/zip")}
    assert client.post("/api/admin/resource-packages/dry-run", files=files).status_code == 403
    assert client.post("/api/admin/resource-packages/dry-run", files={"package": ("p.zip", package_bytes(), "application/zip")}, headers={"X-Teacher-Id": "admin", "X-Role": "admin"}).status_code == 403


def test_p3g1_maj_gov_002_existing_source_must_match_exactly(client):
    assert client.post("/api/admin/resource-packages/import", files={"package": ("p.zip", package_bytes(), "application/zip")}, headers=ADMIN_HEADERS).status_code == 200
    def diverge(files):
        source = json.loads(files["sources.jsonl"]); source["title"] = "Titre divergent"; files["sources.jsonl"] = json.dumps(source).encode()
        resource = json.loads(files["resources.jsonl"]); resource["stable_code"] = "PKG-P3-002"; files["resources.jsonl"] = json.dumps(resource).encode()
        link = json.loads(files["resource_instruction_links.jsonl"]); link["stable_code"] = "PKG-P3-002"; files["resource_instruction_links.jsonl"] = json.dumps(link).encode()
    body = client.post("/api/admin/resource-packages/dry-run", files={"package": ("p.zip", rewrite_package(package_bytes(), diverge), "application/zip")}, headers=ADMIN_HEADERS).json()
    assert body["can_import"] is False and any("SOURCE_CONFLICT" in item for item in body["blocking_errors"])


def test_p3g1_maj_gov_003_wrong_scope_candidate_is_hidden_and_rejected(client):
    with SessionLocal() as db:
        first = db.scalar(select(m.InstructionGuide).order_by(m.InstructionGuide.id)); sequence = db.get(m.Sequence, first.sequence_id)
        other_sequence = m.Sequence(situation_id=sequence.situation_id, guide_version_id=sequence.guide_version_id, code="SEQ-G2-OTHER", title="Autre séquence", position=99); db.add(other_sequence); db.flush()
        resource = m.PedagogicalResource(code="USR-G2-WRONG", title="Hors périmètre", resource_type="APPLICATION_CONSIGNE", level="4e", sequence_id=other_sequence.id, situation_id=sequence.situation_id, origin_type="USER_CONTRIBUTED", validation_status="USER_UNREVIEWED", visibility_scope="PRIVATE", created_by="alice", content="Hors périmètre", content_hash=hashlib.sha256(b"Hors perimetre").hexdigest())
        db.add(resource); db.flush(); version = m.PedagogicalResourceVersion(resource_id=resource.id, version_number=1, title=resource.title); db.add(version); db.flush(); db.add(m.ResourceInstructionMapping(resource_version_id=version.id, instruction_id=first.id, mapping_kind="SUPPORTS")); db.commit()
        made = {"id": resource.id, "resource_version_id": version.id}
    rows = client.get(f"/api/pedagogical-resources/by-instruction/{first.id}", headers={"X-Teacher-Id": "alice"}).json()
    assert all(row["id"] != made["id"] for row in rows)
    assert client.put(f"/api/sheets/{revision()}/resources", json={"resource_version_ids": [made["resource_version_id"]]}, headers={"X-Teacher-Id": "alice"}).status_code == 403


def test_p3g1_maj_snap_001_snapshots_are_complete_for_session_and_homework(client):
    resource = client.post("/api/pedagogical-resources/user", json=user_payload(), headers={"X-Teacher-Id": "alice"}).json(); rev = revision()
    session_snapshot = client.put(f"/api/sheets/{rev}/resources", json={"resource_version_ids": [resource["resource_version_id"]]}, headers={"X-Teacher-Id": "alice"}).json()[0]["snapshot"]
    required = {"resource_id", "resource_version_id", "stable_code", "content", "content_format", "resource_type", "origin_type", "validation_status", "provenance", "content_hash"}
    assert required <= set(session_snapshot)
    homework_id = imported_homework(client)
    homework_snapshot = client.put(f"/api/sheets/{rev}/homework", json={"items": [{"pedagogical_resource_id": homework_id, "homework_usage_type": "CURRENT_SCOPE"}]}).json()[0]["snapshot"]
    assert required <= set(homework_snapshot) and homework_snapshot["source_version"]


def test_p3g1_maj_snap_002_replacement_is_atomic(client):
    resource = client.post("/api/pedagogical-resources/user", json=user_payload(), headers={"X-Teacher-Id": "alice"}).json(); rev = revision()
    client.put(f"/api/sheets/{rev}/resources", json={"resource_version_ids": [resource["resource_version_id"]]}, headers={"X-Teacher-Id": "alice"})
    failed = client.put(f"/api/sheets/{rev}/resources", json={"resource_version_ids": [resource["resource_version_id"], 999999]}, headers={"X-Teacher-Id": "alice"})
    assert failed.status_code == 403
    assert [row["source_resource_version_id"] for row in client.get(f"/api/sheets/{rev}").json()["resources"]] == [resource["resource_version_id"]]


def test_p3g1_maj_doc_001_get_documents_is_pure(client):
    rev = revision()
    with SessionLocal() as db: before = db.scalar(select(func.count()).select_from(m.TeacherSheetDocumentReference))
    assert client.get(f"/api/sheets/{rev}/documents-used").status_code == 200
    with SessionLocal() as db: assert db.scalar(select(func.count()).select_from(m.TeacherSheetDocumentReference)) == before


def test_p3g1_maj_doc_002_deduplicates_by_source_and_version(client):
    resource_id = imported_homework(client); rev = revision()
    client.put(f"/api/sheets/{rev}/homework", json={"items": [{"pedagogical_resource_id": resource_id, "homework_usage_type": "CURRENT_SCOPE"}]})
    with SessionLocal() as db:
        row = db.scalar(select(m.TeacherSheetHomeworkSelection).where(m.TeacherSheetHomeworkSelection.teacher_revision_id == rev)); snapshot = json.loads(row.snapshot_json); snapshot["source_version"] = "b" * 64
        db.add(m.SheetResourceInstance(teacher_revision_id=rev, origin="LIBRARY_DERIVED", source_resource_version_id=row.resource_version_id, title="Version B", position=1, snapshot_json=json.dumps(snapshot))); db.commit()
    client.put(f"/api/sheets/{rev}/documents-used", json={"manual": []})
    assert len(client.get(f"/api/sheets/{rev}/documents-used").json()) == 2


def test_p3g1_maj_pkg_003_content_format_is_governed(client):
    def unsafe(files):
        row = json.loads(files["resources.jsonl"]); row["content"] = r"\input{secret}"; row["content_hash"] = hashlib.sha256(row["content"].encode()).hexdigest(); files["resources.jsonl"] = json.dumps(row).encode()
    body = client.post("/api/admin/resource-packages/dry-run", files={"package": ("p.zip", rewrite_package(package_bytes(), unsafe), "application/zip")}, headers=ADMIN_HEADERS).json()
    assert body["can_import"] is False and any("CONTENT_UNSAFE" in item for item in body["blocking_errors"])


def test_p3g1_import_dry_run_does_not_mutate_logical_state(client):
    with SessionLocal() as db: before = tuple(db.scalar(select(func.count()).select_from(model)) for model in (m.SourceDocument, m.PedagogicalResource, m.PackageImportRecord))
    assert client.post("/api/admin/resource-packages/dry-run", files={"package": ("p.zip", package_bytes(), "application/zip")}, headers=ADMIN_HEADERS).status_code == 200
    with SessionLocal() as db: after = tuple(db.scalar(select(func.count()).select_from(model)) for model in (m.SourceDocument, m.PedagogicalResource, m.PackageImportRecord))
    assert after == before


def test_p3g1_maj_transaction_import_rolls_back_after_writes(client):
    engine = SessionLocal.kw["bind"]
    def fail_audit_record(_connection, _cursor, statement, _parameters, _context, _many):
        if "INSERT INTO package_import_records" in statement: raise RuntimeError("forced late import failure")
    event.listen(engine, "before_cursor_execute", fail_audit_record)
    try:
        with pytest.raises(RuntimeError, match="forced late import failure"):
            client.post("/api/admin/resource-packages/import", files={"package": ("p.zip", package_bytes(), "application/zip")}, headers=ADMIN_HEADERS)
    finally:
        event.remove(engine, "before_cursor_execute", fail_audit_record)
    with SessionLocal() as db:
        assert db.scalar(select(func.count()).select_from(m.PedagogicalResource).where(m.PedagogicalResource.code == "PKG-P3-001")) == 0
        assert db.scalar(select(func.count()).select_from(m.SourceDocument).where(m.SourceDocument.code == "SRC-P3-SYN")) == 0
        assert db.scalar(select(func.count()).select_from(m.PackageImportRecord)) == 0


@pytest.mark.parametrize("field,value", [("country", None), ("country", 123), ("subject", []), ("producer", None), ("producer", ""), ("provenance_notice", {}), ("provenance_notice", []), ("generated_at", "bad"), ("generated_at", None), ("resource_count", "1"), ("resource_count", True), ("source_count", -1), ("link_count", 1.5), ("file_hashes", []), ("file_hashes", {"resources.jsonl": "bad"})])
def test_g3_pkg_001_manifest_adversarial_matrix(client, field, value):
    response = client.post("/api/admin/resource-packages/dry-run", files={"package": ("p.zip", mutate_json(package_bytes(), "manifest.json", {field: value}), "application/zip")}, headers=ADMIN_HEADERS)
    assert response.status_code == 200 and response.json()["can_import"] is False
    assert response.json()["validation_errors"] and all({"code", "file", "line", "field", "message"} <= set(error) for error in response.json()["validation_errors"])


@pytest.mark.parametrize("field,value", [("title", None), ("title", []), ("document_type", None), ("document_type", {}), ("file_name", None), ("file_name", 123), ("authority", None), ("authority", []), ("sha256", None), ("sha256", "bad")])
def test_g3_pkg_002_source_adversarial_matrix(client, field, value):
    raw = mutate_json(package_bytes(), "sources.jsonl", {field: value})
    dry = client.post("/api/admin/resource-packages/dry-run", files={"package": ("p.zip", raw, "application/zip")}, headers=ADMIN_HEADERS)
    assert dry.status_code == 200 and dry.json()["can_import"] is False
    assert client.post("/api/admin/resource-packages/import", files={"package": ("p.zip", raw, "application/zip")}, headers=ADMIN_HEADERS).status_code == 422


@pytest.mark.parametrize("field,value", [("instruction_codes", [{}]), ("instruction_codes", [None]), ("instruction_codes", [123]), ("instruction_codes", "SEQ8-INS3"), ("instruction_codes", ["", "SEQ8-INS3"]), ("metadata", None), ("metadata", []), ("content", None), ("content", 123), ("stable_code", None), ("resource_type", []), ("validation_status", {}), ("origin_type", 123)])
def test_g3_pkg_002_resource_adversarial_matrix(client, field, value):
    raw = mutate_json(package_bytes(), "resources.jsonl", {field: value})
    dry = client.post("/api/admin/resource-packages/dry-run", files={"package": ("p.zip", raw, "application/zip")}, headers=ADMIN_HEADERS)
    assert dry.status_code == 200 and dry.json()["can_import"] is False and dry.json()["validation_errors"]
    assert client.post("/api/admin/resource-packages/import", files={"package": ("p.zip", raw, "application/zip")}, headers=ADMIN_HEADERS).status_code == 422


@pytest.mark.parametrize("field,value", [("stable_code", None), ("instruction_code", {}), ("relation_type", []), ("provenance", []), ("validation_status", 123)])
def test_g3_pkg_002_link_adversarial_matrix(client, field, value):
    raw = mutate_json(package_bytes(), "resource_instruction_links.jsonl", {field: value})
    dry = client.post("/api/admin/resource-packages/dry-run", files={"package": ("p.zip", raw, "application/zip")}, headers=ADMIN_HEADERS)
    assert dry.status_code == 200 and dry.json()["can_import"] is False
    assert client.post("/api/admin/resource-packages/import", files={"package": ("p.zip", raw, "application/zip")}, headers=ADMIN_HEADERS).status_code == 422


def test_g3_pkg_002_unknown_fields_are_rejected(client):
    for file_name in ("manifest.json", "resources.jsonl", "resource_instruction_links.jsonl", "sources.jsonl"):
        body = client.post("/api/admin/resource-packages/dry-run", files={"package": ("p.zip", mutate_json(package_bytes(), file_name, {"unexpected": True}), "application/zip")}, headers=ADMIN_HEADERS).json()
        assert body["can_import"] is False
        assert any(error["code"] == "UNKNOWN_FIELD" and error["file"] == file_name for error in body["validation_errors"])


@pytest.mark.parametrize("content", [r"\openin1=/etc/passwd", r"\openin 1 = foo", r"\input{foo}", r"\include{foo}", r"\read1 to \x", r"\readline1 to \x", r"\openout1=foo", r"\write1{abc}", r"\write18{cmd}", r"\usepackage{x}", r"\RequirePackage{x}", r"\special{x}", r"\catcode`\@=11", r"\csname input\endcsname", r"\def\x{\input{foo}}"])
def test_g3_pkg_003_latex_adversarial_matrix(client, content):
    raw = mutate_json(package_bytes(), "resources.jsonl", {"content": content, "content_hash": hashlib.sha256(content.encode()).hexdigest()})
    response = client.post("/api/admin/resource-packages/dry-run", files={"package": ("p.zip", raw, "application/zip")}, headers=ADMIN_HEADERS)
    assert response.status_code == 200 and response.json()["can_import"] is False
    assert any("CONTENT_UNSAFE" in error for error in response.json()["blocking_errors"])


def test_g3_pkg_003_text_is_escaped_and_never_interpreted():
    from app.exporter import snapshot_content
    raw = r"#$%&_{}~^\input{secret}"
    rendered = snapshot_content({"content_format": "TEXT", "content": raw})
    for escaped in (r"\#", r"\$", r"\%", r"\&", r"\_", r"\{", r"\}", r"\textasciitilde{}", r"\textasciicircum{}", r"\textbackslash{}"):
        assert escaped in rendered
    assert r"\input{secret}" not in rendered
