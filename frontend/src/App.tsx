import { FormEvent, useCallback, useEffect, useMemo, useState } from 'react'
import { api, post, put } from './api'
import { LatexPreview } from './LatexPreview'
import type { Dashboard, Instruction, Resource, SheetDetail, SheetSummary, SupportDetail, SupportSummary } from './types'

type View = 'dashboard' | 'sheets' | 'library' | 'supports' | 'progress' | 'sources'
const steps = ['Identification', 'Programme', 'Choix des activités', 'Adaptation', 'Déroulement', 'Planification', 'Aperçu', 'Finalisation']

const navItems: { id: View; label: string; icon: string }[] = [
  { id: 'dashboard', label: 'Tableau de bord', icon: '⌂' },
  { id: 'sheets', label: 'Mes fiches', icon: '▤' },
  { id: 'library', label: 'Bibliothèque', icon: '▦' },
  { id: 'supports', label: 'Supports apprenants', icon: '◫' },
  { id: 'progress', label: 'Progression', icon: '↗' },
  { id: 'sources', label: 'Sources', icon: '◎' },
]

export default function App() {
  const [view, setView] = useState<View>('dashboard')
  const [dashboard, setDashboard] = useState<Dashboard | null>(null)
  const [instructions, setInstructions] = useState<Instruction[]>([])
  const [resources, setResources] = useState<Resource[]>([])
  const [sheets, setSheets] = useState<SheetSummary[]>([])
  const [supports, setSupports] = useState<SupportSummary[]>([])
  const [activeSheet, setActiveSheet] = useState<SheetDetail | null>(null)
  const [activeSupport, setActiveSupport] = useState<SupportDetail | null>(null)
  const [notice, setNotice] = useState<string>('')
  const [error, setError] = useState<string>('')
  const [loading, setLoading] = useState(true)

  const refresh = useCallback(async () => {
    try {
      const [dash, ins, res, sheetRows, supportRows] = await Promise.all([
        api<Dashboard>('/api/dashboard'), api<Instruction[]>('/api/instructions'), api<Resource[]>('/api/resources'),
        api<SheetSummary[]>('/api/sheets'), api<SupportSummary[]>('/api/supports'),
      ])
      setDashboard(dash); setInstructions(ins); setResources(res); setSheets(sheetRows); setSupports(supportRows)
      setError('')
    } catch (err) { setError(err instanceof Error ? err.message : 'Connexion impossible.') }
    finally { setLoading(false) }
  }, [])

  useEffect(() => { void refresh() }, [refresh])

  async function openSheet(id: number) {
    try { setActiveSheet(await api<SheetDetail>(`/api/sheets/${id}`)); setView('sheets') }
    catch (err) { setError((err as Error).message) }
  }
  async function openSupport(id: number) {
    try { setActiveSupport(await api<SupportDetail>(`/api/supports/${id}`)); setView('supports') }
    catch (err) { setError((err as Error).message) }
  }
  function showNotice(message: string) { setNotice(message); window.setTimeout(() => setNotice(''), 3500) }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand"><span className="brand-mark">∑</span><div><strong>FicheMaths</strong><small>Bénin · 4e</small></div></div>
        <nav aria-label="Navigation principale">
          {navItems.map(item => <button key={item.id} className={view === item.id ? 'active' : ''} onClick={() => { setView(item.id); if (item.id !== 'sheets') setActiveSheet(null); if (item.id !== 'supports') setActiveSupport(null) }}><span>{item.icon}</span>{item.label}</button>)}
        </nav>
        <div className="sidebar-foot"><span className="status-dot" /> Application locale<br /><small>MVP · données 4e</small></div>
      </aside>
      <main>
        <header className="topbar">
          <div><p className="eyebrow">Générateur pédagogique</p><h1>{navItems.find(item => item.id === view)?.label}</h1></div>
          <div className="top-actions"><span className="level-pill">Classe de 4e</span><button className="primary small" onClick={() => { setView('sheets'); setActiveSheet(null) }}>＋ Nouvelle fiche</button></div>
        </header>
        {notice && <div className="toast success">✓ {notice}</div>}
        {error && <div className="toast error">{error}<button onClick={() => setError('')}>×</button></div>}
        {loading ? <div className="empty">Chargement de l’espace de travail…</div> : (
          <div className="page">
            {view === 'dashboard' && dashboard && <DashboardPage data={dashboard} sheets={sheets} onView={setView} onOpen={openSheet} />}
            {view === 'sheets' && (activeSheet ? <SheetEditor sheet={activeSheet} setSheet={setActiveSheet} instructions={instructions} resources={resources} notify={showNotice} refresh={refresh} close={() => setActiveSheet(null)} /> : <SheetsPage sheets={sheets} instructions={instructions} onOpen={openSheet} onCreated={(sheet) => { setActiveSheet(sheet); void refresh() }} />)}
            {view === 'library' && <LibraryPage resources={resources} instructions={instructions} activeSheet={activeSheet} onSheetChange={setActiveSheet} notify={showNotice} />}
            {view === 'supports' && (activeSupport ? <SupportEditor support={activeSupport} setSupport={setActiveSupport} resources={resources} notify={showNotice} refresh={refresh} close={() => setActiveSupport(null)} onSheetCreated={(sheet) => { setActiveSheet(sheet); setActiveSupport(null); setView('sheets'); void refresh() }} /> : <SupportsPage supports={supports} onOpen={openSupport} onCreated={(support) => { setActiveSupport(support); void refresh() }} />)}
            {view === 'progress' && <ProgressPage />}
            {view === 'sources' && <SourcesPage resources={resources} />}
          </div>
        )}
      </main>
    </div>
  )
}

