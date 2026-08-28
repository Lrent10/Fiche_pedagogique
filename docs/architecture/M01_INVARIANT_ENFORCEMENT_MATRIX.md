# M01 invariant enforcement matrix

Status values: `IMPLEMENTED`, `TESTED`, `PARTIAL`. `PARTIAL` means the core model exists but the full multi-scope or administration workflow is deliberately outside the pilot slice.

| ID | Rule summary | Layer | Mechanism | Test | Status |
|---|---|---|---|---|---|
| INV-FP-001 | Sheet never edits official curriculum | DOMAIN/API | Curriculum read-only services from sheet commands | test_sheet_cannot_mutate_curriculum | IMPLEMENTED |
| INV-FP-002 | Curriculum data tied to exact versions | DATABASE/DOMAIN | Required programme/guide relationships | test_curriculum_version_required | IMPLEMENTED |
| INV-FP-003 | Adaptation never edits source version | DOMAIN/TRANSACTION | Snapshot copy then local edits only | test_adaptation_is_local | TESTED |
| INV-FP-004 | Future library change is non-retroactive | VERSIONING/TEST | Immutable versions and copied snapshots | test_new_version_preserves_old_sheet | TESTED |
| INV-FP-005 | Sourced content keeps provenance | DATABASE/VALIDATION | Occurrence associations | test_sourced_version_has_provenance | TESTED |
| INV-FP-006 | Block-level provenance allowed | DATABASE/API | generic typed `SourceOccurrence` | test_block_provenance | PARTIAL |
| INV-FP-007 | Instruction and resource distinct | DOMAIN/DATABASE | Separate identities and mapping relation | test_instruction_resource_distinct | IMPLEMENTED |
| INV-FP-008 | Resource/instruction many-to-many | DATABASE/API | Unique mapping pairs | test_many_candidate_resources | TESTED |
| INV-FP-009 | Local instances independent/adaptable | DOMAIN/TRANSACTION | Sheet/support instance aggregates | test_local_instance_edit | TESTED |
| INV-FP-010 | Derived exact version, original none | DATABASE/DOMAIN | Origin/source XOR constraint | test_instance_origin_source_xor | TESTED |
| INV-FP-011 | Render error preserves source | RENDERING/TEST | Save-before-render and error state | test_invalid_latex_preserved | TESTED |
| INV-FP-012 | Teacher-only results supported | DOMAIN/RENDERING | Visibility targets and export filters | test_teacher_only_hidden_initial | TESTED |
| INV-FP-013 | Multiple variants by usage | DOMAIN/DATABASE | Block variants with target sets | test_block_variants | TESTED |
| INV-FP-014 | Explicit ordering | DATABASE/VALIDATION | position fields and parent uniqueness | test_ordering | TESTED |
| INV-FP-015 | Session duration calculable | DOMAIN/VALIDATION | Sum segments/flow durations | test_session_duration | TESTED |
| INV-FP-016 | Incomplete draft savable | APPLICATION/API | Draft validation is warning-oriented | test_incomplete_draft_saved | TESTED |
| INV-FP-017 | Sheet identifies instructions | DATABASE/API | revision-instruction segments | test_revision_instructions | TESTED |
| INV-FP-018 | Instruction without resource warned | VALIDATION/API | WARNING_INSTRUCTION_WITHOUT_RESOURCE | test_instruction_warning | TESTED |
| INV-FP-019 | At most one effective variant/target | DOMAIN/VALIDATION | Unique block+target constraint | test_variant_overlap_rejected | TESTED |
| INV-FP-020 | Reminder may map to no instruction | DOMAIN/API | Mapping cardinality zero permitted | test_unmapped_prerequisite | PARTIAL |
| INV-FP-021 | Mapping qualified before selection | APPLICATION/VALIDATION | AVAILABLE filter and qualified mappings | test_unqualified_mapping_hidden | TESTED |
| INV-FP-022 | Official instruction text never replaced | IMMUTABILITY/API | Read-only official text in sheet detail | test_official_text_immutable | IMPLEMENTED |
| INV-FP-023 | Sheet instance conditional source | DATABASE/DOMAIN | Check constraint plus validator | test_sheet_origin_xor | TESTED |
| INV-FP-024 | Retirement preserves history | VERSIONING/DATABASE | RETIRED state, no cascade delete | test_retired_resource_history | TESTED |
| INV-FP-025 | Five validation axes separate | DATABASE/API | Five independent columns | test_validation_axes_independent | IMPLEMENTED |
| INV-FP-026 | No contradictory duration double count | DOMAIN/VALIDATION | Direct duration / phase model | test_phase_duration_rule | PARTIAL |
| INV-FP-027 | One teacher sheet is one session | DOMAIN/DATABASE | Stable sheet/revision identity | test_one_sheet_one_session | TESTED |
| INV-FP-028 | Ordered sequence/SA crossing | DOMAIN/VALIDATION | Ordered segment persistence; pilot is one sequence | test_curriculum_crossing_rules | PARTIAL |
| INV-FP-029 | Session segments ordered | DATABASE/VALIDATION | Unique revision+position | test_segment_order | IMPLEMENTED |
| INV-FP-030 | Executed segments drive progress | DOMAIN/APPLICATION | Progress query ignores free text | test_progress_from_execution | TESTED |
| INV-FP-031 | Normative/planned/actual separate | DATABASE/DOMAIN | Separate allocation and duration columns | test_time_dimensions | TESTED |
| INV-FP-032 | Support spans multiple sessions | DATABASE/API | Repeated SupportUse records | test_support_four_sessions | PARTIAL |
| INV-FP-033 | Support scope sequence XOR SA | DATABASE/DOMAIN | Two FKs and XOR constraint | test_support_scope_xor | TESTED |
| INV-FP-034 | Teacher/support distinct local families | DOMAIN/DATABASE | Separate instance tables | test_instance_families_distinct | TESTED |
| INV-FP-035 | Faithful transcription may be flawed | DOMAIN/API | Independent status axes | test_verified_incomplete_source | IMPLEMENTED |
| INV-FP-036 | Missing/ambiguous recorded explicitly | DATABASE/API | SourceIssue types/status | test_source_issue | TESTED |
| INV-FP-037 | Document differs from occurrence | DOMAIN/DATABASE | Separate tables, required parent | test_occurrence_parent | TESTED |
| INV-FP-038 | Proposed repair separate from source | DATABASE/API | proposed_contents table | test_proposal_not_transcription | PARTIAL |
| INV-FP-039 | Historical support use exact | VERSIONING/DATABASE | SupportUse targets exact revision/part | test_support_use_history | IMPLEMENTED |
| INV-FP-040 | Finalized revisions immutable | MULTI_LAYER | Service guard, API rejection, transaction guard | test_finalized_immutable | TESTED |
| INV-FP-041 | Execution never rewrites preparation | DOMAIN/TRANSACTION | Separate TeachingSession aggregate | test_execution_preserves_plan | TESTED |
| INV-FP-042 | Ambiguous allocation yields no fake remainder | DOMAIN/API | Nullable remainder + ambiguity flag | test_ambiguous_progress | TESTED |
| INV-FP-043 | Flow item exactly one kind/target | DATABASE/DOMAIN | Kind/target XOR validation | test_flow_item_target | IMPLEMENTED |
| INV-FP-044 | Variant/duration conflicts block finalization | VALIDATION/API | Unique variants plus duration warnings | test_finalize_conflicts | PARTIAL |
| INV-FP-045 | Export keeps family/revision/target | DATABASE/APPLICATION | Required metadata and exact source | test_export_provenance | TESTED |
| INV-FP-046 | Instance origin total and exclusive | DATABASE/DOMAIN | Enum plus source XOR | test_origin_total_exclusive | TESTED |
| INV-FP-047 | Derived instance has source and snapshots | TRANSACTION/VALIDATION | Atomic copier and source requirement | test_derived_snapshot | TESTED |
| INV-FP-048 | Original has no fake source and blocks | DATABASE/DOMAIN | XOR plus atomic service creation | test_local_original | TESTED |
| INV-FP-049 | Support adaptation local and frozen | MULTI_LAYER | Support snapshots and finalization guard | test_support_snapshot_immutable | TESTED |
| INV-FP-050 | Export exactly one revision family | DATABASE/DOMAIN | XOR check and validator | test_export_source_xor | TESTED |

Final MVP audit: **50/50 mapped; 34 TESTED; 9 IMPLEMENTED; 7 PARTIAL and disclosed as non-blocking pilot limitations.**
