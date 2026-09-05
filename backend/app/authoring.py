"""Curriculum composition with explicit provenance and human finalization."""
import json
import random
from uuid import uuid4
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from . import models as m
from .database import get_db
from .services import require_draft, sheet_detail

router = APIRouter(prefix="/api/authoring", tags=["authoring"])
SOURCE_KINDS = {"OFFICIAL_PROGRAM", "OFFICIAL_GUIDE", "INSPECTOR_VALIDATED", "TEACHER_COMMUNITY", "BOOK_SOURCE", "LOCAL_TEACHER", "DEMO_UNSOURCED"}
TEACHER_ONLY = {"EXPECTED_RESPONSE", "EXPECTED_RESULT", "EXPECTED_TRACE", "SOLUTION", "CORRECTION", "TEACHER_NOTE"}
BLOCK_TYPES = {"INSTRUCTION", "CONSIGNE", "STATEMENT", "DEFINITION", "PROPERTY", "FORMULA", "METHOD", "REMARK", "APPLICATION", "FIGURE", "EXPECTED_RESPONSE"}


class Scope(BaseModel):
    programme_id: int
    scope: Literal["CLASS", "SA", "SEQUENCE", "INSTRUCTION"] = "SEQUENCE"
    scope_id: int


class Compose(Scope):
    title: str = Field(min_length=1)
    instruction_ids: list[int] = Field(default_factory=list)
    automatic: bool = False
    allow_demo: bool = False
    seed: int | None = None
    local: dict[str, str] = Field(default_factory=dict)
    reused_local_fields: list[str] = Field(default_factory=list)


class Selection(BaseModel):
    instruction_id: int
    resource_version_id: int
    allow_demo: bool = False


class ResourceBlock(BaseModel):
    block_type: str
    title: str
    content_latex: str = Field(min_length=1)


class ResourceCreate(BaseModel):
    title: str = Field(min_length=1)
    level: str
    instruction_ids: list[int] = Field(min_length=1)
    source_kind: Literal["OFFICIAL_PROGRAM", "OFFICIAL_GUIDE", "INSPECTOR_VALIDATED", "TEACHER_COMMUNITY", "BOOK_SOURCE", "LOCAL_TEACHER", "DEMO_UNSOURCED"] = "LOCAL_TEACHER"
    source_ref: str = Field(min_length=1)
    source_version: str = Field(min_length=1)
    source_document_id: int | None = None
    page_label: str = ""
    author: str = ""
    validation_status: Literal["NON_REVU", "COMMUNITY", "INSPECTOR_VALIDATED", "OFFICIAL"] = "NON_REVU"
    validation_ref: str = ""
    notes: str = ""
    blocks: list[ResourceBlock] = Field(min_length=1)


def source_info(db, source, page="", scope="", scope_id=None):
    return {"source_kind": {"PROGRAMME": "OFFICIAL_PROGRAM", "GUIDE": "OFFICIAL_GUIDE"}.get(source.document_type, "BOOK_SOURCE"), "source_id": source.id, "source_ref": source.title, "source_version": source.sha256 or source.code, "page_label": page, "scope": scope, "scope_id": scope_id}


def occurrence(db, entity_type, entity_id):
    result = []
    for row in db.scalars(select(m.SourceOccurrence).where(m.SourceOccurrence.entity_type == entity_type, m.SourceOccurrence.entity_id == entity_id)):
        source = db.get(m.SourceDocument, row.source_document_id)
        if source:
            result.append(source_info(db, source, row.page_label, entity_type, entity_id))
    return result


