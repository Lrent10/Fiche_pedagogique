import { describe, expect, it } from 'vitest'
import { provenanceLabel, toggleComparison, totalPlannedMinutes } from './logic'

describe('logique du parcours frontend', () => {
  it('calcule la durée visible du déroulement', () => {
    expect(totalPlannedMinutes([{ duration_minutes: 10 }, { duration_minutes: 15 }])).toBe(25)
  })

  it('ne fabrique jamais une provenance pour une ressource de démonstration', () => {
    expect(provenanceLabel({ provenance_kind: 'DEMO_NON_SOURCE', sources: [] })).toBe('DÉMO — NON SOURCÉ')
  })

  it('limite une comparaison à trois candidats', () => {
    expect(toggleComparison([1, 2, 3], 4)).toEqual([1, 2, 3])
    expect(toggleComparison([1, 2, 3], 2)).toEqual([1, 3])
  })
})
