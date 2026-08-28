from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    event,
    inspect,
)
from sqlalchemy.orm import Mapped, Session, mapped_column

from .database import Base


def now() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


class ProgrammeVersion(Base):
    __tablename__ = "programme_versions"
    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(80), unique=True)
    title: Mapped[str] = mapped_column(String(255))
    level: Mapped[str] = mapped_column(String(30), default="4e")
    status: Mapped[str] = mapped_column(String(30), default="ACTIVE")


class GuideVersion(Base):
    __tablename__ = "guide_versions"
    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(80), unique=True)
    title: Mapped[str] = mapped_column(String(255))
    level: Mapped[str] = mapped_column(String(30), default="4e")
    status: Mapped[str] = mapped_column(String(30), default="ACTIVE")


class SituationApprentissage(Base):
    __tablename__ = "learning_situations"
    id: Mapped[int] = mapped_column(primary_key=True)
    programme_version_id: Mapped[int] = mapped_column(ForeignKey("programme_versions.id"))
    code: Mapped[str] = mapped_column(String(50), unique=True)
    title: Mapped[str] = mapped_column(String(255))
    position: Mapped[int] = mapped_column(Integer)


class Sequence(Base):
    __tablename__ = "sequences"
    id: Mapped[int] = mapped_column(primary_key=True)
    situation_id: Mapped[int] = mapped_column(ForeignKey("learning_situations.id"))
    guide_version_id: Mapped[int] = mapped_column(ForeignKey("guide_versions.id"))
    code: Mapped[str] = mapped_column(String(50), unique=True)
    title: Mapped[str] = mapped_column(String(255))
    position: Mapped[int] = mapped_column(Integer)


class ConnaissanceTechnique(Base):
    __tablename__ = "knowledge_items"
    id: Mapped[int] = mapped_column(primary_key=True)
    sequence_id: Mapped[int] = mapped_column(ForeignKey("sequences.id"))
    code: Mapped[str] = mapped_column(String(60), unique=True)
    label: Mapped[str] = mapped_column(String(255))
    position: Mapped[int] = mapped_column(Integer)


class InstructionGuide(Base):
    __tablename__ = "guide_instructions"
    id: Mapped[int] = mapped_column(primary_key=True)
    sequence_id: Mapped[int] = mapped_column(ForeignKey("sequences.id"))
    code: Mapped[str] = mapped_column(String(60), unique=True)
    text: Mapped[str] = mapped_column(Text)
    position: Mapped[int] = mapped_column(Integer)


class CurriculumTimeAllocation(Base):
    __tablename__ = "curriculum_time_allocations"
    id: Mapped[int] = mapped_column(primary_key=True)
    situation_id: Mapped[int] = mapped_column(ForeignKey("learning_situations.id"))
    source_document_id: Mapped[int] = mapped_column(ForeignKey("source_documents.id"))
    hours: Mapped[float] = mapped_column(Float)
    note: Mapped[str] = mapped_column(Text, default="")


class SourceDocument(Base):
    __tablename__ = "source_documents"
    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(80), unique=True)
    title: Mapped[str] = mapped_column(String(255))
    document_type: Mapped[str] = mapped_column(String(50))
    file_name: Mapped[str] = mapped_column(String(255))
    sha256: Mapped[str] = mapped_column(String(64), default="")
    authority: Mapped[str] = mapped_column(String(255), default="")


class SourceOccurrence(Base):
    __tablename__ = "source_occurrences"
    id: Mapped[int] = mapped_column(primary_key=True)
    source_document_id: Mapped[int] = mapped_column(ForeignKey("source_documents.id"))
    entity_type: Mapped[str] = mapped_column(String(50))
    entity_id: Mapped[int] = mapped_column(Integer)
    page_label: Mapped[str] = mapped_column(String(50))
    locator: Mapped[str] = mapped_column(String(255), default="")
    excerpt: Mapped[str] = mapped_column(Text, default="")


class SourceIssue(Base):
    __tablename__ = "source_issues"
    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(60), unique=True)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(30), default="OPEN")
    resolution: Mapped[str] = mapped_column(Text, default="")


