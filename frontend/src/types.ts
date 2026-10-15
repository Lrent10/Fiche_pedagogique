export type Dashboard = {
  draft_sheets: number
  finalized_sheets: number
  resources: number
  supports: number
  open_source_issues: number
}

export type Instruction = { id: number; code: string; text: string; position: number; sequence_id: number }
export type Block = { id: number; block_type: string; title: string; content_latex: string; position: number; visible: boolean }
export type Resource = {
  id: number
  code: string
  title: string
  resource_type: string
  provenance_kind: string
  provenance?: { source_kind: string; source_ref: string; source_version: string; page_label?: string; adaptation?: boolean; validation_status?: string; author?: string }
  summary: string
  estimated_minutes: number
  blocks: Block[]
  mappings: { instruction_id: number; instruction_code: string; text: string; validation_status: string }[]
  sources: { document: string; file_name: string; sha256: string; page: string; locator: string }[]
}

export type SheetSummary = { sheet_id: number; revision_id: number; code: string; title: string; revision_number: number; status: string }
export type SheetDetail = {
  competency_selection?: CompetencyChoice[] | null
  id: number
  sheet_id: number
  planned_session?: { id: number; sequence_plan_id: number; number: number } | null
  code: string
  title: string
  revision_number: number
  status: string
  curriculum_level?: string
  authoring?: { duration_conflict?: boolean; durations?: { hours: number; source_kind: string; source_ref: string; source_version: string; page_label?: string }[]; session_preparation?: SessionPreparation; mode?: string; scope?: { programme_id: number; scope: string; scope_id: number }; provenance?: Record<string, { origin: string; sources: unknown[] }>; selections?: Record<string, { resource_version_id: number }> }
  identification: Record<string, string>
  planning: Record<string, string>
  segments: { id: number; instruction_id: number; instruction_code: string; text: string; planned_minutes: number }[]
  resources: { id: number; origin: string; source_resource_version_id: number | null; title: string; adaptation_note: string; position: number; snapshot?: Record<string, unknown>; blocks: Block[] }[]
  flow: { id: number; block_instance_id: number; phase_code: string; teacher_action: string; learner_action: string; strategy: string; expected_result_latex: string; duration_minutes: number; position: number }[]
  support_use: { support_revision_id: number; part_label: string; selected_block_ids: number[] } | null
  homework?: { homework_usage_type: string; selected_order: number; teacher_note?: string; snapshot: Record<string, unknown> }[]
  documents_used?: { origin: string; display_label: string; author?: string; title?: string; edition?: string; note?: string; selected_order: number }[]
}

export type SessionDurations = { slot_minutes: number; break_minutes: number; default_break_minutes: number; break_override: boolean; pedagogical_minutes?: number }
export type CompetencyChoice = { competency_id: number; context_id: number; label: string; competency_type: string; selection_origin?: string; source_document: string; source_page?: string; authority_class: string; is_primary?: boolean; reason?: string }
export type SessionPreparation = { durations: SessionDurations; planned_sequence_minutes: number | null; deferred_instruction_ids: number[]; reactivate_instruction_ids: number[]; class_context_id: number; class_label: string; school_year: string; session_number: number; teacher_actual_weekly_minutes: number | null }

export type SupportSummary = { support_id: number; revision_id: number; code: string; title: string; revision_number: number; status: string }
export type SupportDetail = {
  id: number
  support_id: number
  code: string
  title: string
  revision_number: number
  status: string
  level?: string
  scope: 'SEQUENCE' | 'SA'
  sequence: { id: number; code: string; title: string } | null
  situation: { id: number; code: string; title: string } | null
  resources: { id: number; origin: string; title: string; blocks: Block[] }[]
}
