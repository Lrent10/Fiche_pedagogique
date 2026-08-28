from pathlib import Path


def test_e2e_001_complete_vertical_slice(client):
    instructions = client.get("/api/instructions").json()
    develop_product = next(item for item in instructions if item["code"] == "SEQ8-INS6")
    candidates = client.get(f"/api/resources?instruction_id={develop_product['id']}").json()
    assert len(candidates) >= 3
    assert any(item["provenance_kind"] == "DEMO_NON_SOURCE" for item in candidates)

    sheet = client.post(
        "/api/sheets",
        json={"title": "E2E — calcul littéral", "instruction_ids": [develop_product["id"]], "duration_minutes": 10},
    ).json()
    revision_id = sheet["id"]
    for candidate in candidates[:2]:
        response = client.post(f"/api/sheets/{revision_id}/resources/library", json={"resource_version_id": candidate["id"]})
        assert response.status_code == 201
        sheet = response.json()

    first_block = sheet["resources"][0]["blocks"][0]
    edited_source = r"Développe $(2x+1)^2$ puis représente $a^2$ avec \badcommand{conservée}."
    sheet = client.put(f"/api/sheets/{revision_id}/blocks/{first_block['id']}", json={"content_latex": edited_source}).json()
    assert sheet["resources"][0]["blocks"][0]["content_latex"] == edited_source

    ordered = [item["block_instance_id"] for item in reversed(sheet["flow"])]
    reordered = client.put(f"/api/sheets/{revision_id}/flow", json={"ordered_block_ids": ordered})
    assert reordered.status_code == 200
    warnings = client.get(f"/api/sheets/{revision_id}/warnings").json()
    assert any(item["code"] == "WARNING_DURATION_EXCEEDED" for item in warnings)

    detail = reordered.json()
    detail["identification"]["durée"] = "60 min"
    corrected = client.put(f"/api/sheets/{revision_id}/metadata", json={"identification": detail["identification"], "planning": detail["planning"]})
    assert corrected.status_code == 200

    assert client.post(f"/api/sheets/{revision_id}/finalize").json()["status"] == "FINALIZED"
    teacher_export = client.post("/api/exports", json={"document_family": "TEACHER", "revision_id": revision_id, "target": "TEACHER"})
    assert teacher_export.status_code == 201
    assert Path(teacher_export.json()["file_path"]).is_file()

    support = client.post("/api/supports", json={"title": "E2E — support apprenant"}).json()
    support_id = support["id"]
    product_resource = next(item for item in candidates if "produits remarquables" in item["title"].lower())
    assert client.post(f"/api/supports/{support_id}/resources/library", json={"resource_version_id": product_resource["id"]}).status_code == 201
    assert client.post(f"/api/supports/{support_id}/finalize").json()["status"] == "FINALIZED"
    initial = client.post("/api/exports", json={"document_family": "LEARNER", "revision_id": support_id, "target": "LEARNER_INITIAL"}).json()
    completed = client.post("/api/exports", json={"document_family": "LEARNER", "revision_id": support_id, "target": "LEARNER_COMPLETED"}).json()
    assert Path(initial["file_path"]).is_file()
    assert Path(completed["file_path"]).is_file()
    assert initial["file_path"] != completed["file_path"]

    execution = client.post("/api/teaching-sessions", json={"teacher_revision_id": revision_id, "taught_on": "2026-08-28", "class_label": "4e B", "actual_minutes": 67, "status": "DONE"})
    assert execution.status_code == 201
    progress_payload = client.get("/api/progress").json()
    assert progress_payload["normative_allocation"]["status"] == "UNRESOLVED_NORMATIVE_ALLOCATION"
    assert progress_payload["normative_allocation"]["remaining_hours"] is None
    progress = progress_payload["instructions"]
    progress_row = next(item for item in progress if item["code"] == "SEQ8-INS6")
    assert progress_row["status"] == "DONE"
    assert progress_row["actual_minutes"] == 67
