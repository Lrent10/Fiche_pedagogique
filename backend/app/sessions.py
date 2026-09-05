"""P1: explicit planning, execution events and contextual coverage projection."""
import json
import re
import unicodedata
from datetime import date
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, StrictInt, field_validator, model_validator
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy.orm import Session

from . import models as m
from .authoring import Compose, compose_sheet
from .database import get_db
from .services import class_label_matches_level, require_draft, sheet_detail

router = APIRouter(prefix="/api/session-planning", tags=["sessions"])
WEEKLY_MASS = {"minutes": 360, "source": "Programme de mathématiques 4e examiné", "page": 12, "sha256": "7795dd2370db4c879187f5fcbc7247babcab2ab0a3fd9d9f579663d0114fd62d"}


class ContextInput(BaseModel):
    class_level: Literal["4e"] = "4e"
    class_label: str = Field(min_length=1, max_length=80)
    school_year: str
    teacher_actual_weekly_minutes: StrictInt | None = Field(default=None, gt=0)

    @field_validator("class_label")
    @classmethod
    def normalize_label(cls, value):
        value = " ".join(value.split())
        if not class_label_matches_level(value, "4e"):
            raise ValueError("Choisissez une subdivision de 4e, par exemple 4e A.")
        normalized = "".join(c for c in unicodedata.normalize("NFKD", value) if not unicodedata.combining(c))
        suffix = re.sub(r"^4\s*(?:eme|e)", "", normalized, flags=re.I).strip()
        return "4e" + (" " + suffix.upper() if suffix else "")

    @field_validator("school_year")
    @classmethod
    def normalize_year(cls, value):
        value = value.strip().replace("–", "-").replace("/", "-")
        if not re.fullmatch(r"\d{4}-\d{4}", value) or int(value[5:]) != int(value[:4]) + 1:
            raise ValueError("Année scolaire attendue : 2026-2027.")
        return value


class Durations(BaseModel):
    slot_minutes: StrictInt = Field(gt=0)
    break_minutes: StrictInt = Field(ge=0)
    default_break_minutes: StrictInt = Field(default=10, ge=0)
    break_override: bool = False

    @model_validator(mode="after")
    def validate_break(self):
        if self.break_minutes >= self.slot_minutes:
            raise ValueError("La pause doit être inférieure au créneau.")
        return self

    def snapshot(self):
        return {**self.model_dump(), "pedagogical_minutes": self.slot_minutes - self.break_minutes, "origin": "LOCAL_TEACHER", "profile_threshold_minutes": 120}


class PlanInput(BaseModel):
    class_context_id: int
    sequence_id: int
    planned_sequence_minutes: StrictInt | None = Field(default=None, gt=0)


class Preparation(BaseModel):
    instruction_ids: list[StrictInt] = Field(min_length=1)
    deferred_instruction_ids: list[StrictInt] = Field(default_factory=list)
    reactivate_instruction_ids: list[StrictInt] = Field(default_factory=list)
    durations: Durations


class CreateSession(Preparation):
    title: str = Field(min_length=1, max_length=255)
    expected_session_number: StrictInt = Field(ge=1)
    automatic: bool = False
    local: dict[str, str] = Field(default_factory=dict)


class InstructionResult(BaseModel):
    segment_id: StrictInt
    status: Literal["PARTIAL", "COVERED", "SKIPPED"]
    actual_minutes: StrictInt = Field(ge=0)


class Execution(BaseModel):
    teacher_revision_id: StrictInt
    taught_on: date
    results: list[InstructionResult] = Field(min_length=1)
    notes: str = ""


def get(db, model, id):
    row = db.get(model, id)
    if not row:
        raise HTTPException(404, "Élément introuvable.")
    return row


def commit_or_conflict(db):
    try:
        db.commit()
    except (IntegrityError, OperationalError) as exc:
        db.rollback()
        raise HTTPException(409, "Une autre sauvegarde a eu lieu. Rechargez puis réessayez.") from exc


@router.get("/contexts")
def contexts(db: Session = Depends(get_db)):
    return list(db.scalars(select(m.ClassContext).order_by(m.ClassContext.school_year.desc(), m.ClassContext.class_label)))


@router.post("/contexts", status_code=201)
def create_context(payload: ContextInput, db: Session = Depends(get_db)):
    row = m.ClassContext(**payload.model_dump())
    db.add(row)
    commit_or_conflict(db)
    return row


@router.put("/contexts/{context_id}/timetable")
def timetable(context_id: int, payload: ContextInput, db: Session = Depends(get_db)):
    row = get(db, m.ClassContext, context_id)
    if (row.class_level, row.class_label, row.school_year) != (payload.class_level, payload.class_label, payload.school_year):
        raise HTTPException(422, "La classe et l’année d’un contexte existant ne changent pas.")
    row.teacher_actual_weekly_minutes = payload.teacher_actual_weekly_minutes
    commit_or_conflict(db)
    return row


