import json
import shutil
import subprocess

import pytest
from sqlalchemy import select

from app import models as m
from app.curriculum_level import CLASS_LEVEL_ERROR, class_label_matches_level
from app.database import SessionLocal
from app.exporter import support_tex, teacher_tex


def _draft(client):
    summary = next(item for item in client.get("/api/sheets").json() if item["status"] == "DRAFT")
    return client.get(f"/api/sheets/{summary['revision_id']}").json()


@pytest.mark.parametrize("class_label", ["4e", "4E", "4ème", "4eme", "4e A", "4e M1", "4ème B"])
def test_supported_4e_spellings_are_normalized(class_label):
    assert class_label_matches_level(class_label, "4e")


@pytest.mark.parametrize("class_label", ["4e", "4e M1", "4ème B"])
def test_001_to_003_compatible_4e_class_labels_are_accepted(client, class_label):
    sheet = _draft(client)
    identification = sheet["identification"] | {"classe": class_label}

    response = client.put(
        f"/api/sheets/{sheet['id']}/metadata",
        json={"identification": identification, "planning": sheet["planning"]},
    )

    assert response.status_code == 200
    assert response.json()["identification"]["classe"] == class_label
    assert response.json()["curriculum_level"] == "4e"


def test_005_and_006_backend_rejects_incompatible_class_without_persisting(client):
    before = _draft(client)
    invalid_identification = before["identification"] | {"classe": "3ème M1"}

    response = client.put(
        f"/api/sheets/{before['id']}/metadata",
        json={"identification": invalid_identification, "planning": before["planning"]},
    )

    assert response.status_code == 422
    assert response.json()["detail"] == CLASS_LEVEL_ERROR
    after = client.get(f"/api/sheets/{before['id']}").json()
    assert after["identification"] == before["identification"]
    assert after["planning"] == before["planning"]


def test_007_to_010_valid_subdivision_changes_document_only(client, tmp_path):
    before = _draft(client)
    identification = before["identification"] | {"classe": "4e M1"}
    before_segment_ids = [segment["instruction_id"] for segment in before["segments"]]
    before_resource_ids = [resource["source_resource_version_id"] for resource in before["resources"]]

    updated = client.put(
        f"/api/sheets/{before['id']}/metadata",
        json={"identification": identification, "planning": before["planning"]},
    ).json()

    assert updated["curriculum_level"] == "4e"
    assert [segment["instruction_id"] for segment in updated["segments"]] == before_segment_ids
    assert [resource["source_resource_version_id"] for resource in updated["resources"]] == before_resource_ids
    assert "4e M1" in teacher_tex(updated)

    with SessionLocal() as db:
        revision = db.get(m.TeacherSheetRevision, before["id"])
        persisted_identification = json.loads(revision.identification_json)
        teacher_sheet = db.get(m.TeacherSessionSheet, revision.sheet_id)
        segment_ids = list(
            db.scalars(
                select(m.SessionCurriculumSegment.instruction_id).where(
                    m.SessionCurriculumSegment.teacher_revision_id == revision.id
                )
            ).all()
        )
        version_ids = [resource_id for resource_id in before_resource_ids if resource_id]
        resource_levels = set(
            db.scalars(
                select(m.PedagogicalResource.level)
                .join(m.PedagogicalResourceVersion, m.PedagogicalResourceVersion.resource_id == m.PedagogicalResource.id)
                .where(m.PedagogicalResourceVersion.id.in_(version_ids))
            ).all()
        ) if version_ids else set()

    assert persisted_identification["classe"] == "4e M1"
    assert teacher_sheet.level == "4e"
    assert segment_ids == before_segment_ids
    assert resource_levels == {"4e"}

    exported = client.post(
        "/api/exports",
        json={"document_family": "TEACHER", "revision_id": before["id"]},
    )
    assert exported.status_code == 201
    pdftotext = shutil.which("pdftotext")
    if pdftotext:
        text_path = tmp_path / "teacher-class.txt"
        subprocess.run(
            [pdftotext, exported.json()["file_path"], str(text_path)],
            check=True,
        )
        assert "4e M1" in text_path.read_text(encoding="utf-8")


def test_creation_keeps_curriculum_level_distinct_from_class_subdivision(client):
    instruction_id = client.get("/api/instructions").json()[0]["id"]

    created = client.post(
        "/api/sheets",
        json={"title": "Subdivision", "instruction_ids": [instruction_id], "class_label": "4ème B"},
    )

    assert created.status_code == 201
    assert created.json()["curriculum_level"] == "4e"
    assert created.json()["identification"]["classe"] == "4ème B"
    with SessionLocal() as db:
        assert db.get(m.TeacherSessionSheet, created.json()["sheet_id"]).level == "4e"


def test_creation_rejects_an_incompatible_level(client):
    instruction_id = client.get("/api/instructions").json()[0]["id"]
    response = client.post(
        "/api/sheets",
        json={"title": "Niveau invalide", "instruction_ids": [instruction_id], "class_label": "3ème M1"},
    )
    assert response.status_code == 422
    assert response.json()["detail"] == CLASS_LEVEL_ERROR


def test_support_pdf_header_uses_the_support_curriculum_level(client):
    support = client.post("/api/supports", json={"title": "Support niveau"}).json()
    assert support["level"] == "4e"
    assert "Mathématiques - 4e" in support_tex(support)