function DashboardPage({ data, sheets, onView, onOpen }: { data: Dashboard; sheets: SheetSummary[]; onView: (v: View) => void; onOpen: (id: number) => void }) {
  const recent = [...sheets].slice(0, 4)
  return <>
    <section className="hero"><div><span className="badge gold">Espace enseignant</span><h2>Préparez votre prochain cours,<br />sans perdre le fil du guide.</h2><p>Choisissez une instruction, comparez les activités disponibles, adaptez-les en LaTeX puis générez vos deux fiches.</p><button className="primary" onClick={() => onView('sheets')}>Créer une fiche pédagogique →</button></div><div className="formula-card"><span>(a + b)²</span><strong>= a² + 2ab + b²</strong><i>Activité · Propriété · Application</i></div></section>
    <div className="stats">
      <Stat value={data.draft_sheets} label="Fiches en brouillon" tone="blue" />
      <Stat value={data.finalized_sheets} label="Fiches finalisées" tone="green" />
      <Stat value={data.resources} label="Activités disponibles" tone="orange" />
      <Stat value={data.supports} label="Supports apprenants" tone="purple" />
    </div>
    <section className="panel"><div className="panel-head"><div><h3>Travail récent</h3><p>Reprenez une préparation là où vous l’avez laissée.</p></div><button className="link" onClick={() => onView('sheets')}>Voir toutes les fiches →</button></div>
      <div className="table-list">{recent.map(sheet => <button className="table-row" key={sheet.revision_id} onClick={() => onOpen(sheet.revision_id)}><span className="doc-icon">▤</span><span><strong>{sheet.title}</strong><small>{sheet.code} · Révision {sheet.revision_number}</small></span><Status value={sheet.status} /><b>›</b></button>)}</div>
    </section>
    {data.open_source_issues > 0 && <div className="source-alert"><strong>◉ {data.open_source_issues} écarts de source conservés</strong><span>Ils sont documentés et ne sont pas arbitrés automatiquement.</span><button onClick={() => onView('sources')}>Consulter</button></div>}
  </>
}

function Stat({ value, label, tone }: { value: number; label: string; tone: string }) { return <div className={`stat ${tone}`}><strong>{value}</strong><span>{label}</span></div> }
function Status({ value }: { value: string }) { return <span className={`status ${value.toLowerCase()}`}>{value === 'DRAFT' ? 'Brouillon' : 'Finalisée'}</span> }

function SheetsPage({ sheets, instructions, onOpen, onCreated }: { sheets: SheetSummary[]; instructions: Instruction[]; onOpen: (id: number) => void; onCreated: (s: SheetDetail) => void }) {
  const [creating, setCreating] = useState(false)
  const [title, setTitle] = useState('Produits remarquables — séance')
  const [selected, setSelected] = useState<number[]>(instructions.slice(2, 4).map(i => i.id))
  async function submit(event: FormEvent) { event.preventDefault(); const sheet = await post<SheetDetail>('/api/sheets', { title, instruction_ids: selected, duration_minutes: 55, class_label: '4e' }); onCreated(sheet) }
  return <section className="panel">
    <div className="panel-head"><div><h2>Mes fiches enseignant</h2><p>Chaque finalisation fige une révision ; l’adaptation suivante crée une nouvelle version.</p></div><button className="primary" onClick={() => setCreating(!creating)}>＋ Créer une fiche</button></div>
    {creating && <form className="create-form" onSubmit={submit}><label>Titre de la séance<input value={title} onChange={e => setTitle(e.target.value)} required /></label><fieldset><legend>Instructions du guide à mettre en œuvre</legend>{instructions.map(i => <label className="check" key={i.id}><input type="checkbox" checked={selected.includes(i.id)} onChange={() => setSelected(old => old.includes(i.id) ? old.filter(id => id !== i.id) : [...old, i.id])} /><span><b>{i.code}</b> {i.text}</span></label>)}</fieldset><button className="primary" disabled={!selected.length}>Commencer la conception →</button></form>}
    <div className="cards-grid">{sheets.map(sheet => <button className="sheet-card" key={sheet.revision_id} onClick={() => onOpen(sheet.revision_id)}><div><span className="doc-icon large">▤</span><Status value={sheet.status} /></div><h3>{sheet.title}</h3><p>{sheet.code} · Révision {sheet.revision_number}</p><span className="link">Ouvrir la fiche →</span></button>)}</div>
  </section>
}

