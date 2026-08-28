import type { Resource } from './types'

export const totalPlannedMinutes = (items: { duration_minutes: number }[]) =>
  items.reduce((total, item) => total + item.duration_minutes, 0)

export const provenanceLabel = (resource: Pick<Resource, 'provenance_kind' | 'sources'>) =>
  resource.provenance_kind === 'SOURCED' && resource.sources.length > 0
    ? `Guide · p. ${resource.sources[0].page}`
    : 'DÉMO — NON SOURCÉ'

export function toggleComparison(selected: number[], id: number, limit = 3): number[] {
  if (selected.includes(id)) return selected.filter(value => value !== id)
  return selected.length < limit ? [...selected, id] : selected
}