def resolve_scope(db, scope):
    programme = db.get(m.ProgrammeVersion, scope.programme_id)
    if not programme:
        raise HTTPException(404, "Programme introuvable.")
    situations = list(db.scalars(select(m.SituationApprentissage).where(m.SituationApprentissage.programme_version_id == programme.id).order_by(m.SituationApprentissage.position)))
    sequences = list(db.scalars(select(m.Sequence).where(m.Sequence.situation_id.in_([s.id for s in situations])).order_by(m.Sequence.position)))
    instructions = list(db.scalars(select(m.InstructionGuide).where(m.InstructionGuide.sequence_id.in_([s.id for s in sequences])).order_by(m.InstructionGuide.position, m.InstructionGuide.id)))
    if scope.scope == "CLASS" and scope.scope_id != programme.id:
        raise HTTPException(422, "Classe et programme incompatibles.")
    if scope.scope == "SA":
        situations = [s for s in situations if s.id == scope.scope_id]
        sequences = [s for s in sequences if s.situation_id in {x.id for x in situations}]
    elif scope.scope == "SEQUENCE":
        sequences = [s for s in sequences if s.id == scope.scope_id]
    elif scope.scope == "INSTRUCTION":
        instructions = [i for i in instructions if i.id == scope.scope_id]
        sequences = [s for s in sequences if s.id in {i.sequence_id for i in instructions}]
    instructions = [i for i in instructions if i.sequence_id in {s.id for s in sequences}]
    sequence_order = {s.id: index for index, s in enumerate(sequences)}
    instructions.sort(key=lambda i: (sequence_order[i.sequence_id], i.position, i.id))
    situations = [s for s in situations if s.id in {q.situation_id for q in sequences}]
    if not instructions:
        raise HTTPException(422, "Aucune instruction disponible dans ce périmètre.")
    return programme, situations, sequences, instructions


@router.get("/curriculum")
def curriculum(db: Session = Depends(get_db)):
    result = []
    for p in db.scalars(select(m.ProgrammeVersion).where(m.ProgrammeVersion.status == "ACTIVE").order_by(m.ProgrammeVersion.id)):
        situations = []
        for s in db.scalars(select(m.SituationApprentissage).where(m.SituationApprentissage.programme_version_id == p.id).order_by(m.SituationApprentissage.position)):
            sequences = []
            for q in db.scalars(select(m.Sequence).where(m.Sequence.situation_id == s.id).order_by(m.Sequence.position)):
                guide = db.get(m.GuideVersion, q.guide_version_id)
                instructions = [{"id": i.id, "code": i.code, "text": i.text, "position": i.position, "sources": occurrence(db, "InstructionGuide", i.id)} for i in db.scalars(select(m.InstructionGuide).where(m.InstructionGuide.sequence_id == q.id).order_by(m.InstructionGuide.position))]
                sequences.append({"id": q.id, "title": q.title, "code": q.code, "instructions": instructions, "guide_version": guide.code})
            situations.append({"id": s.id, "title": s.title, "code": s.code, "sequences": sequences})
        result.append({"id": p.id, "title": p.title, "level": p.level, "version": p.code, "situations": situations})
    return result


def autofill(db, scope, selected_ids=None):
    programme, situations, sequences, instructions = resolve_scope(db, scope)
    if selected_ids:
        if not set(selected_ids) <= {i.id for i in instructions}:
            raise HTTPException(422, "Instruction extérieure au périmètre.")
        instructions = [i for i in instructions if i.id in selected_ids]
        sequences = [s for s in sequences if s.id in {i.sequence_id for i in instructions}]
        situations = [s for s in situations if s.id in {q.situation_id for q in sequences}]
    identification = {"discipline": "Mathématiques", "classe": programme.level, "SA": ", ".join(s.code for s in situations), "titre SA": "; ".join(s.title for s in situations), "séquence": ", ".join(f"Séquence {s.position}" for s in sequences), "titre séquence": "; ".join(s.title for s in sequences)}
    provenance = {}
    for key in identification:
        refs = []
        if key in {"séquence", "titre séquence"}:
            refs = [ref for q in sequences for ref in occurrence(db, "Sequence", q.id)]
        else:
            refs = [ref for s in situations for ref in occurrence(db, "SituationApprentissage", s.id)]
        provenance["identification." + key] = {"origin": "CURRICULUM_DERIVED", "sources": refs}
    scopes = {"CLASS": {programme.id}, "SA": {s.id for s in situations}, "SEQUENCE": {s.id for s in sequences}, "INSTRUCTION": {i.id for i in instructions}}
    planning, attributes = {}, []
    for attr in db.scalars(select(m.CurriculumAttribute).where(m.CurriculumAttribute.programme_version_id == programme.id).order_by(m.CurriculumAttribute.id)):
        if attr.scope_id not in scopes.get(attr.scope, set()):
            continue
        src = source_info(db, db.get(m.SourceDocument, attr.source_document_id), attr.page_label, attr.scope, attr.scope_id)
        src["edition"] = attr.source_version
        attributes.append({"id": attr.id, "field": attr.field, "value": attr.value, **src})
        if attr.field in {"pays", "discipline", "série"}:
            identification[attr.field] = attr.value
            provenance["identification." + attr.field] = {"origin": "CURRICULUM_DERIVED", "sources": [src]}
            continue
        planning[attr.field] = (planning.get(attr.field, "") + "\n" + attr.value).strip()
        entry = provenance.setdefault("planning." + attr.field, {"origin": "CURRICULUM_DERIVED", "sources": []})
        entry["sources"].append(src)
    durations = [{"hours": row.hours, **source_info(db, db.get(m.SourceDocument, row.source_document_id), scope="SA", scope_id=row.situation_id)} for row in db.scalars(select(m.CurriculumTimeAllocation).where(m.CurriculumTimeAllocation.situation_id.in_(scopes["SA"])))]
    if len(situations) == 1 and durations and len({d["hours"] for d in durations}) == 1:
        identification["durée curriculaire SA"] = f'{durations[0]["hours"]:g} h'
        provenance["identification.durée curriculaire SA"] = {"origin": "CURRICULUM_DERIVED", "sources": durations}
    return {"identification": identification, "planning": planning, "provenance": provenance, "attributes": attributes, "durations": durations, "duration_conflict": len({d["hours"] for d in durations}) > 1, "instructions": [{"id": i.id, "text": i.text, "code": i.code, "sources": occurrence(db, "InstructionGuide", i.id)} for i in instructions]}


