from __future__ import annotations

import hashlib
import io
import json
import re
import secrets
import stat
import unicodedata
import zipfile
from datetime import UTC, datetime
from pathlib import PurePosixPath
from typing import Any, Literal
from uuid import uuid4

from fastapi import APIRouter, Depends, Header, HTTPException, UploadFile
from pydantic import BaseModel, ConfigDict, Field, StrictInt, StrictStr, ValidationError, field_validator
from sqlalchemy import delete, or_, select
from sqlalchemy.orm import Session

from . import models as m
from .database import get_db
from .config import settings
from .services import (
    build_resource_snapshot,
    copy_library_to_sheet,
    is_resource_eligible_for_teacher_and_context,
    require_draft,
    resource_matches_instruction,
    revision_instruction_ids,
    teacher_identity,
)
from .latex_safety import ensure_safe_latex, latex_violation

router = APIRouter(prefix="/api", tags=["pedagogical-library"])

RESOURCE_TYPES = {"DISCOVERY_CONSIGNE", "APPLICATION_CONSIGNE", "DECONTEXTUALIZATION_CONSIGNE", "DEEPENING_CONSIGNE", "DEMONSTRATION_CONSIGNE", "ACTIVITY", "HOMEWORK_EXERCISE", "REACTIVATION_EXERCISE", "EXPECTED_RESPONSE", "DEFINITION", "PROPERTY", "THEOREM", "FORMULA", "METHOD", "RULE", "REMARK", "FIGURE", "OTHER_PEDAGOGICAL_RESOURCE"}
CONSIGNE_TYPES = {value for value in RESOURCE_TYPES if value.endswith("_CONSIGNE")}
ORIGINS = {"OFFICIAL_PROGRAM", "OFFICIAL_GUIDE", "OFFICIAL_EXAMPLE", "INSPECTOR_VALIDATED", "CURATED_PROJECT", "BOOK_SOURCE", "COLLEAGUE_RESOURCE", "TEACHER_LOCAL", "USER_CONTRIBUTED"}
VALIDATIONS = {"VERIFIED_SOURCE", "CURATED", "VALIDATED", "USER_UNREVIEWED", "REJECTED", "ARCHIVED"}
VISIBILITIES = {"PRIVATE", "SHARED", "CURATED_GLOBAL", "SYSTEM_REFERENCE"}
RELATIONS = {"PRIMARY", "SUPPORTS", "APPLIES", "REACTIVATES"}
PUBLIC_VALIDATIONS = {"CURATED", "VALIDATED", "VERIFIED_SOURCE"}
CONTENT_FORMATS = {"LATEX", "TEXT"}
STABLE_CODE_RE = re.compile(r"^[A-Z0-9][A-Z0-9-]{2,79}$")
WINDOWS_DRIVE_RE = re.compile(r"^[A-Za-z]:")
REQUIRED_FILES = {"manifest.json", "resources.jsonl", "resource_instruction_links.jsonl", "sources.jsonl"}
ROOT_FILES = REQUIRED_FILES | {"README.md"}


