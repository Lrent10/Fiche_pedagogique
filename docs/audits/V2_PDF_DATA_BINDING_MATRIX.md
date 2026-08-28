# V2 PDF data-binding matrix

The revision JSON columns are historical snapshots: updating the UI changes a draft revision only; finalization makes it immutable.

| Field | UI | API | Persistence | Revision snapshot | Template variable | PDF | Test |
|---|---|---|---|---|---|---|---|
| Course title | Identification | `SheetMetadataUpdate.identification` | `identification_json` | `TeacherSheetRevision` | `titre du cours` | Header + identity | DOC-001 |
| Sheet number | Identification | same | same | same | `numéro fiche pédagogique` | Header + identity | DOC-001 |
| Establishment | Identification | same | same | same | `établissement` | Identity | DOC-001 + sentinel |
| School year | Identification | same | same | same | `année scolaire` | Identity | DOC-001 + sentinel |
| Discipline | Identification | same | same | same | `discipline` | Identity | DOC-001 |
| Date | Identification | same | same | same | `date` | Identity | DOC-001 |
| Teacher | Identification | same | same | same | `nom du professeur` | Identity | DOC-001 + sentinel |
| Class / headcount / groups | Identification | same | same | same | corresponding keys | Identity | DOC-001 + sentinel |
| SA / SA title / curricular time | Identification | same | same | same | corresponding keys | Identity | DOC-001 |
| Sequence / sequence title | Identification | same | same | same | corresponding keys | Identity | DOC-001 |
| Session duration / number | Identification | same | same | same | corresponding keys | Identity | DOC-001 + sentinel |
| Training content | Planning | `SheetMetadataUpdate.planning` | `planning_json` | `TeacherSheetRevision` | `contenus de formation` | Planning | DOC-001 |
| Three competence families | Planning | same | same | same | competence keys | Planning | DOC-002 |
| Knowledge and techniques | Planning | same | same | same | `connaissances et techniques` | Planning | DOC-003 |
| Learning-object strategy | Planning | same | same | same | `stratégie objet d'apprentissage` | Planning | DOC-003 |
| Teaching strategies | Flow + planning | `FlowItemUpdate` / metadata | `flow_items.strategy` / JSON | exact revision rows | `strategy` | Flow + planning | DOC-002 |
| Learner / teacher equipment | Planning | metadata | `planning_json` | `TeacherSheetRevision` | equipment keys | Planning | DOC-004 |
| Manual expected result | Flow editor | `FlowItemUpdate.expected_result_latex` | `flow_items.expected_result_latex` | exact flow row | `expected_result_latex` | Flow, when non-empty | DOC-005 + sentinel |
| Source result / solution | Read-only source data | not copied | source resource only | not written as manual result | none | absent from manual result | DOC-006 |
| Support revision and portion | Support block selection | `SheetFromSupportCreate` | `support_uses` | exact revision + JSON IDs | provenance metadata | historical relation | DOC-009/010 + WF-002/003 |

Sentinel values checked after real PDF generation and text extraction include `CEG_TEST_EXPORT_987`, `PROF_TEST_EXPORT_654`, `43`, `2026-2027`, session `17`, and `RESULTAT_PDF_MANUEL_456`.