@router.post("/preview")
def preview(payload: Scope, db: Session = Depends(get_db)):
    return autofill(db, payload)


def resource_provenance(db, version, resource):
    saved = json.loads(version.provenance_json or "{}")
    if saved:
        return saved
    sources = occurrence(db, "PedagogicalResourceVersion", version.id)
    # Historical source-derived transcriptions are explicitly labelled adaptations.
    return {"source_kind": sources[0]["source_kind"] if sources else ("DEMO_UNSOURCED" if resource.provenance_kind == "DEMO_NON_SOURCE" else "LOCAL_TEACHER"), "source_ref": sources[0]["source_ref"] if sources else "Ressource historique", "source_version": sources[0]["source_version"] if sources else str(version.version_number), "validation_status": "NON_REVU", "adaptation": bool(sources), "sources": sources, "author": ""}


def priority(provenance):
    kind = provenance["source_kind"]
    if kind in {"OFFICIAL_GUIDE", "OFFICIAL_PROGRAM"}:
        return 0
    if provenance.get("validation_status") == "INSPECTOR_VALIDATED" or kind == "INSPECTOR_VALIDATED":
        return 1
    return {"TEACHER_COMMUNITY": 2, "BOOK_SOURCE": 3, "LOCAL_TEACHER": 4, "DEMO_UNSOURCED": 5}.get(kind, 5)


def candidates(db, instruction_id, allow_demo=False):
    instruction = db.get(m.InstructionGuide, instruction_id)
    if not instruction:
        raise HTTPException(404, "Instruction introuvable.")
    sequence = db.get(m.Sequence, instruction.sequence_id)
    situation = db.get(m.SituationApprentissage, sequence.situation_id)
    programme = db.get(m.ProgrammeVersion, situation.programme_version_id)
    result = []
    for mapping in db.scalars(select(m.ResourceInstructionMapping).where(m.ResourceInstructionMapping.instruction_id == instruction_id)):
        if mapping.validation_status in {"REJECTED", "WITHDRAWN"}:
            continue
        version = db.get(m.PedagogicalResourceVersion, mapping.resource_version_id)
        resource = db.get(m.PedagogicalResource, version.resource_id)
        if version.status != "AVAILABLE" or resource.level != programme.level:
            continue
        prov = resource_provenance(db, version, resource)
        if prov["source_kind"] == "DEMO_UNSOURCED" and not allow_demo:
            continue
        blocks = [{"id": b.id, "block_type": b.block_type, "title": b.title, "content_latex": b.content_latex} for b in db.scalars(select(m.PedagogicalBlock).where(m.PedagogicalBlock.resource_version_id == version.id).order_by(m.PedagogicalBlock.position))]
        if not any(b["block_type"] not in TEACHER_ONLY for b in blocks):
            continue
        result.append({"id": version.id, "title": version.title, "version": version.version_number, "provenance": prov, "priority": priority(prov), "blocks": blocks, "instruction_ids": list(db.scalars(select(m.ResourceInstructionMapping.instruction_id).where(m.ResourceInstructionMapping.resource_version_id == version.id)))})
    return sorted(result, key=lambda x: (x["priority"], x["id"]))


