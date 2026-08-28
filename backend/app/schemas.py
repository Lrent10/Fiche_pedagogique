from typing import Literal

from pydantic import BaseModel, Field


class SheetCreate(BaseModel):
    title: str
    instruction_ids: list[int]
    duration_minutes: int = 55
    class_label: str = "4e"


class AddLibraryResource(BaseModel):
    resource_version_id: int
    adaptation_note: str = ""


class AddLocalResource(BaseModel):
    title: str
    block_type: str = "ACTIVITY"
    content_latex: str


class BlockUpdate(BaseModel):
    title: str | None = None
    content_latex: str | None = None
    visible: bool | None = None


class FlowUpdate(BaseModel):
    ordered_block_ids: list[int]


class FlowItemUpdate(BaseModel):
    teacher_action: str | None = None
    learner_action: str | None = None
    strategy: str | None = None
    duration_minutes: int | None = Field(default=None, ge=0)
    expected_result_latex: str | None = None


class SupportCreate(BaseModel):
    title: str


class SheetFromSupportCreate(BaseModel):
    title: str | None = None
    selected_block_ids: list[int] = Field(min_length=1)
    instruction_ids: list[int] = Field(default_factory=list)
    duration_minutes: int = Field(default=55, ge=1)
    class_label: str = "4e"
    part_label: str = ""


class TeachingSessionCreate(BaseModel):
    teacher_revision_id: int
    taught_on: str
    class_label: str
    actual_minutes: int = 55
    status: Literal["DONE", "PARTIAL", "SKIPPED"] = "DONE"
    notes: str = ""


class SupportUseCreate(BaseModel):
    support_revision_id: int
    used_on: str
    class_label: str
    teaching_session_id: int | None = None
    notes: str = ""


class ExportCreate(BaseModel):
    document_family: Literal["TEACHER", "LEARNER"]
    revision_id: int
    target: Literal["TEACHER", "LEARNER_INITIAL", "LEARNER_COMPLETED"] | None = None


class PositionUpdate(BaseModel):
    direction: Literal["UP", "DOWN"]


class SheetMetadataUpdate(BaseModel):
    identification: dict = Field(default_factory=dict)
    planning: dict = Field(default_factory=dict)


class RenamePayload(BaseModel):
    title: str