@router.post("/plans", status_code=201)
def create_plan(payload: PlanInput, db: Session = Depends(get_db)):
    context = get(db, m.ClassContext, payload.class_context_id)
    sequence = get(db, m.Sequence, payload.sequence_id)
    situation = get(db, m.SituationApprentissage, sequence.situation_id)
    programme = get(db, m.ProgrammeVersion, situation.programme_version_id)
    if programme.level != context.class_level or programme.level != "4e" or programme.status != "ACTIVE":
        raise HTTPException(422, "Cette séquence ne relève pas du programme 4e actif.")
    existing = db.scalar(select(m.SequencePlan).where(m.SequencePlan.class_context_id == context.id, m.SequencePlan.sequence_id == sequence.id))
    if existing:
        return existing
    row = m.SequencePlan(**payload.model_dump())
    db.add(row)
    commit_or_conflict(db)
    return row


@router.put("/plans/{plan_id}/duration")
def update_plan(plan_id: int, payload: PlanInput, db: Session = Depends(get_db)):
    row = get(db, m.SequencePlan, plan_id)
    if (row.class_context_id, row.sequence_id) != (payload.class_context_id, payload.sequence_id):
        raise HTTPException(422, "Le contexte et la séquence ne changent pas.")
    row.planned_sequence_minutes = payload.planned_sequence_minutes
    commit_or_conflict(db)
    return row


def coverage(db, context_id, sequence_id=None):
    get(db, m.ClassContext, context_id)
    query = select(m.InstructionGuide).order_by(m.InstructionGuide.sequence_id, m.InstructionGuide.position, m.InstructionGuide.id)
    if sequence_id is not None:
        query = query.where(m.InstructionGuide.sequence_id == sequence_id)
    events = db.execute(select(m.ExecutedCurriculumSegment, m.SessionCurriculumSegment.instruction_id, m.TeachingSession)
        .join(m.SessionCurriculumSegment, m.ExecutedCurriculumSegment.session_curriculum_segment_id == m.SessionCurriculumSegment.id)
        .join(m.TeachingSession, m.ExecutedCurriculumSegment.teaching_session_id == m.TeachingSession.id)
        .join(m.PlannedSession, m.TeachingSession.planned_session_id == m.PlannedSession.id)
        .join(m.SequencePlan, m.PlannedSession.sequence_plan_id == m.SequencePlan.id)
        .where(m.SequencePlan.class_context_id == context_id)
        .order_by(m.TeachingSession.taught_on, m.TeachingSession.id, m.ExecutedCurriculumSegment.position)).all()
    result = []
    for instruction in db.scalars(query):
        relevant = [(event, session) for event, iid, session in events if iid == instruction.id and event.status in {"COVERED", "PARTIAL", "SKIPPED"}]
        statuses = {event.status for event, _ in relevant}
        status = next((s for s in ["COVERED", "PARTIAL", "SKIPPED"] if s in statuses), "NOT_STARTED")
        result.append({"instruction_id": instruction.id, "code": instruction.code, "text": instruction.text, "status": status,
            "last_result": relevant[-1][0].status if relevant else None, "previously_skipped": "SKIPPED" in statuses,
            "actual_minutes": sum(e.actual_minutes for e, _ in relevant),
            "events": [{"execution_id": s.id, "result_id": e.id, "status": e.status, "actual_minutes": e.actual_minutes, "taught_on": s.taught_on} for e, s in relevant]})
    return result


@router.get("/contexts/{context_id}/coverage")
def read_coverage(context_id: int, sequence_id: int | None = None, db: Session = Depends(get_db)):
    return {"instructions": coverage(db, context_id, sequence_id), "curriculum_weekly_mass": WEEKLY_MASS}


@router.get("/plans/{plan_id}")
def plan_detail(plan_id: int, db: Session = Depends(get_db)):
    plan = get(db, m.SequencePlan, plan_id)
    sessions = []
    for row in db.scalars(select(m.PlannedSession).where(m.PlannedSession.sequence_plan_id == plan_id).order_by(m.PlannedSession.session_number_within_sequence)):
        rev = db.scalar(select(m.TeacherSheetRevision).where(m.TeacherSheetRevision.sheet_id == row.sheet_id).order_by(m.TeacherSheetRevision.revision_number.desc()))
        sessions.append({"id": row.id, "number": row.session_number_within_sequence, "sheet_id": row.sheet_id, "revision_id": rev.id, "status": rev.status,
            "instruction_ids": list(db.scalars(select(m.SessionCurriculumSegment.instruction_id).where(m.SessionCurriculumSegment.teacher_revision_id == rev.id)))})
    return {"id": plan.id, "class_context_id": plan.class_context_id, "sequence_id": plan.sequence_id, "planned_sequence_minutes": plan.planned_sequence_minutes, "next_session_number": max([s["number"] for s in sessions], default=0) + 1, "sessions": sessions}


