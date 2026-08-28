from __future__ import annotations

import json
from datetime import datetime

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from . import models as m


def require_draft(revision) -> None:
    if revision is None:
        raise HTTPException(404, "Révision introuvable.")
    if revision.status != "DRAFT":
        raise HTTPException(409, "Une révision finalisée est immuable. Créez une nouvelle révision.")


def copy_library_to_sheet(db: Session, revision_id: int, version_id: int, adaptation_note: str = "") -> m.SheetResourceInstance:
    revision = db.get(m.TeacherSheetRevision, revision_id)
    require_draft(revision)
    version = db.get(m.PedagogicalResourceVersion, version_id)
    if not version:
        raise HTTPException(404, "Ressource introuvable.")
    if version.status != "AVAILABLE":
        raise HTTPException(409, "Cette version de ressource est retirée et ne peut plus être sélectionnée.")
    position = (db.scalar(select(func.max(m.SheetResourceInstance.position)).where(m.SheetResourceInstance.teacher_revision_id == revision_id)) or 0) + 1
    instance = m.SheetResourceInstance(
        teacher_revision_id=revision_id,
        origin="LIBRARY_DERIVED",
        source_resource_version_id=version.id,
        title=version.title,
        position=position,
        adaptation_note=adaptation_note,
    )
    db.add(instance)
    db.flush()
    blocks = db.scalars(select(m.PedagogicalBlock).where(m.PedagogicalBlock.resource_version_id == version.id).order_by(m.PedagogicalBlock.position)).all()
    next_flow = (db.scalar(select(func.max(m.FlowItem.position)).where(m.FlowItem.teacher_revision_id == revision_id)) or 0) + 1
    for offset, block in enumerate(blocks):
        copied = m.SheetBlockInstance(
            resource_instance_id=instance.id,
            source_block_id=block.id,
            block_type=block.block_type,
            title=block.title,
            content_latex=block.content_latex,
            position=block.position,
        )
        db.add(copied)
        db.flush()
        db.add(m.FlowItem(teacher_revision_id=revision_id, block_instance_id=copied.id, phase_code="REALISATION", duration_minutes=5, position=next_flow + offset))
    db.commit()
    db.refresh(instance)
    return instance


def add_local_to_sheet(db: Session, revision_id: int, title: str, block_type: str, content_latex: str) -> m.SheetResourceInstance:
    revision = db.get(m.TeacherSheetRevision, revision_id)
    require_draft(revision)
    position = (db.scalar(select(func.max(m.SheetResourceInstance.position)).where(m.SheetResourceInstance.teacher_revision_id == revision_id)) or 0) + 1
    instance = m.SheetResourceInstance(teacher_revision_id=revision_id, origin="LOCAL_ORIGINAL", title=title, position=position)
    db.add(instance)
    db.flush()
    block = m.SheetBlockInstance(resource_instance_id=instance.id, block_type=block_type, title=title, content_latex=content_latex, position=1)
    db.add(block)
    db.flush()
    flow_position = (db.scalar(select(func.max(m.FlowItem.position)).where(m.FlowItem.teacher_revision_id == revision_id)) or 0) + 1
    db.add(m.FlowItem(teacher_revision_id=revision_id, block_instance_id=block.id, phase_code="REALISATION", duration_minutes=5, position=flow_position))
    db.commit()
    db.refresh(instance)
    return instance


def copy_library_to_support(db: Session, revision_id: int, version_id: int) -> m.SupportResourceInstance:
    revision = db.get(m.LearnerSupportRevision, revision_id)
    require_draft(revision)
    version = db.get(m.PedagogicalResourceVersion, version_id)
    if not version:
        raise HTTPException(404, "Ressource introuvable.")
    if version.status != "AVAILABLE":
        raise HTTPException(409, "Cette version de ressource est retirée et ne peut plus être sélectionnée.")
    position = (db.scalar(select(func.max(m.SupportResourceInstance.position)).where(m.SupportResourceInstance.support_revision_id == revision_id)) or 0) + 1
    instance = m.SupportResourceInstance(support_revision_id=revision_id, origin="LIBRARY_DERIVED", source_resource_version_id=version.id, title=version.title, position=position)
    db.add(instance)
    db.flush()
    for block in db.scalars(select(m.PedagogicalBlock).where(m.PedagogicalBlock.resource_version_id == version.id).order_by(m.PedagogicalBlock.position)).all():
        db.add(m.SupportBlockInstance(support_resource_instance_id=instance.id, source_block_id=block.id, block_type=block.block_type, title=block.title, content_latex=block.content_latex, position=block.position))
    db.commit()
    db.refresh(instance)
    return instance


