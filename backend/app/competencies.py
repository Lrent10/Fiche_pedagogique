"""Versioned reference data and explicit, revision-owned competency choices."""
import json
from pathlib import Path
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from . import models as m
from .database import get_db

router = APIRouter(prefix="/api/competencies", tags=["competencies"])
FIELDS = {"DISCIPLINARY": "compétences disciplinaires", "TRANSDISCIPLINARY": "compétence transdisciplinaire", "TRANSVERSAL": "compétences transversales"}
RANK = {"REQUIRED": 0, "RECOMMENDED": 1, "CONTEXTUAL_CANDIDATE": 2, "EXAMPLE_SELECTION": 3, "LOCAL_SELECTION": 4}
CAPS = {"DISCIPLINARY": 2, "TRANSDISCIPLINARY": 1, "TRANSVERSAL": 3}


def reference_row(db, model, key, **values):
    field, value = key
    row = db.scalar(select(model).where(getattr(model, field) == value))
    if row:
        if any(getattr(row, k) != v for k, v in values.items()):
            raise ValueError(f"Référence divergente conservée : {model.__name__}/{value}. Nouvelle version requise.")
        return row
    row = model(**{field: value}, **values)
    db.add(row)
    db.flush()
    return row


def install_catalog(db):
    data = json.loads(Path(__file__).with_name("competency_reference.json").read_text(encoding="utf-8"))
    sources = {}
    for source in data["sources"]:
        values = dict(source)
        code = values.pop("code")
        sources[code] = reference_row(db, m.SourceDocument, ("code", code), **values)
    catalog = {}
    for context in data["contexts"]:
        code = context["canonical_code"]
        if code in catalog:
            continue
        kind = "TRANSDISCIPLINARY" if code.startswith("CTD") else "TRANSVERSAL" if code.startswith("CT") else "DISCIPLINARY"
        label = context["normalized_display_label"].lstrip('. ').replace('out ils', 'outils')
        catalog[code] = reference_row(db, m.Competency, ("canonical_code", code), competency_type=kind, canonical_label=label, canonical_number=int(code.lstrip('CTD')), active=True)
    issue = reference_row(db, m.SourceIssue, ("code", "P0-SOURCE-CT8-6E-CONTEXT"), title="CT8 : contexte contradictoire du programme 6e", description="Programme 6e, PDF p.40 : le contexte mentionne « troisième ». Source brute conservée ; aucune correction inventée.", status="OPEN", resolution="Erratum autoritatif ou arbitrage inspecteur/CP attendu.")
    for context in data["contexts"]:
        values = dict(context)
        code = values.pop("code")
        values["competency_id"] = catalog[values.pop("canonical_code")].id
        values["source_document_id"] = sources[values.pop("source_code")].id
        values["source_issue_id"] = issue.id if code == "P6-CT8" else None
        reference_row(db, m.CompetencyContext, ("code", code), **values)
    sequence = db.scalar(select(m.Sequence).where(m.Sequence.code == "SEQ8"))
    if sequence:
        programme_id = db.get(m.SituationApprentissage, sequence.situation_id).programme_version_id
        for code in ["CD1", "CD3", "CTD2", "CT1", "CT8", "CT6"]:
            ctx = db.scalar(select(m.CompetencyContext).where(m.CompetencyContext.code == "G4-" + code))
            if ctx:
                reference_row(db, m.CompetencyApplicability, ("code", "G4-SEQ8-" + code), competency_context_id=ctx.id, class_level="4e", programme_version_id=programme_id, situation_id=sequence.situation_id, sequence_id=sequence.id, instruction_id=None, applicability_type="EXAMPLE_SELECTION", source_document_id=ctx.source_document_id, source_version=ctx.curriculum_version, source_page="74", notes="Le guide illustre ce choix pour une séance de calcul algébrique. À adapter aux instructions prévues.")


