# M02-B - Physical data model

Status: FROZEN FOR MVP IMPLEMENTATION

## Conventions

- Integer surrogate primary keys are technical only; domain codes remain unique and human-readable.
- Timestamps use UTC.
- Enumerations are stored as constrained strings for SQLite/PostgreSQL portability.
- Ordered children have `position` unique within their parent.
- Mutable drafts carry `updated_at`; finalized rows reject mutation through domain services and database guards where portable.

## Curriculum and sources

| Table | Identity and key relationships | Critical constraints |
|---|---|---|
| programme_versions | code, grade, discipline, edition | code unique |
| guide_versions | code, programme_version_id | code unique |
| situations | programme_version_id, code, position | parent+code and parent+position unique |
| sequences | situation_id, code, position | parent+code and parent+position unique |
| knowledge_items | code, title | code unique |
| sequence_knowledge | sequence_id, knowledge_item_id | pair unique |
| guide_instructions | guide_version_id, code, official_text | code unique; official text immutable in use |
| instruction_knowledge | instruction_id, knowledge_item_id | pair unique |
| curriculum_time_allocations | one SA or sequence scope, value, source occurrence | exactly one scope branch |
| source_documents | code, title, author, edition, authority_level | code unique |
| source_occurrences | source_document_id, locator | document+locator unique |
| source_issues | code, type, status, description | code unique |
| source_issue_occurrences | issue_id, occurrence_id | pair unique |
| proposed_contents | source_issue_id, status, content | never overwrites transcription |

## Library

| Table | Identity and key relationships | Critical constraints |
|---|---|---|
| pedagogical_resources | code, title, resource_kind, composition | code unique |
| resource_versions | resource_id, version_number, lifecycle_status, five validation axes | resource+version unique; AVAILABLE immutable |
| pedagogical_blocks | resource_version_id, position, block_type, content_format, source_content | parent+position unique |
| block_variants | block_id, target_set, source_content | no overlapping effective target per block |
| resource_version_occurrences | version_id, occurrence_id | pair unique |
| block_occurrences | block_id, occurrence_id | pair unique |
| resource_instruction_mappings | resource_version_id, instruction_id, rationale, qualification_status | pair unique; created before availability |

## Teacher sheets

| Table | Identity and key relationships | Critical constraints |
|---|---|---|
| teacher_sheets | code, title | one logical session identity |
| teacher_sheet_revisions | sheet_id, revision_number, status, identification fields | sheet+revision unique; FINALIZED immutable |
| session_curriculum_segments | revision_id, position, situation_id, sequence_id, planned_duration | parent+position unique |
| revision_instructions | revision_id, instruction_id | pair unique |
| sheet_resource_instances | revision_id, origin, source_resource_version_id, title, kind | derived XOR original source rule |
| sheet_block_instances | instance_id, position, source_block_id, content, visibility, state | parent+position unique; source optional |
| flow_items | revision_id, position, kind, one target branch | exactly one target for the selected kind |
| activity_phases | instance_id, position, phase_kind, planned_duration | parent+position unique |

`sheet_resource_instances` rule:

```text
origin = LIBRARY_DERIVED  <=> source_resource_version_id IS NOT NULL
origin = LOCAL_ORIGINAL  <=> source_resource_version_id IS NULL
```

## Learner supports

| Table | Identity and key relationships | Critical constraints |
|---|---|---|
| learner_supports | code, title, scope_kind, sequence_id, situation_id | exactly one scope branch |
| learner_support_revisions | support_id, revision_number, status | support+revision unique; FINALIZED immutable |
| support_resource_instances | revision_id, origin, source_resource_version_id, title, kind, position | same origin XOR rule |
| support_block_instances | instance_id, position, source_block_id, content, initial_content, completed_content, state | parent+position unique |
| support_uses | teacher_revision_id, support_revision_id, locator, position | unique use position per teacher revision |

## Execution and exports

| Table | Identity and key relationships | Critical constraints |
|---|---|---|
| teaching_sessions | teacher_sheet_id, teacher_revision_id, conducted_at, actual_duration | one execution per sheet; finalized revision required |
| executed_curriculum_segments | teaching_session_id, position, planned_segment_id, SA/sequence, actual_duration, completion_status | parent+position unique |
| document_exports | document_family, teacher_revision_id, support_revision_id, target, generated_at, status, file_path, error | exactly one source branch; path server-generated |

`document_exports` rule:

```text
(teacher_revision_id IS NOT NULL) XOR (support_revision_id IS NOT NULL)
document_family agrees with the selected branch
```

## Deletion and retirement

- Draft revisions can be deleted with owned local instances/blocks.
- Finalized revisions cannot be deleted in the MVP.
- Library resources/versions are retired, not hard-deleted after use.
- Source documents and occurrences referenced by history cannot be removed.
- Export records remain even if a file becomes unavailable; status/error exposes that fact.

## Indexes

- All domain codes and parent/version pairs.
- Curriculum lookup by programme/SA/sequence.
- Instructions by guide and knowledge item.
- Resource mappings by instruction and lifecycle status.
- Sheet/support revisions by owner and status.
- Session segments by sequence and conducted date.

## Transaction proofs required

- Copy version + all snapshots atomically.
- Finalization validates and changes status atomically.
- New revision copies the previous finalized state without editing it.
- TeachingSession + executed segments commit atomically.
- Export file success/failure and metadata are reconciled deterministically.

## M02-B gate

Every M01 invariant has an enforcement entry in `M01_INVARIANT_ENFORCEMENT_MATRIX.md`. The origin and export XOR constraints, snapshots and immutable finalized histories have both domain and persistence strategies.