class ProposedContent(Base):
    __tablename__ = "proposed_contents"
    id: Mapped[int] = mapped_column(primary_key=True)
    entity_type: Mapped[str] = mapped_column(String(50))
    entity_id: Mapped[int] = mapped_column(Integer)
    label: Mapped[str] = mapped_column(String(255))
    content_latex: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(30), default="PROPOSED")
    ia_generated: Mapped[bool] = mapped_column(Boolean, default=False)


class PedagogicalResource(Base):
    __tablename__ = "pedagogical_resources"
    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(80), unique=True)
    title: Mapped[str] = mapped_column(String(255))
    resource_type: Mapped[str] = mapped_column(String(50))
    structure_kind: Mapped[str] = mapped_column(String(30), default="ATOMIC")
    level: Mapped[str] = mapped_column(String(30), default="4e")
    provenance_kind: Mapped[str] = mapped_column(String(30), default="SOURCED")


class PedagogicalResourceVersion(Base):
    __tablename__ = "pedagogical_resource_versions"
    id: Mapped[int] = mapped_column(primary_key=True)
    resource_id: Mapped[int] = mapped_column(ForeignKey("pedagogical_resources.id"))
    version_number: Mapped[int] = mapped_column(Integer, default=1)
    title: Mapped[str] = mapped_column(String(255))
    summary: Mapped[str] = mapped_column(Text, default="")
    estimated_minutes: Mapped[int] = mapped_column(Integer, default=10)
    status: Mapped[str] = mapped_column(String(30), default="AVAILABLE")
    transcription_status: Mapped[str] = mapped_column(String(30), default="NOT_REVIEWED")
    mathematical_status: Mapped[str] = mapped_column(String(30), default="NOT_REVIEWED")
    pedagogical_status: Mapped[str] = mapped_column(String(30), default="NOT_REVIEWED")
    source_completeness_status: Mapped[str] = mapped_column(String(30), default="NOT_REVIEWED")
    source_consistency_status: Mapped[str] = mapped_column(String(30), default="NOT_REVIEWED")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)
    __table_args__ = (UniqueConstraint("resource_id", "version_number"),)


class PedagogicalBlock(Base):
    __tablename__ = "pedagogical_blocks"
    id: Mapped[int] = mapped_column(primary_key=True)
    resource_version_id: Mapped[int] = mapped_column(ForeignKey("pedagogical_resource_versions.id"))
    block_type: Mapped[str] = mapped_column(String(40))
    title: Mapped[str] = mapped_column(String(255))
    content_latex: Mapped[str] = mapped_column(Text)
    position: Mapped[int] = mapped_column(Integer)


class BlockVariant(Base):
    __tablename__ = "block_variants"
    id: Mapped[int] = mapped_column(primary_key=True)
    block_id: Mapped[int] = mapped_column(ForeignKey("pedagogical_blocks.id"))
    target: Mapped[str] = mapped_column(String(40))
    label: Mapped[str] = mapped_column(String(255))
    content_latex: Mapped[str] = mapped_column(Text)
    adaptation_note: Mapped[str] = mapped_column(Text, default="")
    __table_args__ = (UniqueConstraint("block_id", "target"),)


class ResourceInstructionMapping(Base):
    __tablename__ = "resource_instruction_mappings"
    id: Mapped[int] = mapped_column(primary_key=True)
    resource_version_id: Mapped[int] = mapped_column(ForeignKey("pedagogical_resource_versions.id"))
    instruction_id: Mapped[int] = mapped_column(ForeignKey("guide_instructions.id"))
    mapping_kind: Mapped[str] = mapped_column(String(30), default="IMPLEMENTS")
    validation_status: Mapped[str] = mapped_column(String(30), default="SOURCE_CONFIRMED")
    note: Mapped[str] = mapped_column(Text, default="")
    __table_args__ = (UniqueConstraint("resource_version_id", "instruction_id"),)