def context_view(db, ctx):
    source = db.get(m.SourceDocument, ctx.source_document_id)
    issue = db.get(m.SourceIssue, ctx.source_issue_id) if ctx.source_issue_id else None
    return {"context_id": ctx.id, "label": ctx.normalized_display_label, "source_raw_label": ctx.source_raw_label, "source_raw_text": ctx.source_raw_text, "class_level": ctx.class_level, "curriculum_version": ctx.curriculum_version, "source_document": source.title, "source_version": source.sha256 or source.code, "source_page": ctx.source_page, "authority_class": ctx.authority_class, "source_status": ctx.source_status, "realization_context": ctx.realization_context, "evaluation_context": ctx.evaluation_context, "criteria": json.loads(ctx.criteria_json) if ctx.criteria_json else None, "capacities": json.loads(ctx.capacities_json) if ctx.capacities_json else None, "skills": json.loads(ctx.skills_json) if ctx.skills_json else None, "source_issue": {"code": issue.code, "title": issue.title, "status": issue.status} if issue else None}


def active_catalog(db):
    result = []
    for competency in db.scalars(select(m.Competency).where(m.Competency.active.is_(True)).order_by(m.Competency.id)):
        ctx = db.scalar(select(m.CompetencyContext).where(m.CompetencyContext.competency_id == competency.id, m.CompetencyContext.class_level == "4e", m.CompetencyContext.authority_class == "OFFICIAL_PROGRAM").order_by(m.CompetencyContext.id))
        if ctx:
            result.append({"competency_id": competency.id, "canonical_code": competency.canonical_code, "competency_type": competency.competency_type, **context_view(db, ctx)})
    return result


def applicable(db, revision=None, instruction_ids=None):
    from .services import curriculum_level_for_revision
    if revision is not None and curriculum_level_for_revision(db, revision) != "4e":
        return []
    if revision is not None:
        instruction_ids = list(db.scalars(select(m.SessionCurriculumSegment.instruction_id).where(m.SessionCurriculumSegment.teacher_revision_id == revision.id)))
    instructions = list(db.scalars(select(m.InstructionGuide).where(m.InstructionGuide.id.in_(instruction_ids or []))))
    sequences = {i.sequence_id: db.get(m.Sequence, i.sequence_id) for i in instructions}
    programmes = {s.id: db.get(m.SituationApprentissage, s.situation_id).programme_version_id for s in sequences.values()}
    result = []
    for app in db.scalars(select(m.CompetencyApplicability).where(m.CompetencyApplicability.class_level == "4e")):
        # A complete matching path prevents mixing different SA/sequence/instruction scopes.
        if not any((app.programme_version_id is None or app.programme_version_id == programmes[i.sequence_id]) and (app.instruction_id is None or app.instruction_id == i.id) and (app.sequence_id is None or app.sequence_id == i.sequence_id) and (app.situation_id is None or app.situation_id == sequences[i.sequence_id].situation_id) for i in instructions):
            continue
        ctx = db.get(m.CompetencyContext, app.competency_context_id)
        comp = db.get(m.Competency, ctx.competency_id)
        if not comp.active or ctx.class_level != "4e" or ctx.source_issue_id or ctx.source_status in {"REJECTED", "INACTIVE_REFERENCE"}:
            continue
        source = db.get(m.SourceDocument, app.source_document_id)
        result.append({"competency_id": comp.id, "canonical_code": comp.canonical_code, "competency_type": comp.competency_type, **context_view(db, ctx), "applicability_id": app.id, "applicability_type": app.applicability_type, "reason": app.notes, "applicability_source": {"document": source.title, "version": app.source_version, "page": app.source_page}, "specificity": sum(x is not None for x in (app.situation_id, app.sequence_id, app.instruction_id))})
    return sorted(result, key=lambda x: (RANK[x["applicability_type"]], 0 if x["authority_class"] in {"OFFICIAL_PROGRAM", "OFFICIAL_GUIDE"} else 1, -x["specificity"], x["canonical_code"], x["applicability_id"]))


def suggest(db, revision=None, instruction_ids=None):
    chosen = []; seen = set(); counts = dict.fromkeys(CAPS, 0)
    for row in applicable(db, revision, instruction_ids):
        kind = row["competency_type"]
        if row["competency_id"] in seen or counts[kind] >= CAPS[kind] or row["applicability_type"] == "LOCAL_SELECTION":
            continue
        seen.add(row["competency_id"]); counts[kind] += 1
        chosen.append({**row, "selection_origin": "AUTO_SELECTED"})
    return chosen


