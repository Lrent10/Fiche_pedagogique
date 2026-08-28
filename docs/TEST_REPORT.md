# Test report

Final execution date: 2026-08-28.

| Check | Result |
|---|---|
| Backend pytest | 18 passed, 0 failed |
| Frontend Vitest | 3 passed, 0 failed |
| TypeScript + Vite production build | PASS |
| E2E-001 API vertical slice | PASS (included in backend suite) |
| Migration from empty SQLite database | PASS |
| Idempotent seed | PASS |
| `reset-demo.ps1` | PASS |
| `start-dev.ps1` from reset state | PASS |
| Browser visual/interactive QA | PASS, 0 console warnings/errors |
| KaTeX formula preview | PASS |
| Real TikZ compilation | PASS |
| Teacher PDF, learner initial PDF, learner completed PDF | PASS, MiKTeX/LaTeX |
| Three final PDF visual renders | PASS after one template correction |

E2E-001 covers creation, candidate count, source/demo distinction, snapshot copy, LaTeX persistence, flow ordering, duration warning/correction, finalization, three exports, real execution and progress recalculation.