@router.get("/plans/{plan_id}/recommendation")
def recommend(plan_id: int, include_covered: bool = False, db: Session = Depends(get_db)):
    plan = get(db, m.SequencePlan, plan_id)
    rows = coverage(db, plan.class_context_id, plan.sequence_id)
    planned = plan_detail(plan_id, db)["sessions"]
    executed = set(db.scalars(select(m.TeachingSession.planned_session_id).where(m.TeachingSession.planned_session_id.is_not(None))))
    for row in rows:
        row["planned_in_sessions"] = [s["number"] for s in planned if s["id"] not in executed and row["instruction_id"] in s["instruction_ids"]]
        row["eligible"] = row["status"] != "COVERED" or include_covered
    return sorted(rows, key=lambda r: {"PARTIAL": 0, "NOT_STARTED": 1, "SKIPPED": 1, "COVERED": 2}[r["status"]])


def validate_preparation(db, plan, payload):
    allowed = set(db.scalars(select(m.InstructionGuide.id).where(m.InstructionGuide.sequence_id == plan.sequence_id)))
    selected = set(payload.instruction_ids)
    deferred = set(payload.deferred_instruction_ids)
    if len(selected) != len(payload.instruction_ids) or not selected <= allowed or not deferred <= allowed or selected & deferred:
        raise HTTPException(422, "Choix d’instructions incohérent avec la séquence ou le report.")
    covered = {r["instruction_id"] for r in coverage(db, plan.class_context_id, plan.sequence_id) if r["status"] == "COVERED"}
    if not set(payload.reactivate_instruction_ids) <= selected or not (covered & selected) <= set(payload.reactivate_instruction_ids):
        raise HTTPException(422, "Confirmez explicitement la reprise des instructions déjà couvertes.")


def snapshot(db, revision, plan, payload, number):
    context = get(db, m.ClassContext, plan.class_context_id)
    state = json.loads(revision.authoring_json)
    state["session_preparation"] = {"durations": payload.durations.snapshot(), "planned_sequence_minutes": plan.planned_sequence_minutes,
        "deferred_instruction_ids": payload.deferred_instruction_ids, "reactivate_instruction_ids": payload.reactivate_instruction_ids,
        "class_context_id": context.id, "class_label": context.class_label, "school_year": context.school_year,
        "session_number": number, "curriculum_weekly_mass": WEEKLY_MASS,
        "teacher_actual_weekly_minutes": context.teacher_actual_weekly_minutes}
    identification = json.loads(revision.identification_json)
    identification.update({"classe": context.class_label, "année scolaire": context.school_year, "numéro de séance": str(number), "durée de la séance": f"{payload.durations.slot_minutes - payload.durations.break_minutes} min"})
    for key in ["classe", "année scolaire", "numéro de séance", "durée de la séance"]:
        state["provenance"]["identification." + key] = {"origin": "LOCAL_TEACHER", "sources": []}
    revision.identification_json = json.dumps(identification, ensure_ascii=False)
    revision.authoring_json = json.dumps(state, ensure_ascii=False)


@router.post("/plans/{plan_id}/sessions", status_code=201)
def create_session(plan_id: int, payload: CreateSession, db: Session = Depends(get_db)):
    plan = get(db, m.SequencePlan, plan_id)
    validate_preparation(db, plan, payload)
    if plan_detail(plan_id, db)["next_session_number"] != payload.expected_session_number:
        raise HTTPException(409, "Le numéro proposé a changé. Rechargez les séances.")
    sequence = get(db, m.Sequence, plan.sequence_id)
    situation = get(db, m.SituationApprentissage, sequence.situation_id)
    try:
        detail = compose_sheet(Compose(programme_id=situation.programme_version_id, scope="SEQUENCE", scope_id=sequence.id,
            title=payload.title, instruction_ids=payload.instruction_ids, automatic=payload.automatic, local=payload.local), db, commit=False)
        row = m.PlannedSession(sequence_plan_id=plan.id, sheet_id=detail["sheet_id"], session_number_within_sequence=payload.expected_session_number)
        db.add(row)
        snapshot(db, db.get(m.TeacherSheetRevision, detail["id"]), plan, payload, payload.expected_session_number)
        db.flush()
        db.commit()
    except (IntegrityError, OperationalError) as exc:
        db.rollback()
        raise HTTPException(409, "Création concurrente : rechargez les séances. Aucune fiche partielle conservée.") from exc
    return sheet_detail(db, detail["id"])