function SheetEditor({ sheet, setSheet, resources, notify, refresh, close }: { sheet: SheetDetail; setSheet: (s: SheetDetail) => void; instructions: Instruction[]; resources: Resource[]; notify: (m: string) => void; refresh: () => Promise<void>; close: () => void }) {
  const [step, setStep] = useState(0)
  const [localTitle, setLocalTitle] = useState('Ma consigne')
  const [localLatex, setLocalLatex] = useState('Développe et réduis $(2x+1)^2$.')
  const [identification, setIdentification] = useState(sheet.identification)
  const [planning, setPlanning] = useState(sheet.planning)
  const [compareIds, setCompareIds] = useState<number[]>([])
  const draft = sheet.status === 'DRAFT'
  async function addResource(id: number) { const updated = await post<SheetDetail>(`/api/sheets/${sheet.id}/resources/library`, { resource_version_id: id }); setSheet(updated); notify('Activité ajoutée à la fiche.') }
  async function addLocal() { const updated = await post<SheetDetail>(`/api/sheets/${sheet.id}/resources/local`, { title: localTitle, block_type: 'INSTRUCTION', content_latex: localLatex }); setSheet(updated); notify('Contenu local ajouté.') }
  async function saveMetadata() { const updated = await put<SheetDetail>(`/api/sheets/${sheet.id}/metadata`, { identification, planning }); setSheet(updated); notify('Informations enregistrées.') }
  async function updateBlock(id: number, content_latex: string) { const updated = await put<SheetDetail>(`/api/sheets/${sheet.id}/blocks/${id}`, { content_latex }); setSheet(updated); notify('Adaptation enregistrée.') }
  async function updateFlow(id: number, payload: Record<string, string | number>) { const updated = await put<SheetDetail>(`/api/sheets/${sheet.id}/flow/${id}`, payload); setSheet(updated); notify('Déroulement enregistré.') }
  async function move(blockId: number, delta: number) { const ids = [...sheet.flow].sort((a, b) => a.position - b.position).map(f => f.block_instance_id); const index = ids.indexOf(blockId); const next = index + delta; if (next < 0 || next >= ids.length) return; [ids[index], ids[next]] = [ids[next], ids[index]]; setSheet(await put<SheetDetail>(`/api/sheets/${sheet.id}/flow`, { ordered_block_ids: ids })) }
  async function finalize() { if (!confirm('Finaliser cette révision ? Elle deviendra non modifiable.')) return; setSheet(await post<SheetDetail>(`/api/sheets/${sheet.id}/finalize`)); notify('Révision finalisée.'); await refresh() }
  async function revise() { setSheet(await post<SheetDetail>(`/api/sheets/${sheet.id}/new-revision`)); setStep(0); notify('Nouvelle révision créée.'); await refresh() }
  async function duplicate() { setSheet(await post<SheetDetail>(`/api/sheets/${sheet.id}/duplicate`)); notify('Fiche dupliquée dans un nouveau brouillon.'); await refresh() }
  async function rename() { const title = prompt('Nouveau titre de la fiche', sheet.title); if (!title) return; setSheet(await put<SheetDetail>(`/api/sheets/${sheet.sheet_id}/rename`, { title })); notify('Fiche renommée.'); await refresh() }
  async function remove() { if (!confirm('Supprimer définitivement ce brouillon ?')) return; await api(`/api/sheets/${sheet.sheet_id}`, { method: 'DELETE' }); await refresh(); close() }
  async function exportPdf() { const result = await post<{ download_url: string }>('/api/exports', { document_family: 'TEACHER', revision_id: sheet.id }); window.open(result.download_url, '_blank'); notify('PDF enseignant généré.') }
  async function recordExecution() { const actual = Number(prompt('Durée réellement effectuée (minutes)', '55')); if (!actual) return; await post('/api/teaching-sessions', { teacher_revision_id: sheet.id, taught_on: new Date().toISOString().slice(0, 10), class_label: sheet.identification.classe || '4e', actual_minutes: actual, status: 'DONE', notes: '' }); notify('Séance exécutée et progression mise à jour.') }
  const blocks = sheet.resources.flatMap(r => r.blocks)
  return <>
    <button className="back" onClick={close}>← Retour à mes fiches</button>
    <div className="editor-head"><div><div className="meta-line"><Status value={sheet.status} /><span>{sheet.code} · Révision {sheet.revision_number}</span></div><h2>{sheet.title}</h2></div><div className="head-buttons"><button className="outline" onClick={duplicate}>Dupliquer</button>{draft && <button className="outline" onClick={rename}>Renommer</button>}{draft && <button className="danger" onClick={remove}>Supprimer</button>}{draft ? <button className="outline" onClick={saveMetadata}>Enregistrer</button> : <button className="primary" onClick={revise}>Nouvelle révision</button>}</div></div>
    <div className="stepper" aria-label="Étapes de conception">{steps.map((label, index) => <button key={label} className={`${index === step ? 'current' : ''} ${index < step ? 'done' : ''}`} onClick={() => setStep(index)}><span>{index < step ? '✓' : index + 1}</span><small>{label}</small></button>)}</div>
    <section className="editor-panel">
      {step === 0 && <div><SectionTitle number="01" title="Éléments d’identification" subtitle="Renseignez les informations propres à votre séance." /> <div className="form-grid">{Object.entries(identification).map(([key, value]) => <label key={key}>{key.replaceAll('_', ' ')}<input disabled={!draft} value={value} onChange={e => setIdentification({ ...identification, [key]: e.target.value })} /></label>)}</div></div>}
      {step === 1 && <div><SectionTitle number="02" title="Ancrage au programme et au guide" subtitle="Ces instructions définissent le périmètre de la séance." />{sheet.segments.map(s => <article className="instruction-row" key={s.id}><span>{s.instruction_code}</span><LatexPreview content={s.text} compact /><b>{s.planned_minutes} min</b></article>)}</div>}
      {step === 2 && <div><SectionTitle number="03" title="Choisir les activités et consignes" subtitle="Comparez les propositions sourcées et la démonstration clairement étiquetée." /><div className="resource-carousel">{resources.filter(r => r.mappings.some(m => sheet.segments.some(s => s.instruction_id === m.instruction_id))).map(resource => <div className="compare-wrap" key={resource.id}><ResourceCard resource={resource} action={draft ? () => addResource(resource.id) : undefined} /><button className={compareIds.includes(resource.id) ? 'compare selected' : 'compare'} onClick={() => setCompareIds(old => old.includes(resource.id) ? old.filter(id => id !== resource.id) : old.length < 3 ? [...old, resource.id] : old)}>□ {compareIds.includes(resource.id) ? 'Sélectionnée' : 'Comparer'}</button></div>)}</div>{compareIds.length >= 2 && <Comparison resources={resources.filter(r => compareIds.includes(r.id))} />}</div>}
      {step === 3 && <div><SectionTitle number="04" title="Adapter les contenus en LaTeX" subtitle="Les copies de la bibliothèque sont modifiables sans altérer leur source." />{blocks.map(block => <LatexEditor key={block.id} block={block} disabled={!draft} onSave={value => updateBlock(block.id, value)} />)}{draft && <div className="local-box"><h3>Ajouter un contenu original local</h3><input value={localTitle} onChange={e => setLocalTitle(e.target.value)} /><textarea value={localLatex} onChange={e => setLocalLatex(e.target.value)} /><LatexPreview content={localLatex} /><button className="outline" onClick={addLocal}>＋ Ajouter à la fiche</button></div>}</div>}
      {step === 4 && <div><SectionTitle number="05" title="Organiser le déroulement" subtitle="Réordonnez les blocs, précisez les stratégies et saisissez manuellement les résultats attendus." />{sheet.flow.map((flow, index) => { const block = blocks.find(b => b.id === flow.block_instance_id); const needsResult = ['INSTRUCTION', 'CONSIGNE', 'APPLICATION', 'EXERCISE'].includes(block?.block_type || ''); return <article className="flow-editor" key={flow.id}><div className="flow-row"><span className="drag">⋮⋮</span><span className="flow-index">{index + 1}</span><div><b>{block?.title || 'Bloc'}</b><LatexPreview content={block?.content_latex || ''} compact /></div><span>{flow.duration_minutes} min</span>{draft && <div className="move"><button onClick={() => move(flow.block_instance_id, -1)}>↑</button><button onClick={() => move(flow.block_instance_id, 1)}>↓</button></div>}</div><div className="flow-metadata"><label>Stratégie<input disabled={!draft} defaultValue={flow.strategy} onBlur={e => updateFlow(flow.id, { strategy: e.target.value })} /></label><label>Durée (min)<input type="number" min="0" disabled={!draft} defaultValue={flow.duration_minutes} onBlur={e => updateFlow(flow.id, { duration_minutes: Number(e.target.value) })} /></label></div>{needsResult && <ExpectedResultEditor value={flow.expected_result_latex} disabled={!draft} onSave={value => updateFlow(flow.id, { expected_result_latex: value })} />}</article> })}</div>}
      {step === 5 && <div><SectionTitle number="06" title="Éléments de planification" subtitle="Vérifiez la cohérence avant l’aperçu." /><div className="form-grid">{Object.entries(planning).map(([key, value]) => <label key={key}>{key.replaceAll('_', ' ')}<input disabled={!draft} value={value} onChange={e => setPlanning({ ...planning, [key]: e.target.value })} /></label>)}</div><div className="summary-strip"><span><b>{sheet.segments.length}</b> instructions</span><span><b>{sheet.resources.length}</b> activités</span><span><b>{sheet.flow.reduce((n, f) => n + f.duration_minutes, 0)}</b> minutes planifiées</span></div></div>}
      {step === 6 && <TeacherPreview sheet={sheet} />}
      {step === 7 && <div className="final-box"><span className="final-icon">✓</span><h2>{draft ? 'Votre fiche est prête à être finalisée' : 'Cette révision est finalisée'}</h2><p>{draft ? 'La finalisation fige cette révision. Vous pourrez ensuite créer une nouvelle révision pour continuer à l’adapter.' : 'Elle ne peut plus être modifiée. Son PDF reste reproductible depuis ce contenu figé.'}</p><Warnings revisionId={sheet.id} /><div className="final-buttons">{draft && <button className="primary" onClick={finalize}>Finaliser la révision</button>}<button className="outline" onClick={exportPdf}>Générer le PDF enseignant</button>{!draft && <button className="outline" onClick={recordExecution}>Marquer comme effectuée</button>}</div></div>}
      <div className="editor-nav"><button className="outline" disabled={step === 0} onClick={() => setStep(step - 1)}>← Précédent</button><span>Étape {step + 1} sur {steps.length}</span><button className="primary" disabled={step === steps.length - 1} onClick={() => setStep(step + 1)}>Suivant →</button></div>
    </section>
  </>
}