class TeacherSessionSheet(Base):
    __tablename__ = "teacher_session_sheets"
    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(80), unique=True)
    title: Mapped[str] = mapped_column(String(255))
    level: Mapped[str] = mapped_column(String(30), default="4e")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)


class TeacherSheetRevision(Base):
    __tablename__ = "teacher_sheet_revisions"
    id: Mapped[int] = mapped_column(primary_key=True)
    sheet_id: Mapped[int] = mapped_column(ForeignKey("teacher_session_sheets.id"))
    revision_number: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(30), default="DRAFT")
    identification_json: Mapped[str] = mapped_column(Text, default="{}")
    planning_json: Mapped[str] = mapped_column(Text, default="{}")
    finalized_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)
    __table_args__ = (UniqueConstraint("sheet_id", "revision_number"),)


class SessionCurriculumSegment(Base):
    __tablename__ = "session_curriculum_segments"
    id: Mapped[int] = mapped_column(primary_key=True)
    teacher_revision_id: Mapped[int] = mapped_column(ForeignKey("teacher_sheet_revisions.id"))
    instruction_id: Mapped[int] = mapped_column(ForeignKey("guide_instructions.id"))
    position: Mapped[int] = mapped_column(Integer)
    planned_minutes: Mapped[int] = mapped_column(Integer, default=0)
    __table_args__ = (UniqueConstraint("teacher_revision_id", "position"),)


class SheetResourceInstance(Base):
    __tablename__ = "sheet_resource_instances"
    id: Mapped[int] = mapped_column(primary_key=True)
    teacher_revision_id: Mapped[int] = mapped_column(ForeignKey("teacher_sheet_revisions.id"))
    origin: Mapped[str] = mapped_column(String(30))
    source_resource_version_id: Mapped[int | None] = mapped_column(ForeignKey("pedagogical_resource_versions.id"), nullable=True)
    title: Mapped[str] = mapped_column(String(255))
    position: Mapped[int] = mapped_column(Integer)
    adaptation_note: Mapped[str] = mapped_column(Text, default="")
    __table_args__ = (CheckConstraint("(origin = 'LIBRARY_DERIVED' AND source_resource_version_id IS NOT NULL) OR (origin = 'LOCAL_ORIGINAL' AND source_resource_version_id IS NULL)", name="ck_sheet_resource_origin_source"), UniqueConstraint("teacher_revision_id", "position"))


class SheetBlockInstance(Base):
    __tablename__ = "sheet_block_instances"
    id: Mapped[int] = mapped_column(primary_key=True)
    resource_instance_id: Mapped[int] = mapped_column(ForeignKey("sheet_resource_instances.id"))
    source_block_id: Mapped[int | None] = mapped_column(ForeignKey("pedagogical_blocks.id"), nullable=True)
    block_type: Mapped[str] = mapped_column(String(40))
    title: Mapped[str] = mapped_column(String(255))
    content_latex: Mapped[str] = mapped_column(Text)
    position: Mapped[int] = mapped_column(Integer)
    __table_args__ = (UniqueConstraint("resource_instance_id", "position"),)


class FlowItem(Base):
    __tablename__ = "flow_items"
    id: Mapped[int] = mapped_column(primary_key=True)
    teacher_revision_id: Mapped[int] = mapped_column(ForeignKey("teacher_sheet_revisions.id"))
    block_instance_id: Mapped[int | None] = mapped_column(ForeignKey("sheet_block_instances.id"), nullable=True)
    item_kind: Mapped[str] = mapped_column(String(30), default="BLOCK")
    phase_code: Mapped[str] = mapped_column(String(50))
    teacher_action: Mapped[str] = mapped_column(Text, default="")
    learner_action: Mapped[str] = mapped_column(Text, default="")
    strategy: Mapped[str] = mapped_column(String(80), default="")
    duration_minutes: Mapped[int] = mapped_column(Integer, default=0)
    position: Mapped[int] = mapped_column(Integer)
    __table_args__ = (
        CheckConstraint("(item_kind IN ('ACTIVITY', 'BLOCK') AND block_instance_id IS NOT NULL) OR (item_kind = 'SECTION' AND block_instance_id IS NULL)", name="ck_flow_item_kind"),
        UniqueConstraint("teacher_revision_id", "position"),
    )