@router.put("/revisions/{revision_id}/preparation")
def update_preparation(revision_id: int, payload: Preparation, db: Session = Depends(get_db)):
    revision = get(db, m.TeacherSheetRevision, revision_id)
    require_draft(revision)
    planned = db.scalar(select(m.PlannedSession).where(m.PlannedSession.sheet_id == revision.sheet_id))
    if not planned:
        raise HTTPException(422, "Cette fiche appartient à l’historique sans classe et année associées.")
    plan = get(db, m.SequencePlan, planned.sequence_plan_id)
    validate_preparation(db, plan, payload)
    old = list(db.scalars(select(m.SessionCurriculumSegment).where(m.SessionCurriculumSegment.teacher_revision_id == revision_id).order_by(m.SessionCurriculumSegment.position)))
    # Do not silently discard resources already edited for an instruction.
    state = json.loads(revision.authoring_json)
    removed = {s.instruction_id for s in old} - set(payload.instruction_ids)
    for iid in removed:
        selection = state.get("selections", {}).pop(str(iid), None)
        if selection:
            state.setdefault("selection_history", []).append(selection)
            if not any(s["instance_id"] == selection["instance_id"] for s in state["selections"].values()):
                for block in db.scalars(select(m.SheetBlockInstance).where(m.SheetBlockInstance.resource_instance_id == selection["instance_id"])):
                    block.visible = False
    revision.authoring_json = json.dumps(state, ensure_ascii=False)
    for segment in old:
        db.delete(segment)
    db.flush()
    for pos, iid in enumerate(payload.instruction_ids, 1):
        db.add(m.SessionCurriculumSegment(teacher_revision_id=revision_id, instruction_id=iid, position=pos))
    snapshot(db, revision, plan, payload, planned.session_number_within_sequence)
    commit_or_conflict(db)
    return sheet_detail(db, revision_id)


@router.post("/sessions/{planned_id}/executions", status_code=201)
def execute(planned_id: int, payload: Execution, db: Session = Depends(get_db)):
    planned = get(db, m.PlannedSession, planned_id)
    revision = get(db, m.TeacherSheetRevision, payload.teacher_revision_id)
    if revision.sheet_id != planned.sheet_id or revision.status != "FINALIZED":
        raise HTTPException(409, "Choisissez une révision finalisée de cette séance.")
    segments = set(db.scalars(select(m.SessionCurriculumSegment.id).where(m.SessionCurriculumSegment.teacher_revision_id == revision.id)))
    ids = [r.segment_id for r in payload.results]
    if len(set(ids)) != len(ids) or not set(ids) <= segments:
        raise HTTPException(422, "Une instruction est répétée ou extérieure à la révision exécutée.")
    context = get(db, m.ClassContext, get(db, m.SequencePlan, planned.sequence_plan_id).class_context_id)
    event = m.TeachingSession(teacher_revision_id=revision.id, planned_session_id=planned.id, taught_on=payload.taught_on.isoformat(), class_label=context.class_label, notes=payload.notes)
    db.add(event)
    db.flush()
    for position, result in enumerate(payload.results, 1):
        db.add(m.ExecutedCurriculumSegment(teaching_session_id=event.id, session_curriculum_segment_id=result.segment_id, status=result.status, actual_minutes=result.actual_minutes, position=position))
    commit_or_conflict(db)
    return {"id": event.id, "status": "RECORDED", "unreported_segment_ids": sorted(segments - set(ids))}


def historical_progress(db):
    rows = []
    for instruction in db.scalars(select(m.InstructionGuide).order_by(m.InstructionGuide.position)):
        events = db.execute(select(m.ExecutedCurriculumSegment, m.TeachingSession)
            .join(m.TeachingSession, m.ExecutedCurriculumSegment.teaching_session_id == m.TeachingSession.id)
            .join(m.SessionCurriculumSegment, m.ExecutedCurriculumSegment.session_curriculum_segment_id == m.SessionCurriculumSegment.id)
            .where(m.SessionCurriculumSegment.instruction_id == instruction.id, m.TeachingSession.planned_session_id.is_(None))).all()
        rows.append({"instruction_id": instruction.id, "code": instruction.code, "text": instruction.text, "status": "UNCONTEXTUALIZED", "executions": len(events),
            "actual_minutes": sum(e.actual_minutes for e, _ in events), "raw_results": [{"status": e.status, "actual_minutes": e.actual_minutes, "taught_on": s.taught_on} for e, s in events]})
    return rows