def selected(db, revision_id):
    return [{**json.loads(row.snapshot_json), "selection_origin": row.selection_origin, "selected_order": row.selected_order, "is_primary": row.is_primary} for row in db.scalars(select(m.TeacherSheetCompetencySelection).where(m.TeacherSheetCompetencySelection.teacher_revision_id == revision_id).order_by(m.TeacherSheetCompetencySelection.selected_order))]


def selection_enabled(revision):
    return json.loads(revision.authoring_json or "{}").get("competency_selection_version") == 1


def planning_view(db, revision):
    planning = json.loads(revision.planning_json)
    if selection_enabled(revision):
        rows = selected(db, revision.id)
        for kind, field in FIELDS.items():
            planning[field] = "\n".join(r["label"] for r in rows if r["competency_type"] == kind)
    return planning


def save_rows(db, revision, rows):
    from .services import require_draft
    require_draft(revision)
    for old in db.scalars(select(m.TeacherSheetCompetencySelection).where(m.TeacherSheetCompetencySelection.teacher_revision_id == revision.id)):
        db.delete(old)
    db.flush()
    state = json.loads(revision.authoring_json or "{}")
    if not selection_enabled(revision):
        state["legacy_competency_values"] = {field: json.loads(revision.planning_json).get(field, "") for field in FIELDS.values()}
    state["competency_selection_version"] = 1
    state.setdefault("provenance", {})
    revision.authoring_json = json.dumps(state, ensure_ascii=False)
    for order, item in enumerate(rows):
        db.add(m.TeacherSheetCompetencySelection(teacher_revision_id=revision.id, competency_id=item["competency_id"], competency_context_id=item.get("context_id"), applicability_id=item.get("applicability_id"), selection_origin=item.get("selection_origin", "TEACHER_SELECTED"), selected_order=order, is_primary=item.get("is_primary", False), snapshot_json=json.dumps(item, ensure_ascii=False)))
    db.flush()
    revision.planning_json = json.dumps(planning_view(db, revision), ensure_ascii=False)


def initialize_selection(db, revision):
    db.flush()
    save_rows(db, revision, suggest(db, revision))


class Choice(BaseModel):
    competency_id: int
    context_id: int | None = None
    is_primary: bool = False


class Choices(BaseModel):
    selections: list[Choice] = Field(default_factory=list)


@router.get("")
def get_catalog(db: Session = Depends(get_db)):
    return active_catalog(db)


@router.get("/sheets/{revision_id}")
def get_selection(revision_id: int, db: Session = Depends(get_db)):
    revision = db.get(m.TeacherSheetRevision, revision_id)
    if not revision:
        raise HTTPException(404, "Révision introuvable.")
    return {"selected": selected(db, revision_id), "applicable": applicable(db, revision), "suggestions": suggest(db, revision), "catalog": active_catalog(db), "legacy": not selection_enabled(revision)}


@router.put("/sheets/{revision_id}")
def put_selection(revision_id: int, payload: Choices, db: Session = Depends(get_db)):
    from .services import require_draft, sheet_detail, curriculum_level_for_revision
    revision = db.get(m.TeacherSheetRevision, revision_id)
    require_draft(revision)
    if curriculum_level_for_revision(db, revision) != "4e":
        raise HTTPException(422, "Le parcours actif reste limité à la 4e.")
    if len({c.competency_id for c in payload.selections}) != len(payload.selections):
        raise HTTPException(422, "Une compétence ne peut être sélectionnée deux fois.")
    existing = {r["competency_id"]: r for r in selected(db, revision_id)}
    candidates = active_catalog(db) + applicable(db, revision)
    rows = []
    for choice in payload.selections:
        old = existing.get(choice.competency_id)
        if old and (choice.context_id is None or old.get("context_id") == choice.context_id):
            rows.append({**old, "is_primary": choice.is_primary})
            continue
        row = next((r for r in candidates if r["competency_id"] == choice.competency_id and (choice.context_id is None or r["context_id"] == choice.context_id)), None)
        if not row:
            raise HTTPException(422, "Compétence ou contexte indisponible pour cette fiche 4e.")
        rows.append({**row, "selection_origin": "TEACHER_SELECTED", "is_primary": choice.is_primary})
    save_rows(db, revision, rows)
    db.commit()
    return sheet_detail(db, revision_id)