def create_sheet_from_support(
    db: Session,
    support_revision_id: int,
    selected_block_ids: list[int],
    *,
    title: str | None,
    instruction_ids: list[int],
    duration_minutes: int,
    class_label: str,
    part_label: str,
) -> m.TeacherSheetRevision:
    support_revision = db.get(m.LearnerSupportRevision, support_revision_id)
    if not support_revision or support_revision.status != "FINALIZED":
        raise HTTPException(409, "Une fiche ne peut être créée que depuis un support finalisé.")
    if len(selected_block_ids) != len(set(selected_block_ids)):
        raise HTTPException(400, "La sélection de blocs contient des doublons.")

    support = db.get(m.LearnerSupport, support_revision.support_id)
    rows = db.execute(
        select(m.SupportBlockInstance, m.SupportResourceInstance)
        .join(m.SupportResourceInstance)
        .where(
            m.SupportBlockInstance.id.in_(selected_block_ids),
            m.SupportResourceInstance.support_revision_id == support_revision_id,
        )
    ).all()
    by_id = {block.id: (block, resource) for block, resource in rows}
    if set(by_id) != set(selected_block_ids):
        raise HTTPException(400, "Un ou plusieurs blocs ne font pas partie de cette révision du support.")
    teacher_only_types = {"EXPECTED_RESULT", "EXPECTED_TRACE", "SOLUTION", "CORRECTION", "TEACHER_NOTE"}
    for block_id in selected_block_ids:
        block, _ = by_id[block_id]
        if not block.visible or block.block_type in teacher_only_types:
            raise HTTPException(400, "La sélection contient un bloc masqué ou réservé à l'enseignant.")

    if instruction_ids:
        instructions = db.scalars(select(m.InstructionGuide).where(m.InstructionGuide.id.in_(instruction_ids))).all()
        if len(instructions) != len(set(instruction_ids)):
            raise HTTPException(400, "Une ou plusieurs instructions sont introuvables.")
    else:
        version_ids = {resource.source_resource_version_id for _, resource in rows if resource.source_resource_version_id}
        instruction_ids = list(
            dict.fromkeys(
                db.scalars(
                    select(m.ResourceInstructionMapping.instruction_id)
                    .where(m.ResourceInstructionMapping.resource_version_id.in_(version_ids))
                    .order_by(m.ResourceInstructionMapping.instruction_id)
                ).all()
            )
        ) if version_ids else []

    number = (db.scalar(select(func.count()).select_from(m.TeacherSessionSheet)) or 0) + 1
    sheet = m.TeacherSessionSheet(
        code=f"FICHE-4E-{number:03d}",
        title=title or f"Séance - {support.title}",
        level=class_label,
    )
    db.add(sheet)
    db.flush()

    sequence = db.get(m.Sequence, support.sequence_id) if support.sequence_id else None
    situation = db.get(m.SituationApprentissage, support.situation_id) if support.situation_id else None
    if sequence and not situation:
        situation = db.get(m.SituationApprentissage, sequence.situation_id)
    identification = {
        "titre du cours": sheet.title,
        "numéro fiche pédagogique": sheet.code,
        "établissement": "",
        "année scolaire": "",
        "discipline": "Mathématiques",
        "date": "",
        "classe": class_label,
        "effectif": "",
        "nombre de groupes": "",
        "nom du professeur": "",
        "SA": situation.code if situation else "",
        "titre SA": situation.title if situation else "",
        "durée curriculaire SA": "",
        "séquence": sequence.code if sequence else "",
        "titre séquence": sequence.title if sequence else "",
        "durée de la séance": f"{duration_minutes} min",
        "numéro de séance": "",
    }
    planning = {
        "contenus de formation": "",
        "compétences disciplinaires": "",
        "compétence transdisciplinaire": "",
        "compétences transversales": "",
        "connaissances et techniques": "",
        "stratégie objet d'apprentissage": "",
        "durée": f"{duration_minutes} min",
        "stratégies d'enseignement/apprentissage": "",
        "matériels apprenants": "",
        "matériels enseignant": "",
    }
    revision = m.TeacherSheetRevision(
        sheet_id=sheet.id,
        revision_number=1,
        identification_json=json.dumps(identification, ensure_ascii=False),
        planning_json=json.dumps(planning, ensure_ascii=False),
    )
    db.add(revision)
    db.flush()

    per_segment = duration_minutes // max(1, len(instruction_ids))
    for position, instruction_id in enumerate(instruction_ids, 1):
        db.add(m.SessionCurriculumSegment(
            teacher_revision_id=revision.id,
            instruction_id=instruction_id,
            position=position,
            planned_minutes=per_segment,
        ))

    copied_resources: dict[int, m.SheetResourceInstance] = {}
    resource_block_positions: dict[int, int] = {}
    flow_duration = duration_minutes // max(1, len(selected_block_ids))
    for flow_position, block_id in enumerate(selected_block_ids, 1):
        source_block, source_resource = by_id[block_id]
        target_resource = copied_resources.get(source_resource.id)
        if not target_resource:
            target_resource = m.SheetResourceInstance(
                teacher_revision_id=revision.id,
                origin=source_resource.origin,
                source_resource_version_id=source_resource.source_resource_version_id,
                title=source_resource.title,
                position=len(copied_resources) + 1,
                adaptation_note=f"Extrait du support {support.code} r{support_revision.revision_number}",
            )
            db.add(target_resource)
            db.flush()
            copied_resources[source_resource.id] = target_resource
            resource_block_positions[source_resource.id] = 0
        resource_block_positions[source_resource.id] += 1
        copied_block = m.SheetBlockInstance(
            resource_instance_id=target_resource.id,
            source_block_id=source_block.source_block_id,
            block_type=source_block.block_type,
            title=source_block.title,
            content_latex=source_block.content_latex,
            position=resource_block_positions[source_resource.id],
        )
        db.add(copied_block)
        db.flush()
        db.add(m.FlowItem(
            teacher_revision_id=revision.id,
            block_instance_id=copied_block.id,
            item_kind="ACTIVITY" if source_block.block_type == "ACTIVITY" else "BLOCK",
            phase_code="REALISATION",
            duration_minutes=flow_duration,
            expected_result_latex="",
            position=flow_position,
        ))

    selected_titles = [by_id[block_id][0].title for block_id in selected_block_ids]
    db.add(m.SupportUse(
        support_revision_id=support_revision.id,
        teacher_revision_id=revision.id,
        used_on="",
        class_label=class_label,
        part_label=part_label or " ; ".join(selected_titles),
        selected_block_ids_json=json.dumps(selected_block_ids),
        notes="Fiche créée depuis une sélection explicite du support.",
    ))
    db.commit()
    db.refresh(revision)
    return revision


