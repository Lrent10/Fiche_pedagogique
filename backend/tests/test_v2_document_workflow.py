from pathlib import Path
import shutil
import subprocess

import pytest

from app.exporter import support_tex, teacher_tex


TEACHER_ONLY = {"EXPECTED_RESULT", "EXPECTED_TRACE", "SOLUTION", "CORRECTION", "TEACHER_NOTE"}


def _resource_with_blocks(client):
    resources = client.get("/api/resources").json()
    return next(
        resource
        for resource in resources
        if len([block for block in resource["blocks"] if block["block_type"] not in TEACHER_ONLY]) >= 2
    )


def _finalized_support(client):
    resource = _resource_with_blocks(client)
    support = client.post("/api/supports", json={"title": "Support V2 - test"}).json()
    support = client.post(
        f"/api/supports/{support['id']}/resources/library",
        json={"resource_version_id": resource["id"]},
    ).json()
    assert client.post(f"/api/supports/{support['id']}/finalize").status_code == 200
    support = client.get(f"/api/supports/{support['id']}").json()
    eligible = [
        block
        for item in support["resources"]
        for block in item["blocks"]
        if block["visible"] and block["block_type"] not in TEACHER_ONLY
    ]
    return support, eligible


def _sheet_from_support(client):
    support, blocks = _finalized_support(client)
    selected = [block["id"] for block in blocks[:2]]
    response = client.post(
        f"/api/supports/{support['id']}/create-teacher-sheet",
        json={
            "title": "Séance V2 - test",
            "selected_block_ids": selected,
            "duration_minutes": 50,
            "class_label": "4e C",
            "part_label": "Deux blocs de test",
        },
    )
    assert response.status_code == 201
    return support, selected, response.json()


def test_doc_001_to_005_teacher_template_and_manual_expected_result():
    detail = {
        "code": "FICHE-TEST",
        "revision_number": 1,
        "title": "Cours sentinelle",
        "identification": {
            "établissement": "CEG_TEST_EXPORT_987",
            "année scolaire": "2026-2027",
            "discipline": "Mathématiques",
            "date": "17/09/2026",
            "classe": "4e C",
            "effectif": "43",
            "nombre de groupes": "7",
            "nom du professeur": "PROF_TEST_EXPORT_654",
            "SA": "SA_TEST",
            "séquence": "SEQ_TEST",
            "durée de la séance": "55 min",
            "numéro de séance": "17",
        },
        "planning": {
            "contenus de formation": "ALGEBRE_SENTINELLE",
            "compétences disciplinaires": "COMP_DISC_SENTINELLE",
            "connaissances et techniques": "CONNAISSANCE_SENTINELLE",
            "matériels apprenants": "MATERIEL_APPRENANT_SENTINELLE",
            "matériels enseignant": "MATERIEL_ENSEIGNANT_SENTINELLE",
        },
        "segments": [],
        "resources": [{"blocks": [{"id": 1, "title": "Consigne", "block_type": "INSTRUCTION", "content_latex": "Calculer $2+2$."}]}],
        "flow": [{
            "block_instance_id": 1,
            "phase_code": "REALISATION",
            "teacher_action": "",
            "learner_action": "",
            "strategy": "TI",
            "expected_result_latex": r"RESULTAT_MANUEL_SENTINELLE : $2+2=4$.",
            "duration_minutes": 10,
        }],
    }
    tex = teacher_tex(detail)
    for sentinel in (
        "CEG\\_TEST\\_EXPORT\\_987",
        "PROF\\_TEST\\_EXPORT\\_654",
        "2026-2027",
        "43",
        "COMP\\_DISC\\_SENTINELLE",
        "CONNAISSANCE\\_SENTINELLE",
        "MATERIEL\\_APPRENANT\\_SENTINELLE",
        "MATERIEL\\_ENSEIGNANT\\_SENTINELLE",
        "RESULTAT_MANUEL_SENTINELLE",
    ):
        assert sentinel in tex


def test_doc_006_source_result_is_not_copied_to_manual_expected_result(client):
    _, _, sheet = _sheet_from_support(client)
    assert all(flow["expected_result_latex"] == "" for flow in sheet["flow"])
    assert all(
        block["block_type"] not in TEACHER_ONLY
        for resource in sheet["resources"]
        for block in resource["blocks"]
    )


def test_doc_007_and_008_initial_masks_completed_content():
    detail = {
        "title": "Support",
        "sequence": None,
        "situation": None,
        "resources": [{
            "title": "Activité",
            "blocks": [{
                "title": "Correction",
                "content_latex": "SECRET_COMPLETED_789",
                "visible": True,
                "block_type": "SOLUTION",
            }],
        }],
    }
    assert "SECRET_COMPLETED_789" not in support_tex(detail, "LEARNER_INITIAL")
    assert "SECRET_COMPLETED_789" in support_tex(detail, "LEARNER_COMPLETED")


