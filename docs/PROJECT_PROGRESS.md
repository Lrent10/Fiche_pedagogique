# Project progress

## Baseline

- M01 SHA-256: `03F54F7C62A0E6F2F3BE154631EE542408BF5423B5D4FAD8B147CD85CE0E3B67`
- M01 freeze: CLOSED
- M02 gate: OPEN
- Working branch: `feature/mvp-4e-ready-to-test`

## Phases

| Phase | Status | Evidence |
|---|---|---|
| M01 frozen functional model | COMPLETE | `M01_G1_FINAL_INDEPENDENT_REAUDIT.md` |
| M02-A technical architecture | COMPLETE | `docs/architecture/M02_TECHNICAL_ARCHITECTURE.md` |
| M02-B physical data model | COMPLETE | `docs/architecture/M02_PHYSICAL_DATA_MODEL.md` and invariant matrix |
| M03-M04 application and persistence | COMPLETE | FastAPI, SQLAlchemy, Alembic, contraintes et tests adversariaux |
| M05 curriculum pilote | COMPLETE | Seed idempotent, SA1, Séquence 8, instructions, F-01..F-07 préservés |
| M06 bibliothèque | COMPLETE | Ressources sourcées/démo, provenance, filtres, comparaison, snapshots |
| M07 fiche enseignant | COMPLETE | Parcours 8 étapes, LaTeX, déroulement, warnings, versionnement |
| M08 support apprenant | COMPLETE | Support séparé, variantes initiale/complétée, versionnement |
| M09 rendu et exports | COMPLETE | KaTeX, TikZ réel, 3 PDF LaTeX A4 contrôlés visuellement |
| M10 exécution/progression | COMPLETE | Séance exécutée, durée réelle, progression, ambiguïté normative |
| M11 interface | COMPLETE | React responsive, contrôle navigateur sans erreur console |
| M12 données et E2E | COMPLETE | Dataset reproductible et E2E-001 vert |
| M13 QA locale | COMPLETE | 18 tests backend, 3 frontend, build, reset et démarrage propres |

## Current gate

`READY_TO_TEST` — see `docs/audits/MVP_READY_TO_TEST_AUDIT.md` and `MVP_READY_TO_TEST_REPORT.md`.
