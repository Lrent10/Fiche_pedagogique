# M01 invariant enforcement matrix

Status values: `PLANNED`, `IMPLEMENTED`, `TESTED`. The initial M02 design assigns a concrete enforcement strategy to every frozen invariant; implementation phases advance the status.

| ID | Rule summary | Layer | Mechanism | Test | Status |
|---|---|---|---|---|---|
| INV-FP-001 | Sheet never edits official curriculum | DOMAIN/API | Curriculum read-only services from sheet commands | test_sheet_cannot_mutate_curriculum | PLANNED |
| INV-FP-002 | Curriculum data tied to exact versions | DATABASE/DOMAIN | Required programme/guide relationships | test_curriculum_version_required | PLANNED |
| INV-FP-003 | Adaptation never edits source version | DOMAIN/TRANSACTION | Snapshot copy then local edits only | test_adaptation_is_local | PLANNED |
| INV-FP-004 | Future library change is non-retroactive | VERSIONING/TEST | Immutable versions and copied snapshots | test_new_version_preserves_old_sheet | PLANNED |
| INV-FP-005 | Sourced content keeps provenance | DATABASE/VALIDATION | Occurrence associations | test_sourced_version_has_provenance | PLANNED |
| INV-FP-006 | Block-level provenance allowed | DATABASE/API | block_occurrences relation | test_block_provenance | PLANNED |
| INV-FP-007 | Instruction and resource distinct | DOMAIN/DATABASE | Separate identities and mapping relation | test_instruction_resource_distinct | PLANNED |
| INV-FP-008 | Resource/instruction many-to-many | DATABASE/API | Unique mapping pairs | test_many_candidate_resources | PLANNED |
| INV-FP-009 | Local instances independent/adaptable | DOMAIN/TRANSACTION | Sheet/support instance aggregates | test_local_instance_edit | PLANNED |
| INV-FP-010 | Derived exact version, original none | DATABASE/DOMAIN | Origin/source XOR constraint | test_instance_origin_source_xor | PLANNED |
| INV-FP-011 | Render error preserves source | RENDERING/TEST | Save-before-render and error state | test_invalid_latex_preserved | PLANNED |
| INV-FP-012 | Teacher-only results supported | DOMAIN/RENDERING | Visibility targets and export filters | test_teacher_only_hidden_initial | PLANNED |
| INV-FP-013 | Multiple variants by usage | DOMAIN/DATABASE | Block variants with target sets | test_block_variants | PLANNED |
| INV-FP-014 | Explicit ordering | DATABASE/VALIDATION | position fields and parent uniqueness | test_ordering | PLANNED |
| INV-FP-015 | Session duration calculable | DOMAIN/VALIDATION | Sum segments/flow durations | test_session_duration | PLANNED |
| INV-FP-016 | Incomplete draft savable | APPLICATION/API | Draft validation is warning-oriented | test_incomplete_draft_saved | PLANNED |
| INV-FP-017 | Sheet identifies instructions | DATABASE/API | revision_instructions | test_revision_instructions | PLANNED |
| INV-FP-018 | Instruction without resource warned | VALIDATION/API | WARNING_INSTRUCTION_WITHOUT_RESOURCE | test_instruction_warning | PLANNED |
| INV-FP-019 | At most one effective variant/target | DOMAIN/VALIDATION | Target overlap check | test_variant_overlap_rejected | PLANNED |
| INV-FP-020 | Reminder may map to no instruction | DOMAIN/API | Mapping cardinality zero permitted | test_unmapped_prerequisite | PLANNED |
| INV-FP-021 | Mapping qualified before selection | APPLICATION/VALIDATION | AVAILABLE filter requires qualified mapping | test_unqualified_mapping_hidden | PLANNED |
| INV-FP-022 | Official instruction text never replaced | IMMUTABILITY/API | Read-only official_text in sheet flows | test_official_text_immutable | PLANNED |
| INV-FP-023 | Sheet instance conditional source | DATABASE/DOMAIN | Check constraint plus validator | test_sheet_origin_xor | PLANNED |
| INV-FP-024 | Retirement preserves history | VERSIONING/DATABASE | RETIRED state, no cascade delete | test_retired_resource_history | PLANNED |
| INV-FP-025 | Five validation axes separate | DATABASE/API | Five independent columns | test_validation_axes_independent | PLANNED |
| INV-FP-026 | No contradictory duration double count | DOMAIN/VALIDATION | Direct duration XOR phase sum | test_phase_duration_rule | PLANNED |
| INV-FP-027 | One teacher sheet is one session | DOMAIN/DATABASE | Unique session identity/execution | test_one_sheet_one_session | PLANNED |
| INV-FP-028 | Ordered sequence/SA crossing | DOMAIN/VALIDATION | Segment progression validator | test_curriculum_crossing_rules | PLANNED |
| INV-FP-029 | Session segments ordered | DATABASE/VALIDATION | Unique revision+position | test_segment_order | PLANNED |
| INV-FP-030 | Executed segments drive progress | DOMAIN/APPLICATION | Progress query ignores free text | test_progress_from_execution | PLANNED |
| INV-FP-031 | Normative/planned/actual separate | DATABASE/DOMAIN | Separate allocation and duration columns | test_time_dimensions | PLANNED |
| INV-FP-032 | Support spans multiple sessions | DATABASE/API | Many-to-many SupportUse | test_support_four_sessions | PLANNED |
| INV-FP-033 | Support scope sequence XOR SA | DATABASE/DOMAIN | Scope discriminator and XOR | test_support_scope_xor | PLANNED |
| INV-FP-034 | Teacher/support distinct local families | DOMAIN/DATABASE | Separate instance tables | test_instance_families_distinct | PLANNED |
| INV-FP-035 | Faithful transcription may be flawed | DOMAIN/API | Independent status axes | test_verified_incomplete_source | PLANNED |
| INV-FP-036 | Missing/ambiguous recorded explicitly | DATABASE/API | SourceIssue types/status | test_source_issue | PLANNED |
| INV-FP-037 | Document differs from occurrence | DOMAIN/DATABASE | Separate tables, required parent | test_occurrence_parent | PLANNED |
| INV-FP-038 | Proposed repair separate from source | DATABASE/API | proposed_contents relation | test_proposal_not_transcription | PLANNED |
| INV-FP-039 | Historical support use exact | VERSIONING/DATABASE | SupportUse targets exact revision/locator | test_support_use_history | PLANNED |
| INV-FP-040 | Finalized revisions immutable | MULTI_LAYER | Service guard, API rejection, DB event guard | test_finalized_immutable | PLANNED |
| INV-FP-041 | Execution never rewrites preparation | DOMAIN/TRANSACTION | Separate TeachingSession aggregate | test_execution_preserves_plan | PLANNED |
| INV-FP-042 | Ambiguous allocation yields no fake remainder | DOMAIN/API | Nullable derived remainder + ambiguity flag | test_ambiguous_progress | PLANNED |
| INV-FP-043 | Flow item exactly one kind/target | DATABASE/DOMAIN | Kind/target XOR validation | test_flow_item_target | PLANNED |
| INV-FP-044 | Variant/duration conflicts block finalization | VALIDATION/API | Finalization validator | test_finalize_conflicts | PLANNED |
| INV-FP-045 | Export keeps family/revision/target | DATABASE/APPLICATION | Required metadata and exact source | test_export_provenance | PLANNED |
| INV-FP-046 | Instance origin total and exclusive | DATABASE/DOMAIN | Enum plus source XOR | test_origin_total_exclusive | PLANNED |
| INV-FP-047 | Derived instance has source and snapshots | TRANSACTION/VALIDATION | Atomic copier and source requirement | test_derived_snapshot | PLANNED |
| INV-FP-048 | Original has no fake source and blocks | DATABASE/DOMAIN | XOR plus non-empty aggregate | test_local_original | PLANNED |
| INV-FP-049 | Support adaptation local and frozen | MULTI_LAYER | Support snapshots and finalization guard | test_support_snapshot_immutable | PLANNED |
| INV-FP-050 | Export exactly one revision family | DATABASE/DOMAIN | XOR check and validator | test_export_source_xor | PLANNED |

Coverage at M02 design gate: **50/50 have an enforcement strategy; 50/50 have a named automated test when testable.**