def add_local_to_support(db: Session, revision_id: int, title: str, block_type: str, content_latex: str) -> m.SupportResourceInstance:
    revision = db.get(m.LearnerSupportRevision, revision_id)
    require_draft(revision)
    position = (db.scalar(select(func.max(m.SupportResourceInstance.position)).where(m.SupportResourceInstance.support_revision_id == revision_id)) or 0) + 1
    instance = m.SupportResourceInstance(support_revision_id=revision_id, origin="LOCAL_ORIGINAL", title=title, position=position)
    db.add(instance)
    db.flush()
    db.add(m.SupportBlockInstance(support_resource_instance_id=instance.id, block_type=block_type, title=title, content_latex=content_latex, position=1))
    db.commit()
    db.refresh(instance)
    return instance


def finalize_revision(db: Session, family: str, revision_id: int):
    model = m.TeacherSheetRevision if family == "TEACHER" else m.LearnerSupportRevision
    revision = db.get(model, revision_id)
    require_draft(revision)
    revision.status = "FINALIZED"
    revision.finalized_at = m.now()
    db.commit()
    db.refresh(revision)
    return revision


def new_teacher_revision(db: Session, revision_id: int) -> m.TeacherSheetRevision:
    source = db.get(m.TeacherSheetRevision, revision_id)
    if not source:
        raise HTTPException(404, "Révision introuvable.")
    number = (db.scalar(select(func.max(m.TeacherSheetRevision.revision_number)).where(m.TeacherSheetRevision.sheet_id == source.sheet_id)) or 0) + 1
    target = m.TeacherSheetRevision(sheet_id=source.sheet_id, revision_number=number, identification_json=source.identification_json, planning_json=source.planning_json)
    db.add(target)
    db.flush()
    segment_map = {}
    for segment in db.scalars(select(m.SessionCurriculumSegment).where(m.SessionCurriculumSegment.teacher_revision_id == source.id)).all():
        copied = m.SessionCurriculumSegment(teacher_revision_id=target.id, instruction_id=segment.instruction_id, position=segment.position, planned_minutes=segment.planned_minutes)
        db.add(copied)
        db.flush()
        segment_map[segment.id] = copied.id
    block_map = {}
    resources = db.scalars(select(m.SheetResourceInstance).where(m.SheetResourceInstance.teacher_revision_id == source.id).order_by(m.SheetResourceInstance.position)).all()
    for resource in resources:
        copied_resource = m.SheetResourceInstance(teacher_revision_id=target.id, origin=resource.origin, source_resource_version_id=resource.source_resource_version_id, title=resource.title, position=resource.position, adaptation_note=resource.adaptation_note)
        db.add(copied_resource)
        db.flush()
        for block in db.scalars(select(m.SheetBlockInstance).where(m.SheetBlockInstance.resource_instance_id == resource.id).order_by(m.SheetBlockInstance.position)).all():
            copied_block = m.SheetBlockInstance(resource_instance_id=copied_resource.id, source_block_id=block.source_block_id, block_type=block.block_type, title=block.title, content_latex=block.content_latex, position=block.position)
            db.add(copied_block)
            db.flush()
            block_map[block.id] = copied_block.id
    for flow in db.scalars(select(m.FlowItem).where(m.FlowItem.teacher_revision_id == source.id).order_by(m.FlowItem.position)).all():
        db.add(m.FlowItem(teacher_revision_id=target.id, block_instance_id=block_map.get(flow.block_instance_id), phase_code=flow.phase_code, teacher_action=flow.teacher_action, learner_action=flow.learner_action, strategy=flow.strategy, expected_result_latex=flow.expected_result_latex, duration_minutes=flow.duration_minutes, position=flow.position))
    for support_use in db.scalars(select(m.SupportUse).where(m.SupportUse.teacher_revision_id == source.id)).all():
        db.add(m.SupportUse(
            support_revision_id=support_use.support_revision_id,
            teacher_revision_id=target.id,
            teaching_session_id=None,
            used_on=support_use.used_on,
            class_label=support_use.class_label,
            part_label=support_use.part_label,
            selected_block_ids_json=support_use.selected_block_ids_json,
            notes=support_use.notes,
        ))
    db.commit()
    db.refresh(target)
    return target