function SectionTitle({ number, title, subtitle }: { number: string; title: string; subtitle: string }) { return <div className="section-title"><span>{number}</span><div><h3>{title}</h3><p>{subtitle}</p></div></div> }
function Warnings({ revisionId }: { revisionId: number }) { const [rows, setRows] = useState<{code:string;message:string}[]>([]); useEffect(() => { api<typeof rows>(`/api/sheets/${revisionId}/warnings`).then(setRows) }, [revisionId]); if (!rows.length) return <div className="validation-ok">✓ Aucun avertissement détecté.</div>; return <div className="warnings"><b>{rows.length} avertissement(s) à relire</b>{rows.map(row => <span key={row.code + row.message}><strong>{row.code}</strong>{row.message}</span>)}</div> }
function LatexEditor({ block, disabled, onSave }: { block: { title: string; content_latex: string }; disabled: boolean; onSave: (value: string) => void }) { const [value, setValue] = useState(block.content_latex); useEffect(() => setValue(block.content_latex), [block.content_latex]); return <article className="latex-editor"><div className="editor-label"><b>{block.title}</b><span>LaTeX</span></div><div className="split"><textarea disabled={disabled} value={value} onChange={e => setValue(e.target.value)} /><LatexPreview content={value} /></div>{!disabled && <button className="link" onClick={() => onSave(value)}>Enregistrer ce bloc</button>}</article> }
function ExpectedResultEditor({ value: initial, disabled, onSave }: { value: string; disabled: boolean; onSave: (value: string) => void }) { const [value, setValue] = useState(initial); useEffect(() => setValue(initial), [initial]); return <div className="expected-result"><div className="editor-label"><b>RÉSULTATS ATTENDUS</b><span>Saisie manuelle · LaTeX</span></div><div className="split"><textarea disabled={disabled} value={value} placeholder="Saisir ici le résultat attendu par le professeur…" onChange={e => setValue(e.target.value)} /><LatexPreview content={value || '\\textit{Aucun résultat attendu saisi.}'} /></div>{!disabled && <button className="outline" onClick={() => onSave(value)}>Enregistrer le résultat attendu</button>}</div> }

