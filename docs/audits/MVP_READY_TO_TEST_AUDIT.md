# MVP ready-to-test audit

Audit date: 2026-08-28  
Scope: local mathematics pedagogical sheet generator, 4e pilot, Benin.

## Baseline gate

- Frozen M01 exists and SHA-256 is `03F54F7C62A0E6F2F3BE154631EE542408BF5423B5D4FAD8B147CD85CE0E3B67`.
- `M01 FREEZE = CLOSED` and `M02 GATE = OPEN` are present in the independent re-audit.
- The source PDFs were read only; no source document was moved or modified.

## Independent internal review A–K

| Check | Evidence | Verdict |
|---|---|---|
| A. M01 invariant coverage | Matrix maps 50/50: 34 tested, 9 implemented, 7 partial/disclosed | PASS |
| B. Migration clean | Empty SQLite → Alembic `0001_initial` | PASS |
| C. Data seed | Idempotent seed; F-01..F-07 open; 56 h and 60 h both retained | PASS |
| D. Backend tests | 18 passed, 0 failed | PASS |
| E. Frontend tests | 3 passed, 0 failed; TypeScript/Vite build green | PASS |
| F. E2E | E2E-001 creates, adapts, finalizes, exports, executes and recalculates progress | PASS |
| G. Export | Three A4 PDFs compiled by MiKTeX and visually checked | PASS |
| H. Fresh startup | reset → migrate → seed → `start-dev.ps1` → health response | PASS |
| I. No source mutation | Only hashes/occurrences stored; PDFs remain external | PASS |
| J. No historical mutation | Snapshot and retirement tests; API plus transaction immutability guards | PASS |
| K. Hidden blocker review | No BLOCKER or MAJOR remains | PASS |

## Source-fidelity decisions

- The guide structure uses `SEQ8 — Calculs sur les expressions algébriques`.
- The example sheet occurrence mentioning `Séquence N°1` is recorded as `PILOT-OBS-01`, not silently made canonical.
- F-01 retains programme 56 h and guide 60 h. Progress returns `UNRESOLVED_NORMATIVE_ALLOCATION`, with no invented remainder.
- Three resources are sourced with file/page/SHA metadata; the fourth is explicitly `[DÉMO — NON SOURCÉ]` and has zero fake occurrences.

## Residual limitations

Seven invariant mechanisms are partial only where the pilot cannot exercise a wider scope: multi-SA transitions, phase-derived duration, repeated support-use UI and dedicated administration of proposed/block-level source data. Their persistence concepts exist and they are listed in `docs/KNOWN_LIMITATIONS.md`. They do not affect the tested one-sequence vertical slice.

## Verdict

**PASS — MVP 4E READY FOR USER TESTING**