def new_support_revision(db: Session, revision_id: int) -> m.LearnerSupportRevision:
    source = db.get(m.LearnerSupportRevision, revision_id)
    if not source:
        raise HTTPException(404, "Révision introuvable.")
    number = (db.scalar(select(func.max(m.LearnerSupportRevision.revision_number)).where(m.LearnerSupportRevision.support_id == source.support_id)) or 0) + 1
    target = m.LearnerSupportRevision(support_id=source.support_id, revision_number=number)
    db.add(target)
    db.flush()
    resources = db.scalars(select(m.SupportResourceInstance).where(m.SupportResourceInstance.support_revision_id == source.id).order_by(m.SupportResourceInstance.position)).all()
    for resource in resources:
        copied_resource = m.SupportResourceInstance(support_revision_id=target.id, origin=resource.origin, source_resource_version_id=resource.source_resource_version_id, title=resource.title, position=resource.position)
        db.add(copied_resource)
        db.flush()
        for block in db.scalars(select(m.SupportBlockInstance).where(m.SupportBlockInstance.support_resource_instance_id == resource.id).order_by(m.SupportBlockInstance.position)).all():
            db.add(m.SupportBlockInstance(support_resource_instance_id=copied_resource.id, source_block_id=block.source_block_id, block_type=block.block_type, title=block.title, content_latex=block.content_latex, visible=block.visible, position=block.position))
    db.commit()
    db.refresh(target)
    return target


