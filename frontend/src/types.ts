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
  summary: string
  estimated_minutes: number
  blocks: Block[]
  mappings: { instruction_id: number; instruction_code: string; text: string; validation_status: string }[]
  sources: { document: string; file_name: string; sha256: string; page: string; locator: string }[]
}

export type SheetSummary = { sheet_id: number; revision_id: number; code: string; title: string; revision_number: number; status: string }
export type SheetDetail = {
  id: number
  sheet_id: number
  code: string
  title: string
  revision_number: number
  status: string
  identification: Record<string, string>
  planning: Record<string, string>
  segments: { id: number; instruction_id: number; instruction_code: string; text: string; planned_minutes: number }[]
  resources: { id: number; origin: string; source_resource_version_id: number | null; title: string; adaptation_note: string; position: number; blocks: Block[] }[]
  flow: { id: number; block_instance_id: number; phase_code: string; teacher_action: string; learner_action: string; strategy: string; expected_result_latex: string; duration_minutes: number; position: number }[]
  support_use: { support_revision_id: number; part_label: string; selected_block_ids: number[] } | null
}

export type SupportSummary = { support_id: number; revision_id: number; code: string; title: string; revision_number: number; status: string }
export type SupportDetail = {
  id: number
  support_id: number
  code: string
  title: string
  revision_number: number
  status: string
  scope: 'SEQUENCE' | 'SA'
  sequence: { id: number; code: string; title: string } | null
  situation: { id: number; code: string; title: string } | null
  resources: { id: number; origin: string; title: string; blocks: Block[] }[]
}