@router.get("/instructions/{instruction_id}/candidates")
def list_candidates(instruction_id: int, allow_demo: bool = False, db: Session = Depends(get_db)):
    return candidates(db, instruction_id, allow_demo)


@router.post("/resources", status_code=201)
def add_resource(payload: ResourceCreate, db: Session = Depends(get_db)):
    from .services import curriculum_level_for_instruction_ids
    ids = set(payload.instruction_ids)
    found = list(db.scalars(select(m.InstructionGuide.id).where(m.InstructionGuide.id.in_(ids))))
    if set(found) != ids or curriculum_level_for_instruction_ids(db, found) != payload.level:
        raise HTTPException(422, "Classe ou instructions incompatibles.")
    if any(b.block_type not in BLOCK_TYPES for b in payload.blocks):
        raise HTTPException(422, "Type de bloc non reconnu.")
    if payload.source_kind.startswith("OFFICIAL_"):
        source = db.get(m.SourceDocument, payload.source_document_id) if payload.source_document_id else None
        expected = "GUIDE" if payload.source_kind == "OFFICIAL_GUIDE" else "PROGRAMME"
        if not source or source.document_type != expected or not source.sha256 or not payload.page_label:
            raise HTTPException(422, "Une source officielle existante, son empreinte et sa page sont requises.")
    if payload.validation_status == "OFFICIAL" and not payload.source_kind.startswith("OFFICIAL_"):
        raise HTTPException(422, "Une ressource communautaire ne devient pas officielle.")
    if (payload.validation_status == "INSPECTOR_VALIDATED" or payload.source_kind == "INSPECTOR_VALIDATED") and not payload.validation_ref:
        raise HTTPException(422, "Indiquez la référence de validation de l’inspection.")
    resource = m.PedagogicalResource(code="RES-" + uuid4().hex, title=payload.title, level=payload.level, resource_type=payload.blocks[0].block_type, provenance_kind="DEMO_NON_SOURCE" if payload.source_kind == "DEMO_UNSOURCED" else "SOURCED", structure_kind="COMPOSITE" if len(payload.blocks) > 1 else "ATOMIC")
    db.add(resource)
    db.flush()
    prov = payload.model_dump(exclude={"title", "level", "instruction_ids", "blocks"})
    if payload.source_kind.startswith("OFFICIAL_"):
        # A reference proves the document's identity, not transcription fidelity.
        prov.update(source_info(db, source, payload.page_label))
        prov["adaptation"] = True
        prov["validation_status"] = "NON_REVU"
    version = m.PedagogicalResourceVersion(resource_id=resource.id, title=payload.title, provenance_json=json.dumps(prov, ensure_ascii=False))
    db.add(version)
    db.flush()
    for pos, block in enumerate(payload.blocks, 1):
        db.add(m.PedagogicalBlock(resource_version_id=version.id, position=pos, **block.model_dump()))
    for instruction_id in ids:
        db.add(m.ResourceInstructionMapping(resource_version_id=version.id, instruction_id=instruction_id, validation_status="MANUAL_DECLARATION"))
    db.commit()
    return {"id": version.id, "provenance": prov}