function ResourceCard({ resource, action }: { resource: Resource; action?: () => void }) { const sourced = resource.provenance_kind === 'SOURCED'; return <article className={`resource-card ${sourced ? '' : 'demo'}`}><div className="resource-top"><span className={`badge ${sourced ? 'source' : 'demo'}`}>{sourced ? 'Source vérifiée' : 'DÉMO · NON SOURCÉ'}</span><span>{resource.estimated_minutes} min</span></div><h3>{resource.title}</h3><p>{resource.summary}</p><LatexPreview content={resource.blocks[0]?.content_latex || ''} compact /><div className="resource-meta"><span>{resource.resource_type.replaceAll('_', ' ')}</span>{resource.sources[0] && <span>Guide · p. {resource.sources[0].page}</span>}</div>{action && <button className="primary full" onClick={action}>Utiliser cette activité</button>}</article> }
function Comparison({ resources }: { resources: Resource[] }) { return <div className="comparison"><h3>Comparaison des activités</h3><div className="comparison-grid"><b>Critère</b>{resources.map(r => <b key={r.id}>{r.title}</b>)}<span>Provenance</span>{resources.map(r => <span key={r.id}>{r.sources.length ? `Guide p. ${r.sources[0].page}` : 'DÉMO — non sourcé'}</span>)}<span>Durée</span>{resources.map(r => <span key={r.id}>{r.estimated_minutes} min</span>)}<span>Blocs</span>{resources.map(r => <span key={r.id}>{r.blocks.length} blocs</span>)}<span>Validation</span>{resources.map(r => <span key={r.id}>{r.mappings.map(m => m.validation_status).join(', ')}</span>)}</div></div> }

