import { useEffect, useState } from 'react'
import { api } from './api'
import type { CompetencyChoice } from './types'

export const competencyFields = ['compétences disciplinaires', 'compétence transdisciplinaire', 'compétences transversales']
const categories = { DISCIPLINARY: 'Compétences disciplinaires', TRANSDISCIPLINARY: 'Compétence(s) transdisciplinaire(s)', TRANSVERSAL: 'Compétences transversales' }

export function Competencies({ value, onChange, disabled }: { value: CompetencyChoice[]; onChange: (rows: CompetencyChoice[]) => void; disabled: boolean }) {
  const [catalog, setCatalog] = useState<CompetencyChoice[]>([])
  const [error, setError] = useState('')
  useEffect(() => { let active = true; api<CompetencyChoice[]>('/api/competencies').then(rows => { if (active) setCatalog(rows) }).catch(e => { if (active) setError(String(e)) }); return () => { active = false } }, [])
  return <div className="competency-panel"><h3>Compétences proposées pour cette séance</h3><p>Les suggestions sont modifiables. Cochez les compétences à conserver sur la fiche. Vos choix seront enregistrés avec « Suivant » ou « Enregistrer ».</p>{error && <p role="alert">{error}</p>}
    {Object.entries(categories).map(([kind, label]) => <fieldset key={kind} disabled={disabled}><legend>{label}</legend>
      {value.filter(row => row.competency_type === kind).map(row => <label className="competency-option" key={row.competency_id}><input type="checkbox" checked onChange={() => onChange(value.filter(v => v.competency_id !== row.competency_id))} /><span>{row.label}<small>{row.selection_origin === 'TEACHER_SELECTED' ? 'Sélection enseignant' : row.selection_origin === 'AUTO_SELECTED' ? 'Suggestion automatique' : 'Sélection conservée'} · {row.authority_class === 'OFFICIAL_GUIDE' ? 'Exemple officiel' : 'Programme'} · p. {row.source_page}<br />{row.reason || row.source_document}</small></span></label>)}
      {!value.some(row => row.competency_type === kind) && <p>Aucune compétence sélectionnée dans cette catégorie.</p>}
      {!disabled && <details><summary>Ajouter une compétence</summary>{catalog.filter(row => row.competency_type === kind && !value.some(v => v.competency_id === row.competency_id)).map(row => <label className="competency-option" key={row.competency_id}><input type="checkbox" checked={false} onChange={() => onChange([...value, { ...row, selection_origin: 'TEACHER_SELECTED' }])} /><span>{row.label}<small>Catalogue du programme · p. {row.source_page} · choix enseignant</small></span></label>)}</details>}
    </fieldset>)}
  </div>
}