def select_resource(db, revision, instruction_id, candidate, origin):
    state = json.loads(revision.authoring_json)
    previous = state.setdefault("selections", {}).get(str(instruction_id))
    if previous:
        old_id = previous["instance_id"]
        # Hide the previous copy; retain its provenance and edits for review.
        shared = any(key != str(instruction_id) and value["instance_id"] == old_id for key, value in state["selections"].items())
        if not shared:
            for block in db.scalars(select(m.SheetBlockInstance).where(m.SheetBlockInstance.resource_instance_id == old_id)):
                block.visible = False
        state.setdefault("selection_history", []).append(previous)
    position = (db.scalar(select(func.max(m.SheetResourceInstance.position)).where(m.SheetResourceInstance.teacher_revision_id == revision.id)) or 0) + 1
    instance = m.SheetResourceInstance(teacher_revision_id=revision.id, origin="LIBRARY_DERIVED", source_resource_version_id=candidate["id"], title=candidate["title"], position=position, adaptation_note="Choix enseignant" if origin == "COMMUNITY_SELECTED" else "Composition automatique, à relire")
    db.add(instance)
    db.flush()
    flow_position = (db.scalar(select(func.max(m.FlowItem.position)).where(m.FlowItem.teacher_revision_id == revision.id)) or 0) + 1
    for pos, block in enumerate(candidate["blocks"], 1):
        copied = m.SheetBlockInstance(resource_instance_id=instance.id, source_block_id=block["id"], block_type=block["block_type"], title=block["title"], content_latex=block["content_latex"], visible=True, position=pos)
        db.add(copied)
        db.flush()
        db.add(m.FlowItem(teacher_revision_id=revision.id, block_instance_id=copied.id, phase_code="REALISATION", position=flow_position + pos - 1, duration_minutes=0, expected_result_latex=""))
    state["selections"][str(instruction_id)] = {"instruction_id": instruction_id, "resource_version_id": candidate["id"], "instance_id": instance.id, "origin": origin, "provenance": candidate["provenance"], "version": candidate["version"]}
    revision.authoring_json = json.dumps(state, ensure_ascii=False)
    db.flush()


@router.post("/compose", status_code=201)
def compose(payload: Compose, db: Session = Depends(get_db)):
    return compose_sheet(payload, db)


def compose_sheet(payload: Compose, db: Session, *, commit=True):
    if payload.scope == "CLASS":
        raise HTTPException(422, "Choisissez une SA, une séquence ou une instruction pour composer une fiche.")
    filled = autofill(db, payload, payload.instruction_ids)
    pools = {i["id"]: candidates(db, i["id"], payload.allow_demo) for i in filled["instructions"]}
    if payload.automatic and any(not pool for pool in pools.values()):
        missing = [i["code"] for i in filled["instructions"] if not pools[i["id"]]]
        raise HTTPException(422, "Aucune ressource compatible pour : " + ", ".join(missing) + ". Ajoutez une consigne locale ou réduisez le périmètre.")
    identification = {k: "" for k in ["établissement", "année scolaire", "date", "effectif", "nombre de groupes", "nom du professeur", "numéro fiche pédagogique", "numéro de séance", "durée de la séance"]}
    unknown = set(payload.local) - set(identification)
    if unknown:
        raise HTTPException(422, "Les valeurs locales ne peuvent pas remplacer le curriculum.")
    if not set(payload.reused_local_fields) <= set(payload.local):
        raise HTTPException(422, "Une valeur réutilisée doit appartenir aux données locales transmises.")
    identification.update(payload.local)
    identification.update(filled["identification"])
    identification["titre du cours"] = payload.title
    planning = {k: "" for k in ["compétence transdisciplinaire", "stratégie objet d'apprentissage", "stratégies d'enseignement/apprentissage", "matériels apprenants", "matériels enseignant", "durée"]}
    planning.update(filled["planning"])
    state = {"scope": payload.model_dump(include={"programme_id", "scope", "scope_id"}), "provenance": filled["provenance"], "durations": filled["durations"], "duration_conflict": filled["duration_conflict"], "selections": {}, "seed": payload.seed, "mode": "AUTOMATIC" if payload.automatic else "MANUAL"}
    for section, values in [("identification", identification), ("planning", planning)]:
        for key in values:
            state["provenance"].setdefault(section + "." + key, {"origin": "MANUAL_USER_ENTRY", "sources": []})
    for key in payload.reused_local_fields:
        state["provenance"]["identification." + key] = {"origin": "REUSED_TEACHER_DATA", "sources": [{"source_kind": "LOCAL_TEACHER", "source_ref": "Profil local du navigateur", "source_version": "1", "scope": "TEACHER"}]}
    sheet = m.TeacherSessionSheet(code="FICHE-" + uuid4().hex[:12].upper(), title=payload.title, level=identification["classe"])
    db.add(sheet)
    db.flush()
    revision = m.TeacherSheetRevision(sheet_id=sheet.id, revision_number=1, identification_json=json.dumps(identification, ensure_ascii=False), planning_json=json.dumps(planning, ensure_ascii=False), authoring_json=json.dumps(state, ensure_ascii=False))
    db.add(revision)
    db.flush()
    rng = random.Random(payload.seed)
    chosen = {}
    for pos, instruction in enumerate(filled["instructions"], 1):
        db.add(m.SessionCurriculumSegment(teacher_revision_id=revision.id, instruction_id=instruction["id"], position=pos))
        if payload.automatic:
            pool = pools[instruction["id"]]
            best = [c for c in pool if c["priority"] == pool[0]["priority"]]
            candidate = rng.choice(best)
            if candidate["id"] in chosen:
                state = json.loads(revision.authoring_json)
                state["selections"][str(instruction["id"])] = {**chosen[candidate["id"]], "instruction_id": instruction["id"]}
                revision.authoring_json = json.dumps(state, ensure_ascii=False)
            else:
                select_resource(db, revision, instruction["id"], candidate, "AUTO_SELECTED")
                chosen[candidate["id"]] = json.loads(revision.authoring_json)["selections"][str(instruction["id"])]
    if commit:
        db.commit()
    else:
        db.flush()
    return sheet_detail(db, revision.id)