class ActivityPhase(Base):
    __tablename__ = "activity_phases"
    id: Mapped[int] = mapped_column(primary_key=True)
    flow_item_id: Mapped[int] = mapped_column(ForeignKey("flow_items.id"))
    code: Mapped[str] = mapped_column(String(50))
    label: Mapped[str] = mapped_column(String(255))
    duration_minutes: Mapped[int] = mapped_column(Integer, default=0)
    position: Mapped[int] = mapped_column(Integer)


class TeachingSession(Base):
    __tablename__ = "teaching_sessions"
    id: Mapped[int] = mapped_column(primary_key=True)
    teacher_revision_id: Mapped[int] = mapped_column(ForeignKey("teacher_sheet_revisions.id"))
    taught_on: Mapped[str] = mapped_column(String(10))
    class_label: Mapped[str] = mapped_column(String(80))
    notes: Mapped[str] = mapped_column(Text, default="")


class ExecutedCurriculumSegment(Base):
    __tablename__ = "executed_curriculum_segments"
    id: Mapped[int] = mapped_column(primary_key=True)
    teaching_session_id: Mapped[int] = mapped_column(ForeignKey("teaching_sessions.id"))
    session_curriculum_segment_id: Mapped[int] = mapped_column(ForeignKey("session_curriculum_segments.id"))
    status: Mapped[str] = mapped_column(String(30), default="DONE")
    actual_minutes: Mapped[int] = mapped_column(Integer, default=0)
    position: Mapped[int] = mapped_column(Integer)
    __table_args__ = (UniqueConstraint("teaching_session_id", "position"),)


class LearnerSupport(Base):
    __tablename__ = "learner_supports"
    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(80), unique=True)
    title: Mapped[str] = mapped_column(String(255))
    level: Mapped[str] = mapped_column(String(30), default="4e")
    sequence_id: Mapped[int | None] = mapped_column(ForeignKey("sequences.id"), nullable=True)
    situation_id: Mapped[int | None] = mapped_column(ForeignKey("learning_situations.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)
    __table_args__ = (CheckConstraint("(sequence_id IS NOT NULL AND situation_id IS NULL) OR (sequence_id IS NULL AND situation_id IS NOT NULL)", name="ck_support_scope_xor"),)


class LearnerSupportRevision(Base):
    __tablename__ = "learner_support_revisions"
    id: Mapped[int] = mapped_column(primary_key=True)
    support_id: Mapped[int] = mapped_column(ForeignKey("learner_supports.id"))
    revision_number: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(30), default="DRAFT")
    finalized_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)
    __table_args__ = (UniqueConstraint("support_id", "revision_number"),)


class SupportResourceInstance(Base):
    __tablename__ = "support_resource_instances"
    id: Mapped[int] = mapped_column(primary_key=True)
    support_revision_id: Mapped[int] = mapped_column(ForeignKey("learner_support_revisions.id"))
    origin: Mapped[str] = mapped_column(String(30))
    source_resource_version_id: Mapped[int | None] = mapped_column(ForeignKey("pedagogical_resource_versions.id"), nullable=True)
    title: Mapped[str] = mapped_column(String(255))
    position: Mapped[int] = mapped_column(Integer)
    __table_args__ = (CheckConstraint("(origin = 'LIBRARY_DERIVED' AND source_resource_version_id IS NOT NULL) OR (origin = 'LOCAL_ORIGINAL' AND source_resource_version_id IS NULL)", name="ck_support_resource_origin_source"), UniqueConstraint("support_revision_id", "position"))