def test_doc_009_and_010_exports_keep_exact_revisions(client):
    support, _, sheet = _sheet_from_support(client)
    teacher_r1 = sheet["id"]
    support_r1 = support["id"]
    assert client.post(f"/api/sheets/{teacher_r1}/finalize").status_code == 200
    teacher_r2 = client.post(f"/api/sheets/{teacher_r1}/new-revision").json()
    support_r2 = client.post(f"/api/supports/{support_r1}/new-revision").json()
    assert teacher_r2["revision_number"] == 2
    assert support_r2["revision_number"] == 2
    teacher_export = client.post("/api/exports", json={"document_family": "TEACHER", "revision_id": teacher_r1}).json()
    support_export = client.post("/api/exports", json={"document_family": "LEARNER", "revision_id": support_r1, "target": "LEARNER_INITIAL"}).json()
    assert "_r1.pdf" in teacher_export["file_path"]
    assert "_r1.pdf" in support_export["file_path"]


def test_wf_001_support_to_sheet_manual_result_finalize_and_export(client, tmp_path):
    support, selected, sheet = _sheet_from_support(client)
    assert sheet["support_use"]["support_revision_id"] == support["id"]
    assert sheet["support_use"]["selected_block_ids"] == selected
    flow = sheet["flow"][0]
    sheet = client.put(
        f"/api/sheets/{sheet['id']}/flow/{flow['id']}",
        json={
            "expected_result_latex": r"RESULTAT\_PDF\_MANUEL\_456 : $x=7$.",
            "strategy": "TI / TC",
            "duration_minutes": 25,
        },
    ).json()
    identification = sheet["identification"] | {
        "établissement": "CEG_TEST_EXPORT_987",
        "nom du professeur": "PROF_TEST_EXPORT_654",
        "effectif": "43",
        "année scolaire": "2026-2027",
        "numéro de séance": "17",
    }
    sheet = client.put(
        f"/api/sheets/{sheet['id']}/metadata",
        json={"identification": identification, "planning": sheet["planning"]},
    ).json()
    assert client.post(f"/api/sheets/{sheet['id']}/finalize").json()["status"] == "FINALIZED"
    exported = client.post("/api/exports", json={"document_family": "TEACHER", "revision_id": sheet["id"]}).json()
    pdf_path = Path(exported["file_path"])
    assert pdf_path.is_file()
    log_text = pdf_path.with_suffix(".log").read_text(encoding="utf-8")
    assert "ENGINE=LATEX" in log_text
    pdftotext = shutil.which("pdftotext")
    if not pdftotext:
        pytest.skip("pdftotext indisponible")
    text_path = tmp_path / "teacher.txt"
    subprocess.run([pdftotext, str(pdf_path), str(text_path)], check=True)
    pdf_text = text_path.read_text(encoding="utf-8")
    for sentinel in ("CEG_TEST_EXPORT_987", "PROF_TEST_EXPORT_654", "43", "2026-2027", "17", "RESULTAT_PDF_MANUEL_456"):
        assert sentinel in pdf_text


def test_wf_002_and_003_support_history_is_preserved(client):
    support, selected, first_sheet = _sheet_from_support(client)
    support_r1 = support["id"]
    support_r2 = client.post(f"/api/supports/{support_r1}/new-revision").json()
    first_r2_block = support_r2["resources"][0]["blocks"][0]
    changed = client.put(
        f"/api/supports/{support_r2['id']}/blocks/{first_r2_block['id']}",
        json={"content_latex": "CONTENU_NOUVELLE_REVISION_321"},
    ).json()
    assert client.post(f"/api/supports/{changed['id']}/finalize").status_code == 200
    second_selected = [
        block["id"]
        for resource in changed["resources"]
        for block in resource["blocks"]
        if block["visible"] and block["block_type"] not in TEACHER_ONLY
    ][:2]
    second_sheet = client.post(
        f"/api/supports/{changed['id']}/create-teacher-sheet",
        json={"selected_block_ids": second_selected},
    ).json()
    first_again = client.get(f"/api/sheets/{first_sheet['id']}").json()
    assert first_again["support_use"]["support_revision_id"] == support_r1
    assert first_again["support_use"]["selected_block_ids"] == selected
    assert second_sheet["support_use"]["support_revision_id"] == changed["id"]
    assert second_sheet["support_use"]["support_revision_id"] != first_again["support_use"]["support_revision_id"]