class StrictPackageRecord(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


def _non_empty(value: str, *, maximum: int = 500) -> str:
    if not value.strip():
        raise ValueError("must not be empty")
    if len(value) > maximum:
        raise ValueError(f"must contain at most {maximum} characters")
    return value


class ManifestRecord(StrictPackageRecord):
    package_type: Literal["FICHEMATHS_PEDAGOGICAL_LIBRARY_PACKAGE"]
    schema_version: Literal["1.0"]
    package_version: StrictStr
    generated_at: StrictStr
    country: Literal["Bénin"]
    subject: Literal["Mathématiques"]
    supported_class_levels: list[Literal["4e"]]
    resource_count: StrictInt = Field(ge=0)
    source_count: StrictInt = Field(ge=0)
    link_count: StrictInt = Field(ge=0)
    file_hashes: dict[StrictStr, StrictStr]
    producer: StrictStr
    provenance_notice: StrictStr

    @field_validator("package_version", "producer", "provenance_notice")
    @classmethod
    def non_empty_strings(cls, value: str) -> str:
        return _non_empty(value, maximum=1000)

    @field_validator("generated_at")
    @classmethod
    def iso8601_with_timezone(cls, value: str) -> str:
        _non_empty(value, maximum=80)
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError as exc:
            raise ValueError("must be a valid ISO 8601 timestamp") from exc
        if parsed.tzinfo is None or parsed.utcoffset() is None:
            raise ValueError("must include an explicit timezone or Z")
        return value

    @field_validator("supported_class_levels")
    @classmethod
    def active_level_only(cls, value: list[str]) -> list[str]:
        if value != ["4e"]:
            raise ValueError('must equal ["4e"]')
        return value

    @field_validator("file_hashes")
    @classmethod
    def valid_hash_map(cls, value: dict[str, str]) -> dict[str, str]:
        for path, sha256 in value.items():
            if not path or path in {"manifest.json", "README.md"} or "\\" in path or PurePosixPath(path).is_absolute() or ".." in PurePosixPath(path).parts:
                raise ValueError(f"invalid package hash path: {path}")
            if not re.fullmatch(r"[0-9a-f]{64}", sha256):
                raise ValueError(f"invalid lowercase SHA-256 for: {path}")
        return value


class SourceRecord(StrictPackageRecord):
    source_code: StrictStr
    title: StrictStr
    document_type: StrictStr
    file_name: StrictStr
    sha256: StrictStr
    authority: StrictStr

    @field_validator("source_code")
    @classmethod
    def valid_code(cls, value: str) -> str:
        _non_empty(value, maximum=80)
        if not STABLE_CODE_RE.fullmatch(value): raise ValueError("invalid source code")
        return value

    @field_validator("title", "document_type", "file_name", "authority")
    @classmethod
    def required_strings(cls, value: str) -> str:
        return _non_empty(value)

    @field_validator("sha256")
    @classmethod
    def valid_sha256(cls, value: str) -> str:
        if not re.fullmatch(r"[0-9a-f]{64}", value): raise ValueError("invalid lowercase SHA-256")
        return value


class ResourceRecord(StrictPackageRecord):
    stable_code: StrictStr
    resource_type: StrictStr
    title: StrictStr | None = None
    content: StrictStr = Field(min_length=1)
    content_format: StrictStr = "LATEX"
    class_level: StrictStr
    curriculum_version: StrictStr
    SA_code: StrictStr | None = None
    sequence_code: StrictStr | None = None
    instruction_codes: list[StrictStr] = Field(min_length=1)
    origin_type: StrictStr
    validation_status: StrictStr
    visibility_scope: StrictStr = "CURATED_GLOBAL"
    source_code: StrictStr | None = None
    source_page: StrictStr | None = None
    author: StrictStr | None = None
    license_or_usage_note: StrictStr | None = None
    metadata: dict[str, Any]
    content_hash: StrictStr

    @field_validator("stable_code")
    @classmethod
    def valid_code(cls, value: str) -> str:
        if not STABLE_CODE_RE.fullmatch(value): raise ValueError("invalid stable code")
        return value

    @field_validator("resource_type", "class_level", "curriculum_version", "origin_type", "validation_status", "content_hash", "content_format", "visibility_scope")
    @classmethod
    def required_strings(cls, value: str) -> str:
        return _non_empty(value)

    @field_validator("title", "SA_code", "sequence_code", "source_code", "source_page", "author", "license_or_usage_note")
    @classmethod
    def optional_strings(cls, value: str | None) -> str | None:
        return _non_empty(value) if value is not None else None

    @field_validator("instruction_codes")
    @classmethod
    def valid_instruction_codes(cls, value: list[str]) -> list[str]:
        if len(value) != len(set(value)): raise ValueError("duplicate instruction code")
        for code in value:
            if not STABLE_CODE_RE.fullmatch(code): raise ValueError("invalid instruction code")
        return value


class ResourceInstructionLinkRecord(StrictPackageRecord):
    stable_code: StrictStr
    instruction_code: StrictStr
    relation_type: StrictStr
    relevance: StrictStr = "DIRECT"
    validation_status: Literal["VERIFIED_SOURCE", "CURATED", "VALIDATED", "USER_UNREVIEWED", "REJECTED", "ARCHIVED"] = "CURATED"
    provenance: dict[str, Any] = Field(default_factory=dict)

    @field_validator("stable_code", "instruction_code")
    @classmethod
    def valid_codes(cls, value: str) -> str:
        if not STABLE_CODE_RE.fullmatch(value): raise ValueError("invalid code")
        return value

    @field_validator("relation_type", "relevance", "validation_status")
    @classmethod
    def required_strings(cls, value: str) -> str:
        return _non_empty(value)


def _schema_error(file: str, line: int | None, error: dict) -> dict[str, Any]:
    kind = error.get("type", "value_error")
    code = {
        "missing": "MISSING_REQUIRED_FIELD",
        "extra_forbidden": "UNKNOWN_FIELD",
        "string_type": "INVALID_FIELD_TYPE",
        "int_type": "INVALID_FIELD_TYPE",
        "list_type": "INVALID_FIELD_TYPE",
        "dict_type": "INVALID_FIELD_TYPE",
        "literal_error": "INVALID_ENUM",
    }.get(kind, "INVALID_FIELD_VALUE")
    path = ".".join(str(part) for part in error.get("loc", ())) or None
    if path == "generated_at": code = "INVALID_ISO8601"
    if path and (path == "sha256" or path.endswith("content_hash") or path.startswith("file_hashes")): code = "INVALID_SHA256"
    if path and path.startswith("instruction_codes."): code = "INVALID_LIST_ELEMENT"
    # Diagnostics must themselves remain serializable even when a JSON key is invalid.
    safe = lambda text: text.encode("utf-8", errors="backslashreplace").decode("utf-8")
    return {"code": code, "file": file, "line": line, "field": safe(path) if path else None, "message": safe(error.get("msg", "Invalid value"))}


def _unicode_errors(value: Any, file: str, line: int | None) -> list[dict]:
    """Validate every decoded string, including extension keys/values, without rewriting it."""
    errors = []
    pending = [(value, "")]
    while pending:
        item, path = pending.pop()
        if isinstance(item, str):
            try:
                item.encode("utf-8", errors="strict")
            except UnicodeEncodeError:
                errors.append({"code": "INVALID_UNICODE", "file": file, "line": line,
                               "field": path or None, "message": "Text must be valid Unicode representable as UTF-8."})
        elif isinstance(item, dict):
            for key, child in item.items():
                safe_key = str(key).encode("utf-8", errors="backslashreplace").decode("utf-8")
                child_path = f"{path}.{safe_key}" if path else safe_key
                pending.extend(((key, child_path), (child, child_path)))
        elif isinstance(item, list):
            pending.extend((child, f"{path}.{index}") for index, child in enumerate(item))
    return errors


class JsonlRecord(dict):
    """Physical source position kept outside the package fields."""
    def __init__(self, value: dict, line: int):
        super().__init__(value)
        self.line = line


def _strict_records(model, rows: list[tuple[int, dict]], file: str, structured: list[dict]) -> list[dict]:
    validated = []
    for index, row in rows:
        try:
            record = model.model_validate(row).model_dump()
            unicode_errors = _unicode_errors(record, file, index)
            if unicode_errors:
                structured.extend(unicode_errors)
            else:
                validated.append(JsonlRecord(record, index))
        except ValidationError as exc:
            structured.extend(_schema_error(file, index, error) for error in exc.errors())
    return validated


def digest(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def require_package_admin(x_package_import_key: str | None = Header(None)) -> str:
    configured = settings.package_import_key
    if not configured or not x_package_import_key or not secrets.compare_digest(configured, x_package_import_key):
        raise HTTPException(403, "Import de package non autorisé.")
    return "package-admin"


def latest_version(db: Session, resource_id: int) -> m.PedagogicalResourceVersion | None:
    return db.scalar(select(m.PedagogicalResourceVersion).where(m.PedagogicalResourceVersion.resource_id == resource_id).order_by(m.PedagogicalResourceVersion.version_number.desc()))


def resource_view(db: Session, resource: m.PedagogicalResource) -> dict[str, Any]:
    version = latest_version(db, resource.id)
    links = db.execute(select(m.ResourceInstructionMapping, m.InstructionGuide).join(m.InstructionGuide, m.InstructionGuide.id == m.ResourceInstructionMapping.instruction_id).where(m.ResourceInstructionMapping.resource_version_id == version.id)).all() if version else []
    return {"id": resource.id, "stable_code": resource.code, "resource_version_id": version.id if version else None, "resource_type": resource.resource_type, "title": resource.title, "content": resource.content, "content_format": resource.content_format, "class_level": resource.level, "programme_version_id": resource.programme_version_id, "SA_id": resource.situation_id, "sequence_id": resource.sequence_id, "primary_instruction_id": resource.primary_instruction_id, "source_document_id": resource.source_document_id, "source_page": resource.source_page, "origin_type": resource.origin_type, "validation_status": resource.validation_status, "visibility_scope": resource.visibility_scope, "created_by": resource.created_by, "active": resource.active, "metadata": json.loads(resource.metadata_json or "{}"), "provenance": json.loads(resource.provenance_json or "{}"), "content_hash": resource.content_hash, "instruction_links": [{"instruction_id": instruction.id, "instruction_code": instruction.code, "relation_type": link.mapping_kind, "relevance": link.relevance} for link, instruction in links]}


class UserResourceInput(BaseModel):
    content: str = Field(min_length=1)
    class_level: str
    situation_id: int
    sequence_id: int
    instruction_ids: list[int] = Field(min_length=1)
    resource_type: str
    visibility_scope: str = "PRIVATE"
    title: str | None = None
    personal_source_note: str | None = None

    @field_validator("content")
    @classmethod
    def safe_resource_latex(cls, value: str) -> str:
        return ensure_safe_latex(value)


def validate_scope(db: Session, payload: UserResourceInput) -> list[m.InstructionGuide]:
    if payload.class_level != "4e":
        raise HTTPException(422, "P3 est activé uniquement pour la classe de 4e.")
    if payload.resource_type not in CONSIGNE_TYPES:
        raise HTTPException(422, "Le formulaire utilisateur accepte un type de consigne.")
    if payload.visibility_scope not in {"PRIVATE", "SHARED"}:
        raise HTTPException(422, "Visibilité utilisateur non autorisée.")
    sequence = db.get(m.Sequence, payload.sequence_id)
    if not sequence or sequence.situation_id != payload.situation_id:
        raise HTTPException(422, "SA ou séquence incohérente.")
    instructions = list(db.scalars(select(m.InstructionGuide).where(m.InstructionGuide.id.in_(payload.instruction_ids))).all())
    if len(instructions) != len(set(payload.instruction_ids)) or any(item.sequence_id != sequence.id for item in instructions):
        raise HTTPException(422, "Au moins une instruction valide de la séquence est requise.")
    return instructions


@router.get("/pedagogical-resources")
def list_resources(instruction_id: int | None = None, resource_type: str | None = None, x_teacher_id: str | None = Header(None), db: Session = Depends(get_db)):
    owner = teacher_identity(x_teacher_id)
    query = select(m.PedagogicalResource)
    if resource_type:
        query = query.where(m.PedagogicalResource.resource_type == resource_type)
    if instruction_id:
        query = query.join(m.PedagogicalResourceVersion, m.PedagogicalResourceVersion.resource_id == m.PedagogicalResource.id).join(m.ResourceInstructionMapping, m.ResourceInstructionMapping.resource_version_id == m.PedagogicalResourceVersion.id).where(m.ResourceInstructionMapping.instruction_id == instruction_id)
    result = []
    for item in db.scalars(query.order_by(m.PedagogicalResource.code)).unique():
        version = latest_version(db, item.id)
        context = {instruction_id} if instruction_id is not None else None
        if version and is_resource_eligible_for_teacher_and_context(db, item, version, owner, context):
            result.append(resource_view(db, item))
    return result


@router.get("/pedagogical-resources/by-instruction/{instruction_id}")
def by_instruction(instruction_id: int, x_teacher_id: str | None = Header(None), db: Session = Depends(get_db)):
    return list_resources(instruction_id, None, x_teacher_id, db)


@router.get("/pedagogical-resources/contribution-context/{instruction_id}")
def contribution_context(instruction_id: int, db: Session = Depends(get_db)):
    instruction = db.get(m.InstructionGuide, instruction_id)
    sequence = db.get(m.Sequence, instruction.sequence_id) if instruction else None
    if not instruction or not sequence: raise HTTPException(404, "Instruction introuvable.")
    return {"instruction_id": instruction.id, "sequence_id": sequence.id, "situation_id": sequence.situation_id, "class_level": "4e"}


@router.get("/pedagogical-resources/{resource_id}")
def get_resource(resource_id: int, x_teacher_id: str | None = Header(None), db: Session = Depends(get_db)):
    resource = db.get(m.PedagogicalResource, resource_id)
    version = latest_version(db, resource.id) if resource else None
    if not resource or not version or not is_resource_eligible_for_teacher_and_context(db, resource, version, x_teacher_id):
        raise HTTPException(404, "Ressource introuvable.")
    return resource_view(db, resource)


def store_user_resource(db: Session, payload: UserResourceInput, owner: str, resource: m.PedagogicalResource | None = None):
    instructions = validate_scope(db, payload)
    sequence = db.get(m.Sequence, payload.sequence_id)
    situation = db.get(m.SituationApprentissage, payload.situation_id)
    if resource is None:
        resource = m.PedagogicalResource(code=f"USR-{uuid4().hex[:16].upper()}", title=payload.title or "Consigne enseignant", resource_type=payload.resource_type, level="4e", provenance_kind="USER", created_by=owner)
        db.add(resource)
        db.flush()
    resource.title = payload.title or resource.title
    resource.resource_type = payload.resource_type
    resource.content = payload.content
    resource.content_format = "LATEX"
    resource.programme_version_id = situation.programme_version_id
    resource.situation_id = situation.id
    resource.sequence_id = sequence.id
    resource.primary_instruction_id = instructions[0].id
    resource.origin_type = "USER_CONTRIBUTED"
    resource.validation_status = "USER_UNREVIEWED"
    resource.visibility_scope = payload.visibility_scope
    resource.updated_at = datetime.now(UTC).replace(tzinfo=None)
    resource.metadata_json = json.dumps({}, ensure_ascii=False)
    resource.provenance_json = json.dumps({"personal_source_note": payload.personal_source_note}, ensure_ascii=False)
    resource.content_hash = digest(payload.content)
    number = (db.scalar(select(m.PedagogicalResourceVersion.version_number).where(m.PedagogicalResourceVersion.resource_id == resource.id).order_by(m.PedagogicalResourceVersion.version_number.desc())) or 0) + 1
    version = m.PedagogicalResourceVersion(resource_id=resource.id, version_number=number, title=resource.title, summary=payload.content[:200], status="AVAILABLE", provenance_json=resource.provenance_json)
    db.add(version); db.flush()
    db.add(m.PedagogicalBlock(resource_version_id=version.id, block_type="CONSIGNE", title=resource.title, content_latex=payload.content, position=1))
    for index, instruction in enumerate(instructions):
        db.add(m.ResourceInstructionMapping(resource_version_id=version.id, instruction_id=instruction.id, mapping_kind="PRIMARY" if index == 0 else "SUPPORTS", validation_status="USER_UNREVIEWED", created_by=owner, provenance_json=resource.provenance_json))
    db.commit(); db.refresh(resource)
    return resource_view(db, resource)


@router.post("/pedagogical-resources/user", status_code=201)
def create_user_resource(payload: UserResourceInput, x_teacher_id: str | None = Header(None), db: Session = Depends(get_db)):
    return store_user_resource(db, payload, teacher_identity(x_teacher_id))


@router.put("/pedagogical-resources/user/{resource_id}")
def update_user_resource(resource_id: int, payload: UserResourceInput, x_teacher_id: str | None = Header(None), db: Session = Depends(get_db)):
    resource = db.get(m.PedagogicalResource, resource_id)
    owner = teacher_identity(x_teacher_id)
    if not resource or resource.created_by != owner or resource.origin_type != "USER_CONTRIBUTED":
        raise HTTPException(403, "Seul le propriétaire peut modifier cette contribution.")
    return store_user_resource(db, payload, owner, resource)


def resource_snapshot(db: Session, version: m.PedagogicalResourceVersion) -> dict[str, Any]:
    return build_resource_snapshot(db, version)


class SheetResourcesInput(BaseModel):
    resource_version_ids: list[int]


@router.get("/sheets/{revision_id}/resources")
def sheet_resources(revision_id: int, db: Session = Depends(get_db)):
    return [{"id": row.id, "position": row.position, "snapshot": json.loads(row.snapshot_json or "{}")} for row in db.scalars(select(m.SheetResourceInstance).where(m.SheetResourceInstance.teacher_revision_id == revision_id).order_by(m.SheetResourceInstance.position))]


@router.put("/sheets/{revision_id}/resources")
def replace_sheet_resources(revision_id: int, payload: SheetResourcesInput, x_teacher_id: str | None = Header(None), db: Session = Depends(get_db)):
    revision = db.get(m.TeacherSheetRevision, revision_id); require_draft(revision)
    owner = teacher_identity(x_teacher_id)
    validated: list[m.PedagogicalResourceVersion] = []
    for version_id in payload.resource_version_ids:
        version = db.get(m.PedagogicalResourceVersion, version_id); resource = db.get(m.PedagogicalResource, version.resource_id) if version else None
        segment_ids = revision_instruction_ids(db, revision_id)
        if not resource or not version or not is_resource_eligible_for_teacher_and_context(db, resource, version, owner, segment_ids):
            raise HTTPException(403, "Ressource non utilisable dans le périmètre de cette fiche.")
        validated.append(version)
    try:
        old = list(db.scalars(select(m.SheetResourceInstance).where(m.SheetResourceInstance.teacher_revision_id == revision_id)))
        for row in old:
            block_ids = list(db.scalars(select(m.SheetBlockInstance.id).where(m.SheetBlockInstance.resource_instance_id == row.id)))
            if block_ids: db.execute(delete(m.FlowItem).where(m.FlowItem.block_instance_id.in_(block_ids)))
            db.execute(delete(m.SheetBlockInstance).where(m.SheetBlockInstance.resource_instance_id == row.id)); db.delete(row)
        db.flush()
        for version in validated:
            copy_library_to_sheet(db, revision_id, version.id, teacher_id=owner, commit=False)
        sync_documents(db, revision_id, commit=False)
        db.commit()
    except Exception:
        db.rollback()
        raise
    return sheet_resources(revision_id, db)


class HomeworkItem(BaseModel):
    pedagogical_resource_id: int
    homework_usage_type: str
    teacher_note: str | None = None


class HomeworkInput(BaseModel):
    items: list[HomeworkItem]


def homework_view(db: Session, revision_id: int):
    return [{"id": row.id, "pedagogical_resource_id": row.pedagogical_resource_id, "resource_version_id": row.resource_version_id, "homework_usage_type": row.homework_usage_type, "selected_order": row.selected_order, "teacher_note": row.teacher_note, "snapshot": json.loads(row.snapshot_json)} for row in db.scalars(select(m.TeacherSheetHomeworkSelection).where(m.TeacherSheetHomeworkSelection.teacher_revision_id == revision_id).order_by(m.TeacherSheetHomeworkSelection.selected_order))]


@router.get("/sheets/{revision_id}/homework")
def get_homework(revision_id: int, db: Session = Depends(get_db)):
    if not db.get(m.TeacherSheetRevision, revision_id): raise HTTPException(404, "Révision introuvable.")
    return homework_view(db, revision_id)


@router.put("/sheets/{revision_id}/homework")
def put_homework(revision_id: int, payload: HomeworkInput, x_teacher_id: str | None = Header(None), db: Session = Depends(get_db)):
    revision = db.get(m.TeacherSheetRevision, revision_id); require_draft(revision)
    owner = teacher_identity(x_teacher_id); db.execute(delete(m.TeacherSheetHomeworkSelection).where(m.TeacherSheetHomeworkSelection.teacher_revision_id == revision_id))
    for index, item in enumerate(payload.items):
        if item.homework_usage_type not in {"CURRENT_SCOPE", "PRIOR_NOTION_REACTIVATION"}: raise HTTPException(422, "Usage homework invalide.")
        resource = db.get(m.PedagogicalResource, item.pedagogical_resource_id); version = latest_version(db, resource.id) if resource else None
        if not resource or not version or resource.resource_type not in {"HOMEWORK_EXERCISE", "REACTIVATION_EXERCISE"} or not is_resource_eligible_for_teacher_and_context(db, resource, version, owner): raise HTTPException(422, "Exercice de maison non utilisable.")
        if item.homework_usage_type == "CURRENT_SCOPE":
            if not is_resource_eligible_for_teacher_and_context(db, resource, version, owner, revision_instruction_ids(db, revision_id)): raise HTTPException(422, "Exercice extérieur au périmètre courant.")
        db.add(m.TeacherSheetHomeworkSelection(teacher_revision_id=revision_id, pedagogical_resource_id=resource.id, resource_version_id=version.id, homework_usage_type=item.homework_usage_type, selected_order=index, teacher_note=item.teacher_note, snapshot_json=json.dumps(resource_snapshot(db, version), ensure_ascii=False)))
    db.flush()
    sync_documents(db, revision_id, commit=False); db.commit()
    return homework_view(db, revision_id)


class ManualDocument(BaseModel):
    display_label: str = Field(min_length=1)
    author: str | None = None
    title: str | None = None
    edition: str | None = None
    note: str | None = None


class DocumentsInput(BaseModel):
    manual: list[ManualDocument]


def sync_documents(db: Session, revision_id: int, *, commit: bool = True):
    revision = db.get(m.TeacherSheetRevision, revision_id)
    if not revision or revision.status != "DRAFT": return
    manual = list(db.scalars(select(m.TeacherSheetDocumentReference).where(m.TeacherSheetDocumentReference.teacher_revision_id == revision_id, m.TeacherSheetDocumentReference.origin == "MANUAL_REFERENCE").order_by(m.TeacherSheetDocumentReference.selected_order)))
    db.execute(delete(m.TeacherSheetDocumentReference).where(m.TeacherSheetDocumentReference.teacher_revision_id == revision_id, m.TeacherSheetDocumentReference.origin == "AUTO_DERIVED"))
    sources: dict[tuple[int, str | None], dict] = {}
    state = json.loads(revision.authoring_json or "{}")
    has_explicit_selections = isinstance(state, dict) and "selections" in state
    current_instance_ids = {
        selection.get("instance_id")
        for selection in state.get("selections", {}).values()
        if isinstance(selection, dict) and selection.get("instance_id") is not None
    }
    flow_block_ids = set(
        db.scalars(
            select(m.FlowItem.block_instance_id).where(
                m.FlowItem.teacher_revision_id == revision_id,
                m.FlowItem.block_instance_id.is_not(None),
            )
        )
    )
    effective_instances = []
    for instance in db.scalars(
        select(m.SheetResourceInstance).where(m.SheetResourceInstance.teacher_revision_id == revision_id)
    ):
        if not has_explicit_selections:
            effective_instances.append(instance)
            continue
        if instance.id in current_instance_ids:
            effective_instances.append(instance)
            continue
        has_visible_flow_block = db.scalar(
            select(m.SheetBlockInstance.id).where(
                m.SheetBlockInstance.resource_instance_id == instance.id,
                m.SheetBlockInstance.visible.is_(True),
                m.SheetBlockInstance.id.in_(flow_block_ids),
            ).limit(1)
        )
        if has_visible_flow_block:
            effective_instances.append(instance)
    snapshots = [json.loads(row.snapshot_json or "{}") for row in effective_instances]
    snapshots += [json.loads(row.snapshot_json) for row in db.scalars(select(m.TeacherSheetHomeworkSelection).where(m.TeacherSheetHomeworkSelection.teacher_revision_id == revision_id))]
    for snapshot in snapshots:
        source_id, source_version = snapshot.get("source_document_id"), snapshot.get("source_version")
        if source_id: sources[(int(source_id), source_version)] = snapshot
    for index, ((source_id, source_version), snapshot) in enumerate(sorted(sources.items(), key=lambda item: (item[0][0], item[0][1] or ""))):
        label = snapshot.get("source_label") or f"Source {source_id}"
        source_snapshot = {"source_document_id": source_id, "source_version": source_version, "code": snapshot.get("source_code"), "title": label, "document_type": snapshot.get("source_document_type"), "authority": snapshot.get("source_authority"), "page": snapshot.get("source_page"), "provenance": snapshot.get("provenance", {})}
        db.add(m.TeacherSheetDocumentReference(teacher_revision_id=revision_id, origin="AUTO_DERIVED", source_document_id=source_id, source_version=source_version, display_label=label, author=snapshot.get("source_authority"), title=label, note=snapshot.get("source_page"), selected_order=index, snapshot_json=json.dumps(source_snapshot, ensure_ascii=False)))
    for offset, row in enumerate(manual, len(sources)):
        row.selected_order = offset
    if commit: db.commit()
    else: db.flush()


def documents_view(db: Session, revision_id: int):
    return [{"id": row.id, "origin": row.origin, "source_document_id": row.source_document_id, "source_version": row.source_version, "display_label": row.display_label, "author": row.author, "title": row.title, "edition": row.edition, "note": row.note, "selected_order": row.selected_order} for row in db.scalars(select(m.TeacherSheetDocumentReference).where(m.TeacherSheetDocumentReference.teacher_revision_id == revision_id).order_by(m.TeacherSheetDocumentReference.selected_order))]


@router.get("/sheets/{revision_id}/documents-used")
def get_documents(revision_id: int, db: Session = Depends(get_db)):
    if not db.get(m.TeacherSheetRevision, revision_id): raise HTTPException(404, "Révision introuvable.")
    return documents_view(db, revision_id)


@router.put("/sheets/{revision_id}/documents-used")
def put_documents(revision_id: int, payload: DocumentsInput, db: Session = Depends(get_db)):
    revision = db.get(m.TeacherSheetRevision, revision_id); require_draft(revision)
    db.execute(delete(m.TeacherSheetDocumentReference).where(m.TeacherSheetDocumentReference.teacher_revision_id == revision_id, m.TeacherSheetDocumentReference.origin == "MANUAL_REFERENCE")); sync_documents(db, revision_id, commit=False)
    start = len(documents_view(db, revision_id))
    for index, item in enumerate(payload.manual, start):
        snap = item.model_dump()
        db.add(m.TeacherSheetDocumentReference(teacher_revision_id=revision_id, origin="MANUAL_REFERENCE", display_label=item.display_label, author=item.author, title=item.title, edition=item.edition, note=item.note, selected_order=index, snapshot_json=json.dumps(snap, ensure_ascii=False)))
    db.commit(); return documents_view(db, revision_id)


def _allowed_member(name: str) -> bool:
    if name in ROOT_FILES:
        return True
    if name.startswith("figures/"):
        return PurePosixPath(name).suffix.lower() in {".png", ".jpg", ".jpeg", ".webp", ".pdf"}
    if name.startswith("attachments/"):
        return PurePosixPath(name).suffix.lower() in {".png", ".jpg", ".jpeg", ".webp", ".pdf", ".txt", ".csv"}
    return False


def read_package(raw: bytes, structured: list[dict] | None = None) -> tuple[dict, dict[str, bytes], list[tuple[int, dict]], list[tuple[int, dict]], list[tuple[int, dict]], list[str]]:
    if structured is None:
        structured = []
    errors: list[str] = []
    files: dict[str, bytes] = {}
    if len(raw) > settings.package_max_compressed_bytes:
        return {}, {}, [], [], [], ["ARCHIVE_COMPRESSED_SIZE_EXCEEDED"]
    try:
        with zipfile.ZipFile(io.BytesIO(raw)) as archive:
            members = archive.infolist()
            if len(members) > settings.package_max_members: errors.append("ARCHIVE_MEMBER_COUNT_EXCEEDED")
            total = 0
            seen: set[str] = set()
            for info in members:
                raw_name = info.filename
                if info.is_dir(): continue
                name = unicodedata.normalize("NFC", raw_name)
                key = name.casefold()
                path = PurePosixPath(name)
                mode = info.external_attr >> 16
                total += info.file_size
                if key in seen: errors.append(f"DUPLICATE_MEMBER: {name}")
                seen.add(key)
                if raw_name != name or "\\" in name or path.is_absolute() or WINDOWS_DRIVE_RE.match(name) or name.startswith("//") or ".." in path.parts: errors.append(f"UNSAFE_MEMBER_PATH: {name}")
                if not _allowed_member(name): errors.append(f"UNSUPPORTED_PACKAGE_MEMBER: {name}")
                if stat.S_ISLNK(mode): errors.append(f"SYMLINK_MEMBER_REJECTED: {name}")
                if info.flag_bits & 0x1: errors.append(f"ENCRYPTED_MEMBER_REJECTED: {name}")
                if info.file_size > settings.package_max_member_bytes: errors.append(f"MEMBER_SIZE_EXCEEDED: {name}")
                ratio = info.file_size / max(info.compress_size, 1)
                if ratio > settings.package_max_compression_ratio: errors.append(f"COMPRESSION_RATIO_EXCEEDED: {name}")
            if total > settings.package_max_uncompressed_bytes: errors.append("ARCHIVE_UNCOMPRESSED_SIZE_EXCEEDED")
            if not errors:
                files = {info.filename: archive.read(info) for info in members if not info.is_dir()}
    except Exception as exc:
        errors.append(f"ZIP_INVALID: {exc}")
    for name in sorted(REQUIRED_FILES - files.keys()): errors.append(f"MISSING_FILE: {name}")
    try: manifest = json.loads(files.get("manifest.json", b"{}").decode("utf-8", errors="strict"))
    except Exception as exc: manifest, errors = {}, errors + [f"MANIFEST_INVALID: {exc}"]
    def jsonl(name):
        rows = []
        try: lines = files.get(name, b"").decode("utf-8", errors="strict").splitlines()
        except UnicodeDecodeError as exc:
            message = f"UTF8_INVALID: {name}: {exc}"
            number = len(re.findall(rb"\r\n|\r|\n", files.get(name, b"")[:exc.start])) + 1
            errors.append(message)
            structured.append({"code": "UTF8_INVALID", "file": name, "line": number, "field": None, "message": message})
            return rows
        for number, line in enumerate(lines, 1):
            if not line.strip(): continue
            try:
                row = json.loads(line)
                if not isinstance(row, dict): raise ValueError("object expected")
                rows.append((number, row))
            except Exception as exc:
                message = f"JSONL_INVALID: {name}:{number}: {exc}"
                errors.append(message)
                structured.append({"code": "JSONL_INVALID", "file": name, "line": number, "field": None, "message": message})
        return rows
    return manifest, files, jsonl("resources.jsonl"), jsonl("resource_instruction_links.jsonl"), jsonl("sources.jsonl"), errors


def _source_values(row: dict) -> tuple:
    return tuple(row.get(key, "") for key in ("title", "document_type", "file_name", "sha256", "authority"))


def validate_package(db: Session, raw: bytes) -> tuple[dict, tuple]:
    structured_errors: list[dict[str, Any]] = []
    manifest, files, resources, links, sources, errors = read_package(raw, structured_errors)
    parse_error_count = len(structured_errors)
    try:
        manifest = ManifestRecord.model_validate(manifest).model_dump()
        unicode_errors = _unicode_errors(manifest, "manifest.json", None)
        if unicode_errors:
            structured_errors.extend(unicode_errors)
            manifest = {}
    except ValidationError as exc:
        structured_errors.extend(_schema_error("manifest.json", None, error) for error in exc.errors())
        manifest = {}
    resources = _strict_records(ResourceRecord, resources, "resources.jsonl", structured_errors)
    links = _strict_records(ResourceInstructionLinkRecord, links, "resource_instruction_links.jsonl", structured_errors)
    sources = _strict_records(SourceRecord, sources, "sources.jsonl", structured_errors)
    legacy_prefix = {"manifest.json": "MANIFEST_CONTRACT_INVALID", "resources.jsonl": "RESOURCE_SCHEMA_INVALID", "resource_instruction_links.jsonl": "LINK_INVALID", "sources.jsonl": "SOURCE_SCHEMA_INVALID"}
    errors.extend(f"{legacy_prefix[error['file']]}: {error['code']}:{error['file']}:{error['line'] or '-'}:{error['field'] or '-'}: {error['message']}" for error in structured_errors[parse_error_count:])
    hashes = manifest.get("file_hashes") if isinstance(manifest.get("file_hashes"), dict) else {}
    hash_required = {name for name in files if name not in {"manifest.json", "README.md"}}
    for name in sorted(hash_required - hashes.keys()): errors.append(f"HASH_MISSING: {name}")
    for name, expected in hashes.items():
        if name not in files: errors.append(f"MISSING_FILE: {name}")
        elif not isinstance(expected, str) or hashlib.sha256(files[name]).hexdigest() != expected: errors.append(f"HASH_MISMATCH: {name}")
    if manifest.get("resource_count") != len(resources) or manifest.get("source_count") != len(sources) or manifest.get("link_count") != len(links): errors.append("MANIFEST_COUNT_MISMATCH")

    def record_error(message: str, file: str, row: JsonlRecord):
        errors.append(message)
        structured_errors.append({"code": message.split(":", 1)[0], "file": file,
                                  "line": row.line, "field": None, "message": message})

    required_source = {"source_code", "title", "document_type", "file_name", "sha256", "authority"}
    source_codes = [row.get("source_code") for row in sources]
    if None in source_codes or len(source_codes) != len(set(source_codes)):
        seen_sources = set()
        for row in sources:
            code = row.get("source_code")
            if code is None or code in seen_sources:
                record_error("DUPLICATE_SOURCE_CODE", "sources.jsonl", row)
            seen_sources.add(code)
    existing_sources = {row.code: row for row in db.scalars(select(m.SourceDocument))}
    for row in sources:
        code = row.get("source_code")
        if not required_source <= set(row) or not isinstance(code, str) or not STABLE_CODE_RE.fullmatch(code) or not re.fullmatch(r"[0-9a-fA-F]{64}", str(row.get("sha256", ""))): record_error(f"SOURCE_SCHEMA_INVALID: {code}", "sources.jsonl", row)
        existing = existing_sources.get(code)
        if existing and _source_values(row) != (existing.title, existing.document_type, existing.file_name, existing.sha256, existing.authority): record_error(f"SOURCE_CONFLICT: {code}", "sources.jsonl", row)
    known_source_codes = set(existing_sources) | set(source_codes)

    instruction_map = {row.code: row for row in db.scalars(select(m.InstructionGuide))}
    sequence_map = {row.code: row for row in db.scalars(select(m.Sequence))}
    situation_map = {row.code: row for row in db.scalars(select(m.SituationApprentissage))}
    programme_map = {row.code: row for row in db.scalars(select(m.ProgrammeVersion))}
    required_resource = {"stable_code", "resource_type", "content", "class_level", "curriculum_version", "instruction_codes", "origin_type", "validation_status", "metadata", "content_hash"}
    package_codes = [row.get("stable_code") for row in resources]
    if None in package_codes or len(package_codes) != len(set(package_codes)):
        seen_resources = set()
        for row in resources:
            code = row.get("stable_code")
            if code is None or code in seen_resources:
                record_error("DUPLICATE_STABLE_CODE", "resources.jsonl", row)
            seen_resources.add(code)
    new = unchanged = conflicts = 0
    for row in resources:
        code = row.get("stable_code")
        if not required_resource <= set(row) or not isinstance(code, str) or not STABLE_CODE_RE.fullmatch(code) or not isinstance(row.get("content"), str) or not isinstance(row.get("instruction_codes"), list) or not row.get("instruction_codes") or not isinstance(row.get("metadata"), dict): record_error(f"RESOURCE_SCHEMA_INVALID: {code}", "resources.jsonl", row)
        if row.get("resource_type") not in RESOURCE_TYPES or row.get("origin_type") not in ORIGINS or row.get("validation_status") not in VALIDATIONS or row.get("visibility_scope", "CURATED_GLOBAL") not in VISIBILITIES or row.get("content_format", "LATEX") not in CONTENT_FORMATS: record_error(f"ENUM_INVALID: {code}", "resources.jsonl", row)
        content = row.get("content") if isinstance(row.get("content"), str) else ""
        if len(content.encode("utf-8")) > settings.package_max_member_bytes or (row.get("content_format", "LATEX") == "LATEX" and latex_violation(content)): record_error(f"CONTENT_UNSAFE: {code}", "resources.jsonl", row)
        if row.get("class_level") != "4e": record_error(f"CLASS_LEVEL_UNSUPPORTED: {code}", "resources.jsonl", row)
        if row.get("content_hash") != digest(content): record_error(f"CONTENT_HASH_MISMATCH: {code}", "resources.jsonl", row)
        if row.get("source_code") and row.get("source_code") not in known_source_codes: record_error(f"SOURCE_UNKNOWN: {row.get('source_code')}", "resources.jsonl", row)
        programme = programme_map.get(row.get("curriculum_version")); situation = situation_map.get(row.get("SA_code")) if row.get("SA_code") else None; sequence = sequence_map.get(row.get("sequence_code")) if row.get("sequence_code") else None
        if not programme: record_error(f"CURRICULUM_UNKNOWN: {code}", "resources.jsonl", row)
        if row.get("SA_code") and not situation: record_error(f"SA_UNKNOWN: {code}", "resources.jsonl", row)
        if row.get("sequence_code") and not sequence: record_error(f"SEQUENCE_UNKNOWN: {code}", "resources.jsonl", row)
        if sequence and situation and sequence.situation_id != situation.id: record_error(f"RESOURCE_SCOPE_CONFLICT: {code}", "resources.jsonl", row)
        instructions = [instruction_map.get(item) for item in row.get("instruction_codes", [])]
        if any(item is None for item in instructions): record_error(f"INSTRUCTION_UNKNOWN: {code}", "resources.jsonl", row)
        for instruction in [item for item in instructions if item]:
            ins_sequence = db.get(m.Sequence, instruction.sequence_id); ins_situation = db.get(m.SituationApprentissage, ins_sequence.situation_id)
            if (sequence and ins_sequence.id != sequence.id) or (situation and ins_situation.id != situation.id) or (programme and ins_situation.programme_version_id != programme.id): record_error(f"RESOURCE_SCOPE_CONFLICT: {code}", "resources.jsonl", row)
        figure_path = row.get("metadata", {}).get("figure_path") if isinstance(row.get("metadata"), dict) else None
        if row.get("resource_type") == "FIGURE":
            if not isinstance(figure_path, str) or figure_path not in files or not figure_path.startswith("figures/") or figure_path not in hashes: record_error(f"FIGURE_INVALID: {code}", "resources.jsonl", row)
        existing = db.scalar(select(m.PedagogicalResource).where(m.PedagogicalResource.code == code))
        if not existing: new += 1
        elif existing.content_hash == row.get("content_hash"): unchanged += 1
        else: conflicts += 1; record_error(f"STABLE_CODE_CONFLICT: {code}", "resources.jsonl", row)
    resource_by_code = {row.get("stable_code"): row for row in resources}
    for row in links:
        resource_row = resource_by_code.get(row.get("stable_code"))
        if not {"stable_code", "instruction_code", "relation_type"} <= set(row) or not resource_row or row.get("instruction_code") not in instruction_map or row.get("instruction_code") not in resource_row.get("instruction_codes", []) or row.get("relation_type") not in RELATIONS: record_error(f"LINK_INVALID: {row}", "resource_instruction_links.jsonl", row)
    errors = list(dict.fromkeys(errors))
    generic_structured = [{"code": error.split(":", 1)[0].replace(" ", "_"), "file": None, "line": None, "field": None, "message": error} for error in errors if not any(error.endswith(item["message"]) and item["code"] in error for item in structured_errors)]
    report = {"package_version": manifest.get("package_version"), "new_resources": new, "unchanged_resources": unchanged, "divergent_resources": conflicts, "references_not_found": [e for e in errors if "UNKNOWN" in e], "invalid_links": [e for e in errors if e.startswith("LINK_INVALID")], "invalid_sources": [e for e in errors if e.startswith(("SOURCE_", "SOURCE_SCHEMA")) or "sources.jsonl" in e], "missing_files": [e for e in errors if e.startswith("MISSING_FILE")], "hash_mismatches": [e for e in errors if "HASH_" in e or "INVALID_SHA256" in e], "stable_code_conflicts": [e for e in errors if "STABLE_CODE_CONFLICT" in e], "validation_errors": structured_errors + generic_structured, "blocking_errors": errors, "can_import": not errors}
    return report, (manifest, resources, links, sources)


@router.post("/admin/resource-packages/dry-run")
async def package_dry_run(package: UploadFile, _admin: str = Depends(require_package_admin), db: Session = Depends(get_db)):
    report, _ = validate_package(db, await package.read()); return report


def _latex_text(value: str) -> str:
    replacements = {"\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "$": r"\$", "#": r"\#", "_": r"\_", "{": r"\{", "}": r"\}", "~": r"\textasciitilde{}", "^": r"\textasciicircum{}"}
    return "".join(replacements.get(char, char) for char in value)


@router.post("/admin/resource-packages/import")
async def package_import(package: UploadFile, _admin: str = Depends(require_package_admin), db: Session = Depends(get_db)):
    raw = await package.read(); report, parsed = validate_package(db, raw)
    if not report["can_import"]: raise HTTPException(422, report)
    manifest, resources, links, sources = parsed
    try:
        source_map = {row.code: row for row in db.scalars(select(m.SourceDocument))}
        for row in sources:
            if row["source_code"] not in source_map:
                source = m.SourceDocument(code=row["source_code"], title=row["title"], document_type=row["document_type"], file_name=row["file_name"], sha256=row["sha256"], authority=row["authority"]); db.add(source); db.flush(); source_map[source.code] = source
        instruction_map = {row.code: row for row in db.scalars(select(m.InstructionGuide))}; sequence_map = {row.code: row for row in db.scalars(select(m.Sequence))}; situation_map = {row.code: row for row in db.scalars(select(m.SituationApprentissage))}; programme_map = {row.code: row for row in db.scalars(select(m.ProgrammeVersion))}
        resource_map = {row.code: row for row in db.scalars(select(m.PedagogicalResource))}; version_map = {}
        for row in resources:
            if row["stable_code"] in resource_map: continue
            source = source_map.get(row.get("source_code")); instruction = instruction_map[row["instruction_codes"][0]]; sequence = sequence_map.get(row.get("sequence_code")) or db.get(m.Sequence, instruction.sequence_id); situation = situation_map.get(row.get("SA_code")) or db.get(m.SituationApprentissage, sequence.situation_id); programme = programme_map[row["curriculum_version"]]
            resource = m.PedagogicalResource(code=row["stable_code"], title=row.get("title") or row["stable_code"], resource_type=row["resource_type"], level=row["class_level"], provenance_kind="SOURCED", content=row["content"], content_format=row.get("content_format", "LATEX"), programme_version_id=programme.id, situation_id=situation.id, sequence_id=sequence.id, primary_instruction_id=instruction.id, source_document_id=source.id if source else None, source_page=row.get("source_page"), origin_type=row["origin_type"], validation_status=row["validation_status"], visibility_scope=row.get("visibility_scope", "CURATED_GLOBAL"), metadata_json=json.dumps(row["metadata"], ensure_ascii=False), provenance_json=json.dumps({"package_version": manifest["package_version"], "author": row.get("author"), "license_or_usage_note": row.get("license_or_usage_note")}, ensure_ascii=False), content_hash=row["content_hash"]); db.add(resource); db.flush()
            version = m.PedagogicalResourceVersion(resource_id=resource.id, version_number=1, title=resource.title, summary=row["content"][:200], provenance_json=resource.provenance_json); db.add(version); db.flush(); block_content = row["content"] if resource.content_format == "LATEX" else _latex_text(row["content"]); db.add(m.PedagogicalBlock(resource_version_id=version.id, block_type="EXERCISE" if "EXERCISE" in resource.resource_type else "CONSIGNE", title=resource.title, content_latex=block_content, position=1)); resource_map[resource.code] = resource; version_map[resource.code] = version
        for row in links:
            resource, instruction = resource_map[row["stable_code"]], instruction_map[row["instruction_code"]]; version = version_map.get(resource.code) or latest_version(db, resource.id)
            exists = db.scalar(select(m.ResourceInstructionMapping).where(m.ResourceInstructionMapping.resource_version_id == version.id, m.ResourceInstructionMapping.instruction_id == instruction.id))
            if not exists: db.add(m.ResourceInstructionMapping(resource_version_id=version.id, instruction_id=instruction.id, mapping_kind=row["relation_type"], relevance=row.get("relevance", "DIRECT"), validation_status=row.get("validation_status", "CURATED"), provenance_json=json.dumps(row.get("provenance", {}), ensure_ascii=False)))
        db.flush()
        for row in resources:
            if not db.scalar(select(m.PedagogicalResource.id).where(m.PedagogicalResource.code == row["stable_code"])): raise RuntimeError("Post-import resource verification failed")
        manifest_hash = hashlib.sha256(files_manifest_bytes(raw)).hexdigest()
        if not db.scalar(select(m.PackageImportRecord).where(m.PackageImportRecord.manifest_hash == manifest_hash)):
            db.add(m.PackageImportRecord(package_version=manifest["package_version"], schema_version=manifest["schema_version"], manifest_hash=manifest_hash, imported_by="package-admin", resource_count=len(resources), source_count=len(sources), link_count=len(links), status="IMPORTED", report_json=json.dumps(report, ensure_ascii=False)))
        db.commit()
    except Exception:
        db.rollback(); raise
    report["imported_resources"] = report["new_resources"]; return report


def files_manifest_bytes(raw: bytes) -> bytes:
    with zipfile.ZipFile(io.BytesIO(raw)) as archive: return archive.read("manifest.json")