@router.put("/sheets/{revision_id}/selection")
def replace_selection(revision_id: int, payload: Selection, db: Session = Depends(get_db)):
    revision = db.get(m.TeacherSheetRevision, revision_id)
    require_draft(revision)
    if not db.scalar(select(m.SessionCurriculumSegment.id).where(m.SessionCurriculumSegment.teacher_revision_id == revision_id, m.SessionCurriculumSegment.instruction_id == payload.instruction_id)):
        raise HTTPException(422, "Instruction extérieure à cette fiche.")
    if not json.loads(revision.authoring_json or "{}"):
        raise HTTPException(422, "Cette fiche utilise le parcours historique.")
    candidate = next((c for c in candidates(db, payload.instruction_id, payload.allow_demo) if c["id"] == payload.resource_version_id), None)
    if not candidate:
        raise HTTPException(422, "Consigne incompatible avec cette instruction.")
    select_resource(db, revision, payload.instruction_id, candidate, "COMMUNITY_SELECTED")
    db.commit()
    return sheet_detail(db, revision_id)


@router.post("/sheets/{revision_id}/learner-support", status_code=201)
def create_learner_support(revision_id: int, db: Session = Depends(get_db)):
    """Copy the current visible lesson into a separately editable learner draft."""
    from .services import support_detail
    detail = sheet_detail(db, revision_id)
    instruction_ids = [s["instruction_id"] for s in detail["segments"]]
    instructions = list(db.scalars(select(m.InstructionGuide).where(m.InstructionGuide.id.in_(instruction_ids))))
    sequences = list(db.scalars(select(m.Sequence).where(m.Sequence.id.in_({i.sequence_id for i in instructions}))))
    situation_ids = {s.situation_id for s in sequences}
    if not sequences or len(situation_ids) != 1:
        raise HTTPException(422, "Le support doit couvrir une séquence ou une seule SA.")
    support = m.LearnerSupport(code="SUPPORT-" + uuid4().hex[:12].upper(), title=detail["title"], level=detail["curriculum_level"], sequence_id=sequences[0].id if len(sequences) == 1 else None, situation_id=next(iter(situation_ids)) if len(sequences) > 1 else None)
    db.add(support)
    db.flush()
    revision = m.LearnerSupportRevision(support_id=support.id, revision_number=1)
    db.add(revision)
    db.flush()
    lookup = {b["id"]: (resource, b) for resource in detail["resources"] for b in resource["blocks"]}
    position = 0
    for flow in detail["flow"]:
        if flow["block_instance_id"] not in lookup:
            continue
        resource, block = lookup[flow["block_instance_id"]]
        if not block["visible"] or block["block_type"] in TEACHER_ONLY | {"RESPONSE_SPACE", "ANSWER_SPACE"}:
            continue
        position += 1
        instance = m.SupportResourceInstance(support_revision_id=revision.id, origin=resource["origin"], source_resource_version_id=resource["source_resource_version_id"], title=block["title"], position=position)
        db.add(instance)
        db.flush()
        source_block = db.get(m.SheetBlockInstance, block["id"])
        db.add(m.SupportBlockInstance(support_resource_instance_id=instance.id, source_block_id=source_block.source_block_id, block_type=block["block_type"], title=block["title"], content_latex=block["content_latex"], position=1))
    if not position:
        db.rollback()
        raise HTTPException(422, "Ajoutez un contenu visible destiné aux apprenants.")
    db.commit()
    return support_detail(db, revision.id)