def sheet_detail(db: Session, revision_id: int) -> dict:
    revision = db.get(m.TeacherSheetRevision, revision_id)
    if not revision:
        raise HTTPException(404, "Révision introuvable.")
    sheet = db.get(m.TeacherSessionSheet, revision.sheet_id)
    segments = db.execute(select(m.SessionCurriculumSegment, m.InstructionGuide).join(m.InstructionGuide, m.InstructionGuide.id == m.SessionCurriculumSegment.instruction_id).where(m.SessionCurriculumSegment.teacher_revision_id == revision.id).order_by(m.SessionCurriculumSegment.position)).all()
    resources = []
    for resource in db.scalars(select(m.SheetResourceInstance).where(m.SheetResourceInstance.teacher_revision_id == revision.id).order_by(m.SheetResourceInstance.position)).all():
        blocks = db.scalars(select(m.SheetBlockInstance).where(m.SheetBlockInstance.resource_instance_id == resource.id).order_by(m.SheetBlockInstance.position)).all()
        resources.append({"id": resource.id, "origin": resource.origin, "source_resource_version_id": resource.source_resource_version_id, "title": resource.title, "adaptation_note": resource.adaptation_note, "position": resource.position, "blocks": [{"id": b.id, "block_type": b.block_type, "title": b.title, "content_latex": b.content_latex, "position": b.position} for b in blocks]})
    flows = db.scalars(select(m.FlowItem).where(m.FlowItem.teacher_revision_id == revision.id).order_by(m.FlowItem.position)).all()
    support_use = db.scalar(select(m.SupportUse).where(m.SupportUse.teacher_revision_id == revision.id))
    return {
        "id": revision.id,
        "sheet_id": sheet.id,
        "code": sheet.code,
        "title": sheet.title,
        "revision_number": revision.revision_number,
        "status": revision.status,
        "identification": json.loads(revision.identification_json),
        "planning": json.loads(revision.planning_json),
        "segments": [{"id": s.id, "instruction_id": i.id, "instruction_code": i.code, "text": i.text, "planned_minutes": s.planned_minutes} for s, i in segments],
        "resources": resources,
        "flow": [{"id": f.id, "block_instance_id": f.block_instance_id, "phase_code": f.phase_code, "teacher_action": f.teacher_action, "learner_action": f.learner_action, "strategy": f.strategy, "expected_result_latex": f.expected_result_latex, "duration_minutes": f.duration_minutes, "position": f.position} for f in flows],
        "support_use": None if not support_use else {
            "support_revision_id": support_use.support_revision_id,
            "part_label": support_use.part_label,
            "selected_block_ids": json.loads(support_use.selected_block_ids_json),
        },
    }


