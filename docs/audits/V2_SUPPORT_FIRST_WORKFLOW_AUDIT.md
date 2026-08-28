# V2 support-first workflow audit

## Implemented flow

1. Create or open a learner support.
2. Add, edit, reorder and hide/show blocks in a draft.
3. Preview in the screen; export initial or completed variants.
4. Finalize the support revision.
5. Select the exact visible learner blocks used in the session.
6. Enter an estimated duration and create the teacher sheet.
7. Complete identification, planning, strategy, duration and manual LaTeX expected results.
8. Finalize and export the teacher revision.

## Traceability

`SupportUse` stores:

- exact `LearnerSupportRevision.id`;
- linked `TeacherSheetRevision.id`;
- exact selected support-block IDs as JSON;
- human-readable part label;
- class and later teaching-session link.

Copied sheet blocks retain their original `source_block_id` where one exists. Expected results are initialized to an empty string and are never copied from source `EXPECTED_TRACE`, `SOLUTION` or `CORRECTION` blocks.

## Automated scenarios

| Scenario | Evidence | Result |
|---|---|---|
| WF-001 support → finalize → select 2 blocks → sheet → manual result → finalize → PDF | `test_wf_001_support_to_sheet_manual_result_finalize_and_export` | PASS |
| WF-002 later support edit does not change old sheet link or selected IDs | `test_wf_002_and_003_support_history_is_preserved` | PASS |
| WF-003 new support revision creates a new sheet while old sheet stays on R1 | same test | PASS |

The warnings endpoint reports a missing manual expected result for relevant instructions but does not block finalization, as required.