class SupportBlockInstance(Base):
    __tablename__ = "support_block_instances"
    id: Mapped[int] = mapped_column(primary_key=True)
    support_resource_instance_id: Mapped[int] = mapped_column(ForeignKey("support_resource_instances.id"))
    source_block_id: Mapped[int | None] = mapped_column(ForeignKey("pedagogical_blocks.id"), nullable=True)
    block_type: Mapped[str] = mapped_column(String(40))
    title: Mapped[str] = mapped_column(String(255))
    content_latex: Mapped[str] = mapped_column(Text)
    visible: Mapped[bool] = mapped_column(Boolean, default=True)
    position: Mapped[int] = mapped_column(Integer)
    __table_args__ = (UniqueConstraint("support_resource_instance_id", "position"),)


class SupportUse(Base):
    __tablename__ = "support_uses"
    id: Mapped[int] = mapped_column(primary_key=True)
    support_revision_id: Mapped[int] = mapped_column(ForeignKey("learner_support_revisions.id"))
    teaching_session_id: Mapped[int | None] = mapped_column(ForeignKey("teaching_sessions.id"), nullable=True)
    used_on: Mapped[str] = mapped_column(String(10))
    class_label: Mapped[str] = mapped_column(String(80))
    part_label: Mapped[str] = mapped_column(String(255), default="Ensemble du support")
    notes: Mapped[str] = mapped_column(Text, default="")


class DocumentExport(Base):
    __tablename__ = "document_exports"
    id: Mapped[int] = mapped_column(primary_key=True)
    document_family: Mapped[str] = mapped_column(String(30))
    teacher_revision_id: Mapped[int | None] = mapped_column(ForeignKey("teacher_sheet_revisions.id"), nullable=True)
    support_revision_id: Mapped[int | None] = mapped_column(ForeignKey("learner_support_revisions.id"), nullable=True)
    format: Mapped[str] = mapped_column(String(20), default="PDF")
    target: Mapped[str] = mapped_column(String(40), default="TEACHER")
    file_path: Mapped[str] = mapped_column(String(500))
    status: Mapped[str] = mapped_column(String(30), default="READY")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)
    __table_args__ = (
        CheckConstraint("(document_family = 'TEACHER' AND teacher_revision_id IS NOT NULL AND support_revision_id IS NULL) OR (document_family = 'LEARNER' AND teacher_revision_id IS NULL AND support_revision_id IS NOT NULL)", name="ck_export_family_xor"),
    )


def _revision_is_finalized(session: Session, family: str, revision_id: int | None) -> bool:
    if revision_id is None:
        return False
    model = TeacherSheetRevision if family == "TEACHER" else LearnerSupportRevision
    revision = session.get(model, revision_id)
    return bool(revision and revision not in session.new and revision.status == "FINALIZED")


@event.listens_for(Session, "before_flush")
def protect_finalized_revisions(session: Session, _flush_context, _instances) -> None:
    for obj in set(session.new).union(session.dirty).union(session.deleted):
        family = None
        revision_id = None
        if isinstance(obj, TeacherSheetRevision):
            history = inspect(obj).attrs.status.history
            if history.deleted and history.deleted[0] == "FINALIZED":
                raise ValueError("Une révision enseignant finalisée est immuable.")
            continue
        if isinstance(obj, (SessionCurriculumSegment, SheetResourceInstance, FlowItem)):
            family, revision_id = "TEACHER", obj.teacher_revision_id
        elif isinstance(obj, SheetBlockInstance):
            parent = session.get(SheetResourceInstance, obj.resource_instance_id)
            family, revision_id = "TEACHER", parent.teacher_revision_id if parent else None
        elif isinstance(obj, LearnerSupportRevision):
            history = inspect(obj).attrs.status.history
            if history.deleted and history.deleted[0] == "FINALIZED":
                raise ValueError("Une révision apprenant finalisée est immuable.")
            continue
        elif isinstance(obj, SupportResourceInstance):
            family, revision_id = "LEARNER", obj.support_revision_id
        elif isinstance(obj, SupportBlockInstance):
            parent = session.get(SupportResourceInstance, obj.support_resource_instance_id)
            family, revision_id = "LEARNER", parent.support_revision_id if parent else None
        if family and _revision_is_finalized(session, family, revision_id):
            raise ValueError("Le contenu d'une révision finalisée est immuable.")
