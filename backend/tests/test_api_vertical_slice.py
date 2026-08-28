def test_health_dashboard_and_curriculum_fidelity(client):
    assert client.get("/api/health").json()["status"] == "ok"
    dashboard = client.get("/api/dashboard").json()
    assert dashboard["draft_sheets"] == 1
    assert dashboard["resources"] == 4

    curriculum = client.get("/api/curriculum").json()
    allocations = curriculum["situations"][0]["time_allocations"]
    assert {item["hours"] for item in allocations} == {56.0, 60.0}
    assert curriculum["situations"][0]["sequences"][0]["code"] == "SEQ8"
    issue_codes = {issue["code"] for issue in curriculum["source_issues"]}
    assert {f"F-{index:02d}" for index in range(1, 8)} <= issue_codes
    assert "PILOT-OBS-01" in issue_codes


def test_resources_keep_source_and_demo_labels(client):
    resources = client.get("/api/resources").json()
    sourced = [item for item in resources if item["provenance_kind"] == "SOURCED"]
    demo = [item for item in resources if item["provenance_kind"] == "DEMO_NON_SOURCE"]
    assert len(sourced) == 3
    assert len(demo) == 1
    assert all(item["sources"] for item in sourced)
    assert demo[0]["sources"] == []
    assert "DÉMO" in demo[0]["title"]


def test_teacher_sheet_workflow_and_finalized_immutability(client):
    instruction_ids = [row["id"] for row in client.get("/api/instructions").json()[:2]]
    created = client.post("/api/sheets", json={"title": "Fiche test", "instruction_ids": instruction_ids, "duration_minutes": 50}).json()
    revision_id = created["id"]
    assert created["status"] == "DRAFT"

    resource_id = client.get("/api/resources").json()[0]["id"]
    with_resource = client.post(f"/api/sheets/{revision_id}/resources/library", json={"resource_version_id": resource_id, "adaptation_note": "Adapté au temps disponible"})
    assert with_resource.status_code == 201
    block = with_resource.json()["resources"][0]["blocks"][0]
    edited = client.put(f"/api/sheets/{revision_id}/blocks/{block['id']}", json={"content_latex": r"Calculer $(a+b)^2$."})
    assert edited.status_code == 200
    assert "Calculer" in edited.json()["resources"][0]["blocks"][0]["content_latex"]

    finalized = client.post(f"/api/sheets/{revision_id}/finalize")
    assert finalized.json()["status"] == "FINALIZED"
    blocked = client.put(f"/api/sheets/{revision_id}/blocks/{block['id']}", json={"title": "Interdit"})
    assert blocked.status_code == 409

    new_revision = client.post(f"/api/sheets/{revision_id}/new-revision")
    assert new_revision.status_code == 201
    assert new_revision.json()["revision_number"] == 2
    assert new_revision.json()["status"] == "DRAFT"


def test_support_workflow_visibility_and_revision(client):
    support = client.post("/api/supports", json={"title": "Support test"}).json()
    revision_id = support["id"]
    resource_id = client.get("/api/resources").json()[1]["id"]
    populated = client.post(f"/api/supports/{revision_id}/resources/library", json={"resource_version_id": resource_id})
    block_id = populated.json()["resources"][0]["blocks"][0]["id"]
    hidden = client.put(f"/api/supports/{revision_id}/blocks/{block_id}", json={"visible": False})
    assert hidden.json()["resources"][0]["blocks"][0]["visible"] is False
    assert client.post(f"/api/supports/{revision_id}/finalize").json()["status"] == "FINALIZED"
    assert client.put(f"/api/supports/{revision_id}/blocks/{block_id}", json={"visible": True}).status_code == 409
    revised = client.post(f"/api/supports/{revision_id}/new-revision")
    assert revised.json()["status"] == "DRAFT"


def test_library_snapshot_is_not_changed_by_future_library_edit(client):
    draft = next(item for item in client.get("/api/sheets").json() if item["status"] == "DRAFT")
    detail = client.get(f"/api/sheets/{draft['revision_id']}").json()
    original_copy = detail["resources"][0]["blocks"][0]["content_latex"]
    resource_id = detail["resources"][0]["source_resource_version_id"]

    from app import models as m
    from app.database import SessionLocal
    with SessionLocal() as db:
        library_block = db.query(m.PedagogicalBlock).filter(m.PedagogicalBlock.resource_version_id == resource_id).first()
        library_block.content_latex = "CHANGEMENT FUTUR DE BIBLIOTHÈQUE"
        db.commit()

    unchanged = client.get(f"/api/sheets/{draft['revision_id']}").json()
    assert unchanged["resources"][0]["blocks"][0]["content_latex"] == original_copy


def test_warning_and_ambiguous_progress_are_explicit(client):
    instruction = client.get("/api/instructions").json()[0]
    sheet = client.post("/api/sheets", json={"title": "Brouillon incomplet", "instruction_ids": [instruction["id"]], "duration_minutes": 10}).json()
    warnings = client.get(f"/api/sheets/{sheet['id']}/warnings").json()
    assert any(item["code"] == "WARNING_INSTRUCTION_WITHOUT_RESOURCE" for item in warnings)
    progress = client.get("/api/progress").json()
    assert progress["normative_allocation"]["status"] == "UNRESOLVED_NORMATIVE_ALLOCATION"
    assert progress["normative_allocation"]["remaining_hours"] is None


def test_retired_resource_disappears_for_new_use_but_snapshot_survives(client):
    draft = next(item for item in client.get("/api/sheets").json() if item["status"] == "DRAFT")
    detail_before = client.get(f"/api/sheets/{draft['revision_id']}").json()
    version_id = detail_before["resources"][0]["source_resource_version_id"]
    from app import models as m
    from app.database import SessionLocal
    with SessionLocal() as db:
        db.get(m.PedagogicalResourceVersion, version_id).status = "RETIRED"
        db.commit()
    assert all(item["id"] != version_id for item in client.get("/api/resources").json())
    blocked = client.post(f"/api/sheets/{draft['revision_id']}/resources/library", json={"resource_version_id": version_id})
    assert blocked.status_code == 409
    detail_after = client.get(f"/api/sheets/{draft['revision_id']}").json()
    assert detail_after["resources"][0]["blocks"] == detail_before["resources"][0]["blocks"]
