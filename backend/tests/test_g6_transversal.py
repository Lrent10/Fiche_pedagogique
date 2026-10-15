import json
import os
import shutil
import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest
from sqlalchemy import select

from app import models as m
from app.database import SessionLocal
from app.exporter import teacher_tex
from test_resource_library import ADMIN_HEADERS, curriculum, package_bytes, revision, user_payload


AUTHORIZED_SHA = "aa20e7d246ee5735c5ee4b41e01efd74c8cbf0d5"
P3_TABLES = (
    "pedagogical_resources",
    "resource_instruction_mappings",
    "sheet_resource_instances",
    "teacher_sheet_homework_selections",
    "teacher_sheet_document_references",
    "package_import_records",
)


def _sheet(client, instruction_ids):
    response = client.post(
        "/api/sheets",
        json={"title": "G6", "instruction_ids": instruction_ids, "duration_minutes": 20},
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


def _authoring_sheet(client, instruction_ids, automatic=False, headers=None):
    with SessionLocal() as db:
        instruction = db.get(m.InstructionGuide, instruction_ids[0])
        sequence = db.get(m.Sequence, instruction.sequence_id)
        situation = db.get(m.SituationApprentissage, sequence.situation_id)
    response = client.post(
        "/api/authoring/compose",
        headers=headers or {},
        json={
            "programme_id": situation.programme_version_id,
            "scope": "SEQUENCE",
            "scope_id": sequence.id,
            "title": "G6 authoring",
            "instruction_ids": instruction_ids,
            "automatic": automatic,
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def _resource(db, code, source_code, instruction_ids, *, source_kind="BOOK_SOURCE", priority_status="COMMUNITY"):
    source = m.SourceDocument(
        code=source_code,
        title=f"Source {source_code}",
        document_type="TEST",
        file_name=f"{source_code}.pdf",
        sha256=("a" if source_code.endswith("A") else "b") * 64,
        authority="Fixture G6",
    )
    db.add(source)
    db.flush()
    instruction = db.get(m.InstructionGuide, instruction_ids[0])
    sequence = db.get(m.Sequence, instruction.sequence_id)
    situation = db.get(m.SituationApprentissage, sequence.situation_id)
    resource = m.PedagogicalResource(
        code=code,
        title=code,
        resource_type="ACTIVITY",
        level="4e",
        content=f"Contenu {code}",
        programme_version_id=situation.programme_version_id,
        situation_id=situation.id,
        sequence_id=sequence.id,
        primary_instruction_id=instruction.id,
        source_document_id=source.id,
        origin_type="CURATED_PROJECT",
        validation_status="CURATED",
        visibility_scope="CURATED_GLOBAL",
        content_hash=("c" if code.endswith("A") else "d") * 64,
    )
    db.add(resource)
    db.flush()
    provenance = {
        "source_kind": source_kind,
        "source_ref": source.title,
        "source_version": source.sha256,
        "validation_status": priority_status,
    }
    version = m.PedagogicalResourceVersion(
        resource_id=resource.id,
        version_number=1,
        title=resource.title,
        provenance_json=json.dumps(provenance),
    )
    db.add(version)
    db.flush()
    db.add(
        m.PedagogicalBlock(
            resource_version_id=version.id,
            block_type="CONSIGNE",
            title=resource.title,
            content_latex=resource.content,
            position=1,
        )
    )
    for instruction_id in instruction_ids:
        db.add(
            m.ResourceInstructionMapping(
                resource_version_id=version.id,
                instruction_id=instruction_id,
                mapping_kind="SUPPORTS",
                validation_status="CURATED",
            )
        )
    db.flush()
    return resource, version


def test_g6_governance_is_common_across_legacy_and_p3_routes(client):
    instruction_id, _, _, _ = curriculum()
    private = client.post(
        "/api/pedagogical-resources/user",
        headers={"X-Teacher-Id": "alice"},
        json=user_payload(visibility_scope="PRIVATE"),
    )
    assert private.status_code == 201
    resource_id = private.json()["id"]
    version_id = private.json()["resource_version_id"]

    for path, identity, expected in (
        (f"/api/pedagogical-resources/by-instruction/{instruction_id}", "alice", True),
        (f"/api/pedagogical-resources/by-instruction/{instruction_id}", "bob", False),
        (f"/api/resources?instruction_id={instruction_id}", "alice", True),
        (f"/api/resources?instruction_id={instruction_id}", "bob", False),
        (f"/api/authoring/instructions/{instruction_id}/candidates", "alice", True),
        (f"/api/authoring/instructions/{instruction_id}/candidates", "bob", False),
    ):
        rows = client.get(path, headers={"X-Teacher-Id": identity})
        assert rows.status_code == 200, rows.text
        assert (version_id in {row.get("id") if path.startswith("/api/resources") or "/authoring/" in path else row.get("resource_version_id") for row in rows.json()}) is expected

    bob_p3 = client.put(
        f"/api/sheets/{_sheet(client, [instruction_id])}/resources",
        headers={"X-Teacher-Id": "bob"},
        json={"resource_version_ids": [version_id]},
    )
    bob_legacy = client.post(
        f"/api/sheets/{_sheet(client, [instruction_id])}/resources/library",
        headers={"X-Teacher-Id": "bob"},
        json={"resource_version_id": version_id},
    )
    assert bob_p3.status_code == 403
    assert bob_legacy.status_code == 403

    owner_revision = _sheet(client, [instruction_id])
    owner_legacy = client.post(
        f"/api/sheets/{owner_revision}/resources/library",
        headers={"X-Teacher-Id": "alice"},
        json={"resource_version_id": version_id},
    )
    assert owner_legacy.status_code == 201
    assert client.post(f"/api/sheets/{owner_revision}/finalize").status_code == 200

    with SessionLocal() as db:
        resource = db.get(m.PedagogicalResource, resource_id)
        resource.validation_status = "REJECTED"
        resource.active = False
        db.commit()
    assert client.get(f"/api/sheets/{owner_revision}").json()["resources"]


@pytest.mark.parametrize("validation_status,active", [("REJECTED", True), ("ARCHIVED", True), ("CURATED", False)])
def test_g6_withdrawn_resources_are_hidden_and_refused_everywhere(client, validation_status, active):
    instruction_id, _, _, _ = curriculum()
    with SessionLocal() as db:
        resource, version = _resource(db, f"G6-{validation_status}-{active}", f"G6-SRC-{validation_status}{active}", [instruction_id])
        resource.validation_status = validation_status
        resource.active = active
        db.commit()
        version_id = version.id

    paths = (
        f"/api/pedagogical-resources/by-instruction/{instruction_id}",
        f"/api/resources?instruction_id={instruction_id}",
        f"/api/authoring/instructions/{instruction_id}/candidates",
    )
    for path in paths:
        response = client.get(path)
        assert response.status_code == 200
        assert version_id not in {
            row.get("resource_version_id") if path.startswith("/api/pedagogical") else row.get("id")
            for row in response.json()
        }
    assert client.post(
        f"/api/sheets/{_sheet(client, [instruction_id])}/resources/library",
        json={"resource_version_id": version_id},
    ).status_code == 403
    assert client.put(
        f"/api/sheets/{_sheet(client, [instruction_id])}/resources",
        json={"resource_version_ids": [version_id]},
    ).status_code == 403


def test_g6_valid_package_integrates_with_authoring_without_invented_provenance(client):
    instruction_id, _, sequence_id, _ = curriculum()
    dry = client.post(
        "/api/admin/resource-packages/dry-run",
        headers=ADMIN_HEADERS,
        files={"package": ("g6.zip", package_bytes(), "application/zip")},
    )
    imported = client.post(
        "/api/admin/resource-packages/import",
        headers=ADMIN_HEADERS,
        files={"package": ("g6.zip", package_bytes(), "application/zip")},
    )
    assert dry.status_code == 200 and dry.json()["can_import"] is True
    assert imported.status_code == 200

    candidates = client.get(f"/api/authoring/instructions/{instruction_id}/candidates")
    assert candidates.status_code == 200, candidates.text
    candidate = next(row for row in candidates.json() if row["title"] == "Exercice synthétique")
    assert candidate["provenance"]["source_kind"] == "UNKNOWN_NOT_ASSERTED"
    assert candidate["provenance"]["origin_type"] == "CURATED_PROJECT"
    assert candidate["provenance"]["validation_status"] == "CURATED"
    assert "OFFICIAL" not in json.dumps(candidate["provenance"])

    sheet = _authoring_sheet(client, [instruction_id], automatic=True)
    assert sheet["resources"]
    snapshot = sheet["resources"][0]["snapshot"]
    assert snapshot["origin_type"] == "CURATED_PROJECT"
    assert snapshot["validation_status"] == "CURATED"
    assert snapshot["provenance"]["package_version"] == "test-1"
    assert "source_kind" not in snapshot["provenance"]
    assert sequence_id


def test_g6_documents_follow_effective_A_to_B_selection(client):
    instruction_id, _, _, _ = curriculum()
    with SessionLocal() as db:
        _, version_a = _resource(db, "G6-RES-A", "G6-SRC-A", [instruction_id], source_kind="OFFICIAL_GUIDE")
        _, version_b = _resource(db, "G6-RES-B", "G6-SRC-B", [instruction_id])
        db.commit()
        a_id, b_id = version_a.id, version_b.id
    sheet = _authoring_sheet(client, [instruction_id], automatic=True)
    assert sheet["authoring"]["selections"][str(instruction_id)]["resource_version_id"] == a_id
    assert [row["display_label"] for row in sheet["documents_used"]] == ["Source G6-SRC-A"]

    replaced = client.put(
        f"/api/authoring/sheets/{sheet['id']}/selection",
        json={"instruction_id": instruction_id, "resource_version_id": b_id},
    )
    assert replaced.status_code == 200, replaced.text
    body = replaced.json()
    assert [row["display_label"] for row in body["documents_used"]] == ["Source G6-SRC-B"]
    assert "Source G6-SRC-A" not in teacher_tex(body)
    historical_id = body["authoring"]["selection_history"][0]["instance_id"]
    historical = next(row for row in body["resources"] if row["id"] == historical_id)
    assert historical["snapshot"]["source_label"] == "Source G6-SRC-A"
    assert all(block["visible"] is False for block in historical["blocks"])

    assert client.post(f"/api/sheets/{sheet['id']}/finalize").status_code == 200
    frozen = client.get(f"/api/sheets/{sheet['id']}").json()
    with SessionLocal() as db:
        db.get(m.SourceDocument, next(row["snapshot"]["source_document_id"] for row in frozen["resources"] if row["source_resource_version_id"] == b_id)).title = "Source B modifiée"
        db.commit()
    assert client.get(f"/api/sheets/{sheet['id']}").json()["documents_used"] == frozen["documents_used"]


def test_g6_documents_keep_A_when_same_instance_remains_selected_elsewhere(client):
    with SessionLocal() as db:
        instructions = list(db.scalars(select(m.InstructionGuide).order_by(m.InstructionGuide.id).limit(2)))
        instruction_ids = [row.id for row in instructions]
        _, version_a = _resource(db, "G6-SHARED-A", "G6-SHARED-SRC-A", instruction_ids, source_kind="OFFICIAL_GUIDE")
        _, version_b = _resource(db, "G6-SHARED-B", "G6-SHARED-SRC-B", instruction_ids)
        db.commit()
        a_id, b_id = version_a.id, version_b.id
    sheet = _authoring_sheet(client, instruction_ids, automatic=True)
    selections = sheet["authoring"]["selections"]
    assert {selections[str(item)]["resource_version_id"] for item in instruction_ids} == {a_id}
    assert len({selections[str(item)]["instance_id"] for item in instruction_ids}) == 1

    replaced = client.put(
        f"/api/authoring/sheets/{sheet['id']}/selection",
        json={"instruction_id": instruction_ids[0], "resource_version_id": b_id},
    )
    assert replaced.status_code == 200, replaced.text
    labels = {row["display_label"] for row in replaced.json()["documents_used"]}
    assert labels == {"Source G6-SHARED-SRC-A", "Source G6-SHARED-SRC-B"}


def _schema(connection, table):
    columns = [tuple(row[1:6]) for row in connection.execute(f"PRAGMA table_info({table})")]
    foreign_keys = sorted(tuple(row[2:8]) for row in connection.execute(f"PRAGMA foreign_key_list({table})"))
    indexes = []
    for row in connection.execute(f"PRAGMA index_list({table})"):
        columns_in_index = tuple(item[2] for item in connection.execute(f"PRAGMA index_info({row[1]})"))
        indexes.append((bool(row[2]), columns_in_index))
    return {"columns": columns, "foreign_keys": foreign_keys, "indexes": sorted(indexes)}


def test_g6_true_0006_to_0007_preserves_data_enforces_fks_and_matches_fresh_head(tmp_path):
    root = Path(__file__).resolve().parents[2]
    historical_backend = tmp_path / "historical_backend"
    shutil.copytree(root / "backend", historical_backend, ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache"))
    old_models = subprocess.run(
        ["git", "show", f"{AUTHORIZED_SHA}:backend/app/models.py"],
        cwd=root,
        capture_output=True,
        check=True,
    ).stdout
    (historical_backend / "app" / "models.py").write_bytes(old_models)

    historical_db = tmp_path / "historical.db"
    fresh_db = tmp_path / "fresh.db"
    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "EXPORT_DIR": str(tmp_path / "exports")}
    historical_env = {**env, "DATABASE_URL": f"sqlite:///{historical_db.as_posix()}"}
    fresh_env = {**env, "DATABASE_URL": f"sqlite:///{fresh_db.as_posix()}"}

    old_upgrade = subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "0006_competency_catalog"],
        cwd=historical_backend,
        env=historical_env,
        capture_output=True,
        text=True,
    )
    assert old_upgrade.returncode == 0, old_upgrade.stdout + old_upgrade.stderr
    with sqlite3.connect(historical_db) as connection:
        before_columns = [row[1] for row in connection.execute("PRAGMA table_info(pedagogical_resources)")]
        assert before_columns == ["id", "code", "title", "resource_type", "structure_kind", "level", "provenance_kind"]
        assert connection.execute("PRAGMA foreign_key_list(pedagogical_resources)").fetchall() == []
        connection.execute("INSERT INTO pedagogical_resources VALUES (9001,'G6-HIST','Historique','ACTIVITY','ATOMIC','4e','SOURCED')")
        connection.execute(
            "INSERT INTO pedagogical_resource_versions VALUES (9001,9001,1,'Version historique','Résumé',10,'AVAILABLE','NOT_REVIEWED','NOT_REVIEWED','NOT_REVIEWED','NOT_REVIEWED','NOT_REVIEWED','{}','2026-09-06 00:00:00')"
        )
        connection.execute("INSERT INTO pedagogical_blocks VALUES (9001,9001,'CONSIGNE','Bloc historique','Contenu historique',1)")
        connection.commit()

    migrated = subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        cwd=root / "backend",
        env=historical_env,
        capture_output=True,
        text=True,
    )
    fresh = subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        cwd=root / "backend",
        env=fresh_env,
        capture_output=True,
        text=True,
    )
    assert migrated.returncode == 0, migrated.stdout + migrated.stderr
    assert fresh.returncode == 0, fresh.stdout + fresh.stderr

    seeded = subprocess.run(
        [sys.executable, "-c", "from app.database import SessionLocal; from app.seed import seed_database; s=SessionLocal(); seed_database(s); s.close()"],
        cwd=root / "backend",
        env=historical_env,
        capture_output=True,
        text=True,
    )
    assert seeded.returncode == 0, seeded.stdout + seeded.stderr

    expected_fks = {
        ("programme_versions", "programme_version_id", "id"),
        ("learning_situations", "situation_id", "id"),
        ("sequences", "sequence_id", "id"),
        ("guide_instructions", "primary_instruction_id", "id"),
        ("source_documents", "source_document_id", "id"),
    }
    with sqlite3.connect(historical_db) as historical, sqlite3.connect(fresh_db) as fresh_connection:
        historical.execute("PRAGMA foreign_keys=ON")
        observed_fks = {(row[2], row[3], row[4]) for row in historical.execute("PRAGMA foreign_key_list(pedagogical_resources)")}
        assert observed_fks == expected_fks
        row = historical.execute("SELECT id,code,title,resource_type,structure_kind,level,provenance_kind,created_at,updated_at FROM pedagogical_resources WHERE id=9001").fetchone()
        assert row == (9001, "G6-HIST", "Historique", "ACTIVITY", "ATOMIC", "4e", "SOURCED", None, None)
        assert historical.execute("SELECT title FROM pedagogical_resource_versions WHERE id=9001").fetchone() == ("Version historique",)
        assert historical.execute("SELECT content_latex FROM pedagogical_blocks WHERE id=9001").fetchone() == ("Contenu historique",)
        assert historical.execute("PRAGMA foreign_key_check").fetchall() == []
        for column in ("programme_version_id", "situation_id", "sequence_id", "primary_instruction_id", "source_document_id"):
            with pytest.raises(sqlite3.IntegrityError):
                historical.execute(
                    f"INSERT INTO pedagogical_resources (code,title,resource_type,structure_kind,level,provenance_kind,{column}) VALUES (?,?,?,?,?,?,?)",
                    (f"G6-BAD-{column}", "Bad", "ACTIVITY", "ATOMIC", "4e", "SOURCED", 999999),
                )
            historical.rollback()
        valid_ids = {
            "programme_version_id": historical.execute("SELECT id FROM programme_versions LIMIT 1").fetchone()[0],
            "situation_id": historical.execute("SELECT id FROM learning_situations LIMIT 1").fetchone()[0],
            "sequence_id": historical.execute("SELECT id FROM sequences LIMIT 1").fetchone()[0],
            "primary_instruction_id": historical.execute("SELECT id FROM guide_instructions LIMIT 1").fetchone()[0],
            "source_document_id": historical.execute("SELECT id FROM source_documents LIMIT 1").fetchone()[0],
        }
        historical.execute(
            "INSERT INTO pedagogical_resources (code,title,resource_type,structure_kind,level,provenance_kind,programme_version_id,situation_id,sequence_id,primary_instruction_id,source_document_id) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            ("G6-VALID-FKS", "Valid", "ACTIVITY", "ATOMIC", "4e", "SOURCED", *valid_ids.values()),
        )
        assert historical.execute("PRAGMA foreign_key_check").fetchall() == []
        for table in P3_TABLES:
            assert _schema(historical, table) == _schema(fresh_connection, table), table

    smoke = subprocess.run(
        [sys.executable, "-c", "from fastapi.testclient import TestClient; from app.main import app; r=TestClient(app).get('/api/pedagogical-resources'); assert r.status_code == 200, r.text"],
        cwd=root / "backend",
        env=historical_env,
        capture_output=True,
        text=True,
    )
    assert smoke.returncode == 0, smoke.stdout + smoke.stderr