function LibraryPage({ resources, instructions, activeSheet, onSheetChange, notify }: { resources: Resource[]; instructions: Instruction[]; activeSheet: SheetDetail | null; onSheetChange: (s: SheetDetail) => void; notify: (m: string) => void }) { const [filter, setFilter] = useState<number | 'all'>('all'); const visible = filter === 'all' ? resources : resources.filter(r => r.mappings.some(m => m.instruction_id === filter)); async function add(id: number) { if (!activeSheet) return; onSheetChange(await post<SheetDetail>(`/api/sheets/${activeSheet.id}/resources/library`, { resource_version_id: id })); notify('Ressource ajoutée à la fiche ouverte.') } return <><section className="panel"><div className="panel-head"><div><h2>Bibliothèque d’activités</h2><p>Les références sont visibles ; les démonstrations ne sont jamais présentées comme officielles.</p></div><select value={filter} onChange={e => setFilter(e.target.value === 'all' ? 'all' : Number(e.target.value))}><option value="all">Toutes les instructions</option>{instructions.map(i => <option value={i.id} key={i.id}>{i.code} — {i.text.slice(0, 55)}</option>)}</select></div>{!activeSheet && <div className="info">Ouvrez d’abord une fiche brouillon pour pouvoir y ajouter une ressource.</div>}<div className="resource-grid">{visible.map(resource => <ResourceCard key={resource.id} resource={resource} action={activeSheet?.status === 'DRAFT' ? () => add(resource.id) : undefined} />)}</div></section></> }

function TeacherPreview({ sheet }: { sheet: SheetDetail }) { return <div className="paper-preview"><div className="paper-title"><b>FICHE PÉDAGOGIQUE DE L’ENSEIGNANT</b><span>Mathématiques · 4e</span></div><h4>I. ÉLÉMENTS D’IDENTIFICATION</h4><div className="preview-grid">{Object.entries(sheet.identification).map(([k, v]) => <span key={k}><b>{k}</b>{v}</span>)}</div><h4>II. ÉLÉMENTS DE PLANIFICATION</h4><div className="preview-grid">{Object.entries(sheet.planning).map(([k, v]) => <span key={k}><b>{k}</b>{v}</span>)}</div><h4>III. DÉROULEMENT</h4>{sheet.resources.flatMap(r => r.blocks).map(block => <div className="preview-block" key={block.id}><b>{block.title}</b><LatexPreview content={block.content_latex} /></div>)}</div> }

