from app.exporter import support_tex, teacher_tex


def _teacher_detail(*, visible=True, title="Consigne"):
    return {
        "code": "FICHE-INTERNAL-999",
        "revision_number": 1,
        "title": "Produits remarquables",
        "identification": {"titre du cours": "Produits remarquables", "numéro fiche pédagogique": ""},
        "planning": {},
        "segments": [],
        "resources": [{"blocks": [{"id": 1, "title": title, "block_type": "INSTRUCTION", "content_latex": "Calculer $2+2$.", "visible": visible}]}],
        "flow": [{"block_instance_id": 1, "phase_code": "REALISATION", "teacher_action": "", "learner_action": "", "strategy": "TI", "expected_result_latex": "$2+2=4$", "duration_minutes": 10}],
    }


def test_uxdoc_001_teacher_pdf_source_has_no_application_text():
    tex = teacher_tex(_teacher_detail())
    forbidden = ("Révision figée", "générée localement", "consultables dans l'application")
    assert all(text not in tex for text in forbidden)


def test_uxdoc_002_internal_id_is_not_printed_by_default():
    assert "FICHE-INTERNAL-999" not in teacher_tex(_teacher_detail())


def test_uxdoc_003_generated_labels_are_not_duplicated():
    detail = {"title": "Support", "sequence": None, "situation": None, "resources": [{"title": "Activité de découverte", "blocks": [{"title": "Consigne 2", "content_latex": "Calculer.", "visible": True, "block_type": "INSTRUCTION"}, {"title": "Propriété", "content_latex": "$a=b$.", "visible": True, "block_type": "PROPERTY"}]}]}
    tex = support_tex(detail)
    assert r"\ActivityTitle{1}{Découverte}" in tex
    assert r"\InstructionTitle{1}{ :}" in tex
    assert "Consigne - Consigne" not in tex
    assert "Propriété - Propriété" not in tex


def test_uxdoc_003b_single_local_instruction_is_not_repeated_as_activity():
    detail = {"title": "Support", "sequence": None, "situation": None, "resources": [{"title": "Recherche guidée", "blocks": [{"title": "Recherche guidée", "content_latex": "Calculer.", "visible": True, "block_type": "INSTRUCTION"}]}]}
    tex = support_tex(detail)
    assert r"\ActivityTitle{1}" not in tex
    assert r"\InstructionTitle{1}{ : Recherche guidée}" in tex


def test_uxdoc_004_and_005_final_edit_only_changes_draft(client):
    sheet = client.post("/api/sheets", json={"title": "Final edit", "instruction_ids": [1], "duration_minutes": 55}).json()
    sheet = client.post(f"/api/sheets/{sheet['id']}/resources/local", json={"title": "Consigne", "block_type": "INSTRUCTION", "content_latex": "Avant"}).json()
    block = sheet["resources"][0]["blocks"][0]
    edited = client.put(f"/api/sheets/{sheet['id']}/blocks/{block['id']}", json={"title": "Titre naturel", "content_latex": "Après", "visible": False})
    assert edited.status_code == 200
    assert edited.json()["resources"][0]["blocks"][0]["visible"] is False
    assert client.post(f"/api/sheets/{sheet['id']}/finalize").status_code == 200
    assert client.put(f"/api/sheets/{sheet['id']}/blocks/{block['id']}", json={"content_latex": "Interdit"}).status_code == 409


def test_uxdoc_006_preview_edit_round_trip_preserves_support_link(client):
    resources = client.get("/api/resources").json()
    resource = next(row for row in resources if row["blocks"])
    support = client.post("/api/supports", json={"title": "Round trip"}).json()
    support = client.post(f"/api/supports/{support['id']}/resources/library", json={"resource_version_id": resource["id"]}).json()
    assert client.post(f"/api/supports/{support['id']}/finalize").status_code == 200
    selected = next(block for item in support["resources"] for block in item["blocks"] if block["visible"] and block["block_type"] not in {"EXPECTED_TRACE", "SOLUTION", "CORRECTION", "TEACHER_NOTE"})
    sheet = client.post(f"/api/supports/{support['id']}/create-teacher-sheet", json={"selected_block_ids": [selected["id"]]}).json()
    block = sheet["resources"][0]["blocks"][0]
    client.put(f"/api/sheets/{sheet['id']}/blocks/{block['id']}", json={"title": "Titre final"})
    again = client.get(f"/api/sheets/{sheet['id']}").json()
    assert again["support_use"]["support_revision_id"] == support["id"]
    assert again["support_use"]["selected_block_ids"] == [selected["id"]]


def test_uxdoc_007_custom_title_appears():
    assert "Titre personnalisé" in teacher_tex(_teacher_detail(title="Titre personnalisé"))


def test_uxdoc_008_hidden_block_disappears():
    tex = teacher_tex(_teacher_detail(visible=False, title="NE_DOIT_PAS_APPARAITRE"))
    assert r"NE\_DOIT\_PAS\_APPARAITRE" not in tex


def test_uxdoc_009_empty_support_cannot_be_finalized(client):
    support = client.post("/api/supports", json={"title": "Support vide"}).json()
    response = client.post(f"/api/supports/{support['id']}/finalize")
    assert response.status_code == 409
    assert "au moins un bloc visible" in response.json()["detail"]


def test_uxdoc_010_same_revision_has_reproducible_source():
    detail = _teacher_detail()
    assert teacher_tex(detail) == teacher_tex(detail)
