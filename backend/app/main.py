from __future__ import annotations

import json
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from . import models as m
from .config import settings
from .database import get_db
from .exporter import export_document
from .schemas import (
    AddLibraryResource,
    AddLocalResource,
    BlockUpdate,
    ExportCreate,
    FlowItemUpdate,
    FlowUpdate,
    RenamePayload,
    SheetCreate,
    SheetFromSupportCreate,
    SheetMetadataUpdate,
    SupportCreate,
    SupportUseCreate,
    TeachingSessionCreate,
)
from .services import (
    add_local_to_sheet,
    add_local_to_support,
    copy_library_to_sheet,
    copy_library_to_support,
    create_sheet_from_support,
    finalize_revision,
    new_support_revision,
    new_teacher_revision,
    require_draft,
    sheet_detail,
    sheet_warnings,
    support_detail,
    support_warnings,
)


settings.export_dir.mkdir(parents=True, exist_ok=True)


@asynccontextmanager
async def lifespan(_: FastAPI):
    yield


app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[item.strip() for item in settings.cors_origins.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/exports", StaticFiles(directory=settings.export_dir), name="exports")


@app.get("/api/health")
def health():
    return {"status": "ok", "app": settings.app_name}


@app.get("/api/dashboard")
def dashboard(db: Session = Depends(get_db)):
    return {
        "draft_sheets": db.scalar(select(func.count()).select_from(m.TeacherSheetRevision).where(m.TeacherSheetRevision.status == "DRAFT")),
        "finalized_sheets": db.scalar(select(func.count()).select_from(m.TeacherSheetRevision).where(m.TeacherSheetRevision.status == "FINALIZED")),
        "resources": db.scalar(select(func.count()).select_from(m.PedagogicalResourceVersion)),
        "supports": db.scalar(select(func.count()).select_from(m.LearnerSupportRevision)),
        "open_source_issues": db.scalar(select(func.count()).select_from(m.SourceIssue).where(m.SourceIssue.status == "OPEN")),
    }


@app.get("/api/curriculum")
def curriculum(db: Session = Depends(get_db)):
    situations = db.scalars(select(m.SituationApprentissage).order_by(m.SituationApprentissage.position)).all()
    result = []
    for situation in situations:
        allocations = db.execute(select(m.CurriculumTimeAllocation, m.SourceDocument).join(m.SourceDocument).where(m.CurriculumTimeAllocation.situation_id == situation.id)).all()
        sequences = db.scalars(select(m.Sequence).where(m.Sequence.situation_id == situation.id).order_by(m.Sequence.position)).all()
        result.append(
            {
                "id": situation.id,
                "code": situation.code,
                "title": situation.title,
                "time_allocations": [{"hours": allocation.hours, "note": allocation.note, "source": source.title, "source_code": source.code} for allocation, source in allocations],
                "sequences": [{"id": sequence.id, "code": sequence.code, "title": sequence.title, "position": sequence.position} for sequence in sequences],
            }
        )
    issues = db.scalars(select(m.SourceIssue).order_by(m.SourceIssue.code)).all()
    return {"situations": result, "source_issues": [{"code": issue.code, "title": issue.title, "description": issue.description, "status": issue.status} for issue in issues]}


@app.get("/api/instructions")
def instructions(sequence_id: int | None = None, db: Session = Depends(get_db)):
    query = select(m.InstructionGuide).order_by(m.InstructionGuide.position)
    if sequence_id:
        query = query.where(m.InstructionGuide.sequence_id == sequence_id)
    rows = db.scalars(query).all()
    return [{"id": row.id, "code": row.code, "text": row.text, "position": row.position, "sequence_id": row.sequence_id} for row in rows]


@app.get("/api/resources")
def resources(instruction_id: int | None = None, db: Session = Depends(get_db)):
    query = select(m.PedagogicalResourceVersion, m.PedagogicalResource).join(m.PedagogicalResource).where(m.PedagogicalResourceVersion.status == "AVAILABLE")
    if instruction_id:
        query = query.join(m.ResourceInstructionMapping).where(m.ResourceInstructionMapping.instruction_id == instruction_id)
    result = []
    for version, resource in db.execute(query.order_by(m.PedagogicalResourceVersion.id)).all():
        blocks = db.scalars(select(m.PedagogicalBlock).where(m.PedagogicalBlock.resource_version_id == version.id).order_by(m.PedagogicalBlock.position)).all()
        mappings = db.execute(select(m.ResourceInstructionMapping, m.InstructionGuide).join(m.InstructionGuide).where(m.ResourceInstructionMapping.resource_version_id == version.id)).all()
        occurrences = db.execute(select(m.SourceOccurrence, m.SourceDocument).join(m.SourceDocument).where(m.SourceOccurrence.entity_type == "PedagogicalResourceVersion", m.SourceOccurrence.entity_id == version.id)).all()
        result.append(
            {
                "id": version.id,
                "code": resource.code,
                "title": version.title,
                "resource_type": resource.resource_type,
                "provenance_kind": resource.provenance_kind,
                "summary": version.summary,
                "estimated_minutes": version.estimated_minutes,
                "blocks": [{"id": block.id, "block_type": block.block_type, "title": block.title, "content_latex": block.content_latex, "position": block.position} for block in blocks],
                "mappings": [{"instruction_id": instruction.id, "instruction_code": instruction.code, "text": instruction.text, "validation_status": mapping.validation_status} for mapping, instruction in mappings],
                "sources": [{"document": source.title, "file_name": source.file_name, "sha256": source.sha256, "page": occurrence.page_label, "locator": occurrence.locator} for occurrence, source in occurrences],
            }
        )
    return result


@app.get("/api/sheets")
def sheets(db: Session = Depends(get_db)):
    rows = db.execute(select(m.TeacherSessionSheet, m.TeacherSheetRevision).join(m.TeacherSheetRevision).order_by(m.TeacherSessionSheet.id, m.TeacherSheetRevision.revision_number.desc())).all()
    return [{"sheet_id": sheet.id, "revision_id": revision.id, "code": sheet.code, "title": sheet.title, "revision_number": revision.revision_number, "status": revision.status} for sheet, revision in rows]


@app.post("/api/sheets", status_code=201)
def create_sheet(payload: SheetCreate, db: Session = Depends(get_db)):
    instructions = db.scalars(select(m.InstructionGuide).where(m.InstructionGuide.id.in_(payload.instruction_ids))).all()
    if len(instructions) != len(set(payload.instruction_ids)):
        raise HTTPException(400, "Une ou plusieurs instructions sont introuvables.")
    number = (db.scalar(select(func.count()).select_from(m.TeacherSessionSheet)) or 0) + 1
    sheet = m.TeacherSessionSheet(code=f"FICHE-4E-{number:03d}", title=payload.title, level=payload.class_label)
    db.add(sheet)
    db.flush()
    revision = m.TeacherSheetRevision(
        sheet_id=sheet.id,
        revision_number=1,
        identification_json=json.dumps({
            "titre du cours": payload.title,
            "numéro fiche pédagogique": "",
            "établissement": "",
            "année scolaire": "",
            "discipline": "Mathématiques",
            "date": "",
            "classe": payload.class_label,
            "effectif": "",
            "nombre de groupes": "",
            "nom du professeur": "",
            "SA": "SA1",
            "titre SA": "Configurations du plan",
            "durée curriculaire SA": "",
            "séquence": "Séquence 8",
            "titre séquence": "Calculs sur les expressions algébriques",
            "durée de la séance": f"{payload.duration_minutes} min",
            "numéro de séance": "",
        }, ensure_ascii=False),
        planning_json=json.dumps({
            "contenus de formation": "",
            "compétences disciplinaires": "",
            "compétence transdisciplinaire": "",
            "compétences transversales": "",
            "connaissances et techniques": "",
            "stratégie objet d'apprentissage": "",
            "durée": f"{payload.duration_minutes} min",
            "stratégies d'enseignement/apprentissage": "TI / TG / TC",
            "matériels apprenants": "",
            "matériels enseignant": "",
        }, ensure_ascii=False),
    )
    db.add(revision)
    db.flush()
    per_segment = payload.duration_minutes // max(1, len(instructions))
    instruction_by_id = {row.id: row for row in instructions}
    for position, instruction_id in enumerate(payload.instruction_ids, 1):
        db.add(m.SessionCurriculumSegment(teacher_revision_id=revision.id, instruction_id=instruction_id, position=position, planned_minutes=per_segment))
    db.commit()
    return sheet_detail(db, revision.id)


@app.get("/api/sheets/{revision_id}")
def get_sheet(revision_id: int, db: Session = Depends(get_db)):
    return sheet_detail(db, revision_id)


@app.get("/api/sheets/{revision_id}/warnings")
def get_sheet_warnings(revision_id: int, db: Session = Depends(get_db)):
    return sheet_warnings(db, revision_id)


@app.put("/api/sheets/{revision_id}/metadata")
def update_metadata(revision_id: int, payload: SheetMetadataUpdate, db: Session = Depends(get_db)):
    revision = db.get(m.TeacherSheetRevision, revision_id)
    require_draft(revision)
    revision.identification_json = json.dumps(payload.identification, ensure_ascii=False)
    revision.planning_json = json.dumps(payload.planning, ensure_ascii=False)
    db.commit()
    return sheet_detail(db, revision_id)


@app.post("/api/sheets/{revision_id}/resources/library", status_code=201)
def add_sheet_library(revision_id: int, payload: AddLibraryResource, db: Session = Depends(get_db)):
    copy_library_to_sheet(db, revision_id, payload.resource_version_id, payload.adaptation_note)
    return sheet_detail(db, revision_id)


@app.post("/api/sheets/{revision_id}/resources/local", status_code=201)
def add_sheet_local(revision_id: int, payload: AddLocalResource, db: Session = Depends(get_db)):
    add_local_to_sheet(db, revision_id, payload.title, payload.block_type, payload.content_latex)
    return sheet_detail(db, revision_id)


@app.put("/api/sheets/{revision_id}/blocks/{block_id}")
def update_sheet_block(revision_id: int, block_id: int, payload: BlockUpdate, db: Session = Depends(get_db)):
    revision = db.get(m.TeacherSheetRevision, revision_id)
    require_draft(revision)
    block = db.execute(select(m.SheetBlockInstance).join(m.SheetResourceInstance).where(m.SheetBlockInstance.id == block_id, m.SheetResourceInstance.teacher_revision_id == revision_id)).scalar_one_or_none()
    if not block:
        raise HTTPException(404, "Bloc introuvable dans cette fiche.")
    if payload.title is not None:
        block.title = payload.title
    if payload.content_latex is not None:
        block.content_latex = payload.content_latex
    if payload.visible is not None:
        block.visible = payload.visible
    db.commit()
    return sheet_detail(db, revision_id)


@app.put("/api/sheets/{revision_id}/flow")
def reorder_flow(revision_id: int, payload: FlowUpdate, db: Session = Depends(get_db)):
    revision = db.get(m.TeacherSheetRevision, revision_id)
    require_draft(revision)
    flows = db.scalars(select(m.FlowItem).where(m.FlowItem.teacher_revision_id == revision_id)).all()
    by_block = {flow.block_instance_id: flow for flow in flows}
    if set(payload.ordered_block_ids) != set(by_block):
        raise HTTPException(400, "La liste doit contenir exactement tous les blocs du déroulement.")
    for temporary, flow in enumerate(flows, 1):
        flow.position = 100000 + temporary
    db.flush()
    for position, block_id in enumerate(payload.ordered_block_ids, 1):
        by_block[block_id].position = position
    db.commit()
    return sheet_detail(db, revision_id)


@app.put("/api/sheets/{revision_id}/flow/{flow_id}")
def update_flow_item(revision_id: int, flow_id: int, payload: FlowItemUpdate, db: Session = Depends(get_db)):
    revision = db.get(m.TeacherSheetRevision, revision_id)
    require_draft(revision)
    flow = db.scalar(select(m.FlowItem).where(m.FlowItem.id == flow_id, m.FlowItem.teacher_revision_id == revision_id))
    if not flow:
        raise HTTPException(404, "Élément de déroulement introuvable.")
    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(flow, field, value)
    db.commit()
    return sheet_detail(db, revision_id)


@app.post("/api/sheets/{revision_id}/finalize")
def finalize_sheet(revision_id: int, db: Session = Depends(get_db)):
    finalize_revision(db, "TEACHER", revision_id)
    return sheet_detail(db, revision_id)


@app.post("/api/sheets/{revision_id}/new-revision", status_code=201)
def revise_sheet(revision_id: int, db: Session = Depends(get_db)):
    revision = new_teacher_revision(db, revision_id)
    return sheet_detail(db, revision.id)


@app.post("/api/sheets/{revision_id}/duplicate", status_code=201)
def duplicate_sheet(revision_id: int, db: Session = Depends(get_db)):
    source = db.get(m.TeacherSheetRevision, revision_id)
    if not source:
        raise HTTPException(404, "Révision introuvable.")
    source_sheet = db.get(m.TeacherSessionSheet, source.sheet_id)
    copied_revision = new_teacher_revision(db, revision_id)
    number = (db.scalar(select(func.count()).select_from(m.TeacherSessionSheet)) or 0) + 1
    copied_sheet = m.TeacherSessionSheet(code=f"FICHE-4E-{number:03d}", title=f"{source_sheet.title} — copie", level=source_sheet.level)
    db.add(copied_sheet)
    db.flush()
    copied_revision.sheet_id = copied_sheet.id
    copied_revision.revision_number = 1
    db.commit()
    return sheet_detail(db, copied_revision.id)


@app.put("/api/sheets/{sheet_id}/rename")
def rename_sheet(sheet_id: int, payload: RenamePayload, db: Session = Depends(get_db)):
    sheet = db.get(m.TeacherSessionSheet, sheet_id)
    if not sheet:
        raise HTTPException(404, "Fiche introuvable.")
    draft_id = db.scalar(select(m.TeacherSheetRevision.id).where(m.TeacherSheetRevision.sheet_id == sheet_id, m.TeacherSheetRevision.status == "DRAFT").limit(1))
    if not draft_id:
        raise HTTPException(409, "Une fiche sans brouillon ne peut pas être renommée.")
    sheet.title = payload.title
    db.commit()
    latest_id = db.scalar(select(m.TeacherSheetRevision.id).where(m.TeacherSheetRevision.sheet_id == sheet_id).order_by(m.TeacherSheetRevision.revision_number.desc()).limit(1))
    return sheet_detail(db, latest_id)


@app.delete("/api/sheets/{sheet_id}", status_code=204)
def delete_draft_sheet(sheet_id: int, db: Session = Depends(get_db)):
    sheet = db.get(m.TeacherSessionSheet, sheet_id)
    if not sheet:
        raise HTTPException(404, "Fiche introuvable.")
    revisions = db.scalars(select(m.TeacherSheetRevision).where(m.TeacherSheetRevision.sheet_id == sheet_id)).all()
    if any(revision.status != "DRAFT" for revision in revisions):
        raise HTTPException(409, "Une fiche possédant une révision finalisée ne peut pas être supprimée.")
    for revision in revisions:
        resources = db.scalars(select(m.SheetResourceInstance).where(m.SheetResourceInstance.teacher_revision_id == revision.id)).all()
        resource_ids = [resource.id for resource in resources]
        block_ids = db.scalars(select(m.SheetBlockInstance.id).where(m.SheetBlockInstance.resource_instance_id.in_(resource_ids))).all() if resource_ids else []
        db.query(m.DocumentExport).filter(m.DocumentExport.teacher_revision_id == revision.id).delete(synchronize_session=False)
        db.query(m.SupportUse).filter(m.SupportUse.teacher_revision_id == revision.id).delete(synchronize_session=False)
        db.query(m.FlowItem).filter(m.FlowItem.teacher_revision_id == revision.id).delete(synchronize_session=False)
        if block_ids:
            db.query(m.SheetBlockInstance).filter(m.SheetBlockInstance.id.in_(block_ids)).delete(synchronize_session=False)
        if resource_ids:
            db.query(m.SheetResourceInstance).filter(m.SheetResourceInstance.id.in_(resource_ids)).delete(synchronize_session=False)
        db.query(m.SessionCurriculumSegment).filter(m.SessionCurriculumSegment.teacher_revision_id == revision.id).delete(synchronize_session=False)
        db.delete(revision)
    db.delete(sheet)
    db.commit()


@app.get("/api/supports")
def supports(db: Session = Depends(get_db)):
    rows = db.execute(select(m.LearnerSupport, m.LearnerSupportRevision).join(m.LearnerSupportRevision).order_by(m.LearnerSupport.id, m.LearnerSupportRevision.revision_number.desc())).all()
    return [{"support_id": support.id, "revision_id": revision.id, "code": support.code, "title": support.title, "revision_number": revision.revision_number, "status": revision.status} for support, revision in rows]


@app.post("/api/supports", status_code=201)
def create_support(payload: SupportCreate, db: Session = Depends(get_db)):
    number = (db.scalar(select(func.count()).select_from(m.LearnerSupport)) or 0) + 1
    sequence_id = db.scalar(select(m.Sequence.id).order_by(m.Sequence.position).limit(1))
    support = m.LearnerSupport(code=f"SUPPORT-4E-{number:03d}", title=payload.title, sequence_id=sequence_id)
    db.add(support)
    db.flush()
    revision = m.LearnerSupportRevision(support_id=support.id, revision_number=1)
    db.add(revision)
    db.commit()
    return support_detail(db, revision.id)


@app.get("/api/supports/{revision_id}")
def get_support(revision_id: int, db: Session = Depends(get_db)):
    return support_detail(db, revision_id)


@app.get("/api/supports/{revision_id}/warnings")
def get_support_warnings(revision_id: int, db: Session = Depends(get_db)):
    return support_warnings(db, revision_id)


@app.post("/api/supports/{revision_id}/resources/library", status_code=201)
def add_support_library(revision_id: int, payload: AddLibraryResource, db: Session = Depends(get_db)):
    copy_library_to_support(db, revision_id, payload.resource_version_id)
    return support_detail(db, revision_id)


@app.post("/api/supports/{revision_id}/resources/local", status_code=201)
def add_support_local(revision_id: int, payload: AddLocalResource, db: Session = Depends(get_db)):
    add_local_to_support(db, revision_id, payload.title, payload.block_type, payload.content_latex)
    return support_detail(db, revision_id)


@app.put("/api/supports/{revision_id}/blocks/{block_id}")
def update_support_block(revision_id: int, block_id: int, payload: BlockUpdate, db: Session = Depends(get_db)):
    revision = db.get(m.LearnerSupportRevision, revision_id)
    require_draft(revision)
    block = db.execute(select(m.SupportBlockInstance).join(m.SupportResourceInstance).where(m.SupportBlockInstance.id == block_id, m.SupportResourceInstance.support_revision_id == revision_id)).scalar_one_or_none()
    if not block:
        raise HTTPException(404, "Bloc introuvable dans ce support.")
    if payload.title is not None:
        block.title = payload.title
    if payload.content_latex is not None:
        block.content_latex = payload.content_latex
    if payload.visible is not None:
        block.visible = payload.visible
    db.commit()
    return support_detail(db, revision_id)


@app.put("/api/supports/{revision_id}/blocks/{block_id}/position")
def move_support_block(revision_id: int, block_id: int, payload: PositionUpdate, db: Session = Depends(get_db)):
    revision = db.get(m.LearnerSupportRevision, revision_id)
    require_draft(revision)
    block = db.execute(
        select(m.SupportBlockInstance)
        .join(m.SupportResourceInstance)
        .where(
            m.SupportBlockInstance.id == block_id,
            m.SupportResourceInstance.support_revision_id == revision_id,
        )
    ).scalar_one_or_none()
    if not block:
        raise HTTPException(404, "Bloc introuvable dans ce support.")
    siblings = db.scalars(
        select(m.SupportBlockInstance)
        .where(m.SupportBlockInstance.support_resource_instance_id == block.support_resource_instance_id)
        .order_by(m.SupportBlockInstance.position)
    ).all()
    index = siblings.index(block)
    target_index = index - 1 if payload.direction == "UP" else index + 1
    if target_index < 0 or target_index >= len(siblings):
        return support_detail(db, revision_id)
    target = siblings[target_index]
    block.position, target.position = 100000 + block.position, 200000 + target.position
    db.flush()
    block.position, target.position = target.position - 200000, block.position - 100000
    db.commit()
    return support_detail(db, revision_id)


@app.post("/api/supports/{revision_id}/finalize")
def finalize_support(revision_id: int, db: Session = Depends(get_db)):
    detail = support_detail(db, revision_id)
    teacher_only = {"EXPECTED_RESULT", "EXPECTED_TRACE", "SOLUTION", "CORRECTION", "TEACHER_NOTE"}
    printable = [
        block
        for resource in detail["resources"]
        for block in resource["blocks"]
        if block["visible"] and block["block_type"] not in teacher_only
    ]
    if not printable:
        raise HTTPException(409, "Ajoutez au moins un bloc visible destiné aux élèves avant de finaliser le support.")
    finalize_revision(db, "LEARNER", revision_id)
    return support_detail(db, revision_id)


@app.post("/api/supports/{revision_id}/new-revision", status_code=201)
def revise_support(revision_id: int, db: Session = Depends(get_db)):
    revision = new_support_revision(db, revision_id)
    return support_detail(db, revision.id)


@app.post("/api/supports/{revision_id}/create-teacher-sheet", status_code=201)
def create_teacher_sheet_from_support(revision_id: int, payload: SheetFromSupportCreate, db: Session = Depends(get_db)):
    revision = create_sheet_from_support(
        db,
        revision_id,
        payload.selected_block_ids,
        title=payload.title,
        instruction_ids=payload.instruction_ids,
        duration_minutes=payload.duration_minutes,
        class_label=payload.class_label,
        part_label=payload.part_label,
    )
    return sheet_detail(db, revision.id)


@app.post("/api/exports", status_code=201)
def create_export(payload: ExportCreate, db: Session = Depends(get_db)):
    try:
        record = export_document(db, payload.document_family, payload.revision_id, payload.target)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    return {"id": record.id, "family": record.document_family, "status": record.status, "file_path": record.file_path, "download_url": f"/exports/{Path(record.file_path).name}"}


@app.get("/api/exports")
def exports(db: Session = Depends(get_db)):
    rows = db.scalars(select(m.DocumentExport).order_by(m.DocumentExport.created_at.desc())).all()
    return [{"id": row.id, "family": row.document_family, "status": row.status, "file_path": row.file_path, "created_at": row.created_at.isoformat()} for row in rows]


@app.post("/api/teaching-sessions", status_code=201)
def record_teaching_session(payload: TeachingSessionCreate, db: Session = Depends(get_db)):
    revision = db.get(m.TeacherSheetRevision, payload.teacher_revision_id)
    if not revision or revision.status != "FINALIZED":
        raise HTTPException(409, "Seule une fiche finalisée peut être marquée comme déroulée.")
    session = m.TeachingSession(teacher_revision_id=revision.id, taught_on=payload.taught_on, class_label=payload.class_label, notes=payload.notes)
    db.add(session)
    db.flush()
    segments = db.scalars(select(m.SessionCurriculumSegment).where(m.SessionCurriculumSegment.teacher_revision_id == revision.id)).all()
    per_segment = payload.actual_minutes // max(1, len(segments))
    for position, segment in enumerate(segments, 1):
        db.add(m.ExecutedCurriculumSegment(teaching_session_id=session.id, session_curriculum_segment_id=segment.id, status=payload.status, actual_minutes=per_segment, position=position))
    db.commit()
    return {"id": session.id, "status": "RECORDED"}


@app.post("/api/support-uses", status_code=201)
def record_support_use(payload: SupportUseCreate, db: Session = Depends(get_db)):
    revision = db.get(m.LearnerSupportRevision, payload.support_revision_id)
    if not revision or revision.status != "FINALIZED":
        raise HTTPException(409, "Seul un support finalisé peut être marqué comme utilisé.")
    use = m.SupportUse(**payload.model_dump())
    db.add(use)
    db.commit()
    return {"id": use.id, "status": "RECORDED"}


@app.get("/api/progress")
def progress(db: Session = Depends(get_db)):
    rows = db.execute(
        select(m.InstructionGuide, func.count(m.ExecutedCurriculumSegment.id), func.coalesce(func.sum(m.ExecutedCurriculumSegment.actual_minutes), 0))
        .outerjoin(m.SessionCurriculumSegment, m.SessionCurriculumSegment.instruction_id == m.InstructionGuide.id)
        .outerjoin(m.ExecutedCurriculumSegment, m.ExecutedCurriculumSegment.session_curriculum_segment_id == m.SessionCurriculumSegment.id)
        .group_by(m.InstructionGuide.id)
        .order_by(m.InstructionGuide.position)
    ).all()
    instruction_rows = [{"instruction_id": instruction.id, "code": instruction.code, "text": instruction.text, "executions": count, "actual_minutes": minutes, "status": "DONE" if count else "NOT_STARTED"} for instruction, count, minutes in rows]
    allocations = db.execute(select(m.CurriculumTimeAllocation, m.SourceDocument).join(m.SourceDocument).order_by(m.CurriculumTimeAllocation.hours)).all()
    values = sorted({allocation.hours for allocation, _ in allocations})
    normative = {
        "status": "UNRESOLVED_NORMATIVE_ALLOCATION" if len(values) > 1 else "DETERMINED",
        "values": [{"hours": allocation.hours, "source": source.code} for allocation, source in allocations],
        "remaining_hours": None if len(values) > 1 else max(0, values[0] - sum(item["actual_minutes"] for item in instruction_rows) / 60) if values else None,
    }
    return {"instructions": instruction_rows, "normative_allocation": normative}