function SupportsPage({ supports, onOpen, onCreated }: { supports: SupportSummary[]; onOpen: (id: number) => void; onCreated: (s: SupportDetail) => void }) { const [title, setTitle] = useState('Support apprenant — produits remarquables'); async function create() { onCreated(await post<SupportDetail>('/api/supports', { title })) } return <section className="panel"><div className="panel-head"><div><h2>Fiches de l’apprenant</h2><p>Un support allégé : activités, consignes, propriétés et zones de réponse.</p></div></div><div className="inline-create"><input value={title} onChange={e => setTitle(e.target.value)} /><button className="primary" onClick={create}>＋ Nouveau support</button></div><div className="cards-grid">{supports.map(s => <button className="sheet-card" key={s.revision_id} onClick={() => onOpen(s.revision_id)}><div><span className="doc-icon large">◫</span><Status value={s.status} /></div><h3>{s.title}</h3><p>{s.code} · Révision {s.revision_number}</p><span className="link">Ouvrir le support →</span></button>)}</div></section> }

function SupportEditor({ support, setSupport, resources, notify, refresh, close, onSheetCreated }: { support: SupportDetail; setSupport: (s: SupportDetail) => void; resources: Resource[]; notify: (m: string) => void; refresh: () => Promise<void>; close: () => void; onSheetCreated: (s: SheetDetail) => void }) {
  const draft = support.status === 'DRAFT'
  const [selected, setSelected] = useState<number[]>([])
  const [duration, setDuration] = useState(55)
  const teacherOnly = ['EXPECTED_RESULT', 'EXPECTED_TRACE', 'SOLUTION', 'CORRECTION', 'TEACHER_NOTE']
  async function add(id: number) { setSupport(await post<SupportDetail>(`/api/supports/${support.id}/resources/library`, { resource_version_id: id })); notify('Activité ajoutée au support.') }
  async function toggle(id: number, visible: boolean) { setSupport(await put<SupportDetail>(`/api/supports/${support.id}/blocks/${id}`, { visible })) }
  async function updateBlock(id: number, content_latex: string) { setSupport(await put<SupportDetail>(`/api/supports/${support.id}/blocks/${id}`, { content_latex })); notify('Bloc du support enregistré.') }
  async function move(id: number, direction: 'UP' | 'DOWN') { setSupport(await put<SupportDetail>(`/api/supports/${support.id}/blocks/${id}/position`, { direction })) }
  async function finalize() { if (!confirm('Finaliser cette révision du support ?')) return; setSupport(await post<SupportDetail>(`/api/supports/${support.id}/finalize`)); await refresh(); notify('Support finalisé.') }
  async function revise() { setSupport(await post<SupportDetail>(`/api/supports/${support.id}/new-revision`)); setSelected([]); await refresh() }
  async function exportPdf(target: 'LEARNER_INITIAL' | 'LEARNER_COMPLETED') { const result = await post<{ download_url: string }>('/api/exports', { document_family: 'LEARNER', revision_id: support.id, target }); window.open(result.download_url, '_blank'); notify(target === 'LEARNER_INITIAL' ? 'PDF initial généré.' : 'PDF complété généré.') }
  async function createSheet() {
    if (!selected.length) return
    const sheet = await post<SheetDetail>(`/api/supports/${support.id}/create-teacher-sheet`, {
      title: `Séance - ${support.title}`,
      selected_block_ids: selected,
      duration_minutes: duration,
      class_label: '4e',
      part_label: `${selected.length} bloc(s) sélectionné(s)`,
    })
    notify('Fiche de séance créée depuis cette révision du support.')
    onSheetCreated(sheet)
  }
  return <>
    <button className="back" onClick={close}>← Retour aux supports</button>
    <div className="editor-head"><div><div className="meta-line"><Status value={support.status} /><span>{support.code} · Révision {support.revision_number} · Portée {support.scope}</span></div><h2>{support.title}</h2><p>{support.situation && `${support.situation.code} - ${support.situation.title}`} {support.sequence && `· ${support.sequence.code} - ${support.sequence.title}`}</p></div>{!draft && <button className="primary" onClick={revise}>Nouvelle révision</button>}</div>
    <div className="two-columns"><section className="panel"><h3>Contenu du support</h3>{support.resources.length === 0 && <div className="empty small">Ajoutez une activité depuis la colonne de droite.</div>}
      {support.resources.map(r => <article className="support-resource" key={r.id}><h4>{r.title}</h4>{r.blocks.map((b, index) => { const selectable = b.visible !== false && !teacherOnly.includes(b.block_type); return <div className={b.visible === false ? 'hidden-block' : ''} key={b.id}><div className="block-head"><b>{b.title} <small>{b.block_type.replaceAll('_', ' ')}</small></b>{draft ? <div className="block-controls"><button onClick={() => move(b.id, 'UP')} disabled={index === 0}>↑</button><button onClick={() => move(b.id, 'DOWN')} disabled={index === r.blocks.length - 1}>↓</button><label className="switch">Visible <input type="checkbox" checked={b.visible !== false} onChange={e => toggle(b.id, e.target.checked)} /></label></div> : selectable && <label className="select-block"><input type="checkbox" checked={selected.includes(b.id)} onChange={e => setSelected(old => e.target.checked ? [...old, b.id] : old.filter(id => id !== b.id))} /> Utiliser dans la séance</label>}</div>{draft ? <LatexEditor block={b} disabled={false} onSave={value => updateBlock(b.id, value)} /> : b.visible !== false && <LatexPreview content={b.content_latex} />}</div> })}</article>)}
      <div className="final-actions">{draft && <button className="primary" onClick={finalize}>Finaliser</button>}<button className="outline" onClick={() => exportPdf('LEARNER_INITIAL')}>PDF initial</button><button className="outline" onClick={() => exportPdf('LEARNER_COMPLETED')}>PDF complété</button></div>
      {!draft && <div className="support-first"><h3>Créer une fiche de séance à partir de ce support</h3><p>Sélectionnez les blocs ci-dessus. La fiche conservera cette révision exacte et les résultats attendus commenceront vides.</p><label>Durée estimée (min)<input type="number" min="1" value={duration} onChange={e => setDuration(Number(e.target.value))} /></label><button className="primary" disabled={!selected.length} onClick={createSheet}>Créer la fiche depuis {selected.length} bloc(s)</button></div>}
    </section><aside className="panel picker"><h3>Ajouter une activité</h3>{resources.map(r => <button key={r.id} disabled={!draft} onClick={() => add(r.id)}><span>{r.provenance_kind === 'SOURCED' ? 'Guide' : 'DÉMO'}</span><b>{r.title}</b><small>＋ Ajouter</small></button>)}</aside></div>
  </>
}