def support_detail(db: Session, revision_id: int) -> dict:
    revision = db.get(m.LearnerSupportRevision, revision_id)
    if not revision:
        raise HTTPException(404, "Révision introuvable.")
    support = db.get(m.LearnerSupport, revision.support_id)
    resources = []
    for resource in db.scalars(select(m.SupportResourceInstance).where(m.SupportResourceInstance.support_revision_id == revision.id).order_by(m.SupportResourceInstance.position)).all():
        blocks = db.scalars(select(m.SupportBlockInstance).where(m.SupportBlockInstance.support_resource_instance_id == resource.id).order_by(m.SupportBlockInstance.position)).all()
        resources.append({"id": resource.id, "origin": resource.origin, "source_resource_version_id": resource.source_resource_version_id, "title": resource.title, "position": resource.position, "blocks": [{"id": b.id, "source_block_id": b.source_block_id, "block_type": b.block_type, "title": b.title, "content_latex": b.content_latex, "visible": b.visible, "position": b.position} for b in blocks]})
    sequence = db.get(m.Sequence, support.sequence_id) if support.sequence_id else None
    situation = db.get(m.SituationApprentissage, support.situation_id) if support.situation_id else None
    if sequence and not situation:
        situation = db.get(m.SituationApprentissage, sequence.situation_id)
    return {
        "id": revision.id,
        "support_id": support.id,
        "code": support.code,
        "title": support.title,
        "revision_number": revision.revision_number,
        "status": revision.status,
        "scope": "SEQUENCE" if sequence else "SA",
        "sequence": None if not sequence else {"id": sequence.id, "code": sequence.code, "title": sequence.title},
        "situation": None if not situation else {"id": situation.id, "code": situation.code, "title": situation.title},
        "resources": resources,
    }


def sheet_warnings(db: Session, revision_id: int) -> list[dict]:
    detail = sheet_detail(db, revision_id)
    warnings: list[dict] = []
    duration_text = str(
        detail["identification"].get("durée de la séance")
        or detail["identification"].get("durée")
        or "0"
    )
    digits = "".join(char for char in duration_text if char.isdigit())
    session_minutes = int(digits) if digits else 0
    flow_total = sum(item["duration_minutes"] for item in detail["flow"])
    if session_minutes and flow_total > session_minutes:
        warnings.append({"code": "WARNING_DURATION_EXCEEDED", "message": f"Le déroulement totalise {flow_total} min pour une séance de {session_minutes} min."})

    version_ids = [r["source_resource_version_id"] for r in detail["resources"] if r["source_resource_version_id"]]
    mapped_ids = set(db.scalars(select(m.ResourceInstructionMapping.instruction_id).where(m.ResourceInstructionMapping.resource_version_id.in_(version_ids))).all()) if version_ids else set()
    for segment in detail["segments"]:
        if segment["instruction_id"] not in mapped_ids:
            warnings.append({"code": "WARNING_INSTRUCTION_WITHOUT_RESOURCE", "message": f"{segment['instruction_code']} ne possède aucune ressource de bibliothèque intégrée."})
    block_lookup = {block["id"]: block for resource in detail["resources"] for block in resource["blocks"]}
    for resource in detail["resources"]:
        types = {block["block_type"] for block in resource["blocks"]}
        if "INSTRUCTION" not in types:
            warnings.append({"code": "WARNING_ACTIVITY_WITHOUT_CONSIGNE", "message": f"« {resource['title']} » ne contient aucun bloc CONSIGNE/INSTRUCTION."})
    for flow in detail["flow"]:
        block = block_lookup.get(flow["block_instance_id"])
        if block and block["block_type"] in {"INSTRUCTION", "CONSIGNE", "APPLICATION", "EXERCISE"} and not flow["expected_result_latex"].strip():
            warnings.append({"code": "WARNING_EXPECTED_RESULT_MISSING", "message": f"« {block['title']} » ne possède pas encore de résultat attendu saisi par le professeur."})
    if detail["flow"] and not any(item["phase_code"] == "RETURN_PROJECTION" for item in detail["flow"]):
        warnings.append({"code": "WARNING_RETURN_PROJECTION_MISSING", "message": "Aucun item de retour/projection n'est présent dans le déroulement."})
    return warnings


def support_warnings(db: Session, revision_id: int) -> list[dict]:
    detail = support_detail(db, revision_id)
    warnings = []
    for resource in detail["resources"]:
        for block in resource["blocks"]:
            if block["visible"] and block["block_type"] in {"EXPECTED_TRACE", "SOLUTION", "CORRECTION"}:
                warnings.append({"code": "WARNING_TEACHER_CONTENT_VISIBLE_TO_INITIAL_LEARNER", "message": f"Le bloc enseignant « {block['title']} » est visible dans le support initial."})
    return warnings