function ProgressPage() { type Row = { instruction_id: number; code: string; text: string; executions: number; actual_minutes: number; status: string }; const [payload, setPayload] = useState<{instructions:Row[];normative_allocation:{status:string;values:{hours:number;source:string}[];remaining_hours:number|null}}>({instructions:[],normative_allocation:{status:'',values:[],remaining_hours:null}}); useEffect(() => { api<typeof payload>('/api/progress').then(setPayload) }, []); const rows = payload.instructions; const done = rows.filter(r => r.executions).length; return <section className="panel"><div className="panel-head"><div><h2>Progression pédagogique</h2><p>Suivi fondé uniquement sur les séances finalisées puis déclarées comme effectivement déroulées.</p></div><div className="progress-ring"><b>{done}/{rows.length}</b><small>instructions</small></div></div>{payload.normative_allocation.status === 'UNRESOLVED_NORMATIVE_ALLOCATION' && <div className="source-alert prominent"><strong>Reste théorique indéterminé</strong><span>Les sources portent des durées contradictoires ({payload.normative_allocation.values.map(v => `${v.hours} h — ${v.source}`).join(' ; ')}). Aucune valeur cachée n’est utilisée.</span></div>}<div className="progress-list">{rows.map(r => <div key={r.instruction_id}><span className={r.executions ? 'done-dot' : 'todo-dot'}>{r.executions ? '✓' : ''}</span><div><b>{r.code}</b><LatexPreview content={r.text} compact /></div><span>{r.executions ? `${r.actual_minutes} min réalisées` : 'Non commencée'}</span></div>)}</div></section> }

function SourcesPage({ resources }: { resources: Resource[] }) { const sourced = resources.filter(r => r.sources.length); return <><div className="source-alert prominent"><strong>Principe de fidélité</strong><span>Une référence de fichier et de page est affichée pour chaque contenu sourcé. Une proposition de démonstration reste explicitement non sourcée.</span></div><section className="panel"><h2>Registre des ressources pilotes</h2><div className="source-list">{resources.map(r => <article key={r.id}><div><span className={`badge ${r.sources.length ? 'source' : 'demo'}`}>{r.sources.length ? 'SOURCÉ' : 'DÉMO · NON SOURCÉ'}</span><h3>{r.title}</h3><p>{r.summary}</p></div>{r.sources.length ? r.sources.map(s => <dl key={s.sha256 + s.page}><dt>Document</dt><dd>{s.file_name}</dd><dt>Localisation</dt><dd>{s.locator}, p. {s.page}</dd><dt>Empreinte SHA-256</dt><dd className="hash">{s.sha256}</dd></dl>) : <div className="no-source">Aucune occurrence de source. Contenu fictif uniquement destiné à tester l’interface.</div>}</article>)}</div><h3>Sources distinctes utilisées</h3><ul>{Array.from(new Set(sourced.flatMap(r => r.sources.map(s => s.file_name)))).map(name => <li key={name}>{name}</li>)}</ul></section></> }
