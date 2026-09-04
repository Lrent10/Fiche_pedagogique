# Known limitations

These limitations are non-blocking for the local 4e pilot.

1. SQLite is the tested local database. The model uses SQLAlchemy/Alembic and remains PostgreSQL-oriented, but no live PostgreSQL run was possible in this environment.
2. The loaded curriculum slice is SA1 / Sequence 8 only. Findings F-02..F-07 are preserved as open `SourceIssue`, but their complete out-of-slice curricula are not ingested.
3. KaTeX previews ordinary mathematics in the browser. TikZ is identified in the editor and rendered by the real LaTeX PDF compiler, not by KaTeX.
4. Strict transition validation across multiple sequences or successive SAs is not exercised by the one-sequence pilot. Ordered segments are persisted, but the future multi-SA validator remains partial.
5. `ProposedContent`, block-level source occurrences, phase-derived duration and repeated support use are represented in persistence; their dedicated administration screens remain outside this lean MVP.
6. Invalid LaTeX is deliberately preserved. The export reports a visible fallback PDF instead of destroying the source.
7. The app has no authentication and binds only to `127.0.0.1`; it is a personal local MVP, not a public deployment.
8. V2-03 excludes typed response areas and removes the known historical “Réponse”/vertical-space suffix at render time, without rewriting saved revisions. Arbitrary answer prose inside a wrongly typed instruction cannot be identified semantically by this MVP. Long blocks may continue across columns; one-piece cutout layout is not guaranteed for them.
9. The support creation screen currently defaults to the first pilot sequence. It displays the exact SA/sequence scope, but choosing another scope remains outside the one-sequence pilot.
10. Source expected results and solutions can remain visible in the resource/support context, but V2 intentionally provides no one-click copy into the teacher's manual result field.
11. Wide figures are scaled to the current column. A dedicated full-page-width figure placement remains a non-blocking enhancement for a later resource-enrichment lot.
12. The final editor performs deliberately simple LaTeX checks for balanced dollars and braces. Full semantic validation still belongs to the real PDF compilation step.

## V2-03 additions (2026-09-04)

13. The initial candidate corpus covers instructions 3, 4 and 6. Automatic composition of all seven instructions is deliberately refused until resources are added for 1, 2, 5 and 7. The curriculum instructions themselves are present.
14. The 56 h programme / 60 h guide discrepancy remains unresolved. No session duration or transdisciplinary competency is invented from it or from a sample lesson.
15. Source-derived historical resources are adaptations to review, not certified transcriptions. Inspector validation requires a reference but there is no authenticated inspector account workflow. The enrichment API accepts all source kinds; the new UI registers personal resources only.
16. Première C documents were studied for model applicability only. Their sequence numbering and page offsets require explicit mapping before ingestion; Première C is not enabled in the UI.
17. Reusable teacher fields are stored in the current browser after creation. Later sheet edits do not automatically update this local profile. There is no cloud synchronization.
18. The completed learner API target remains available as a compatibility alias with teacher answers excluded. Regenerating an older PDF uses the new rendering semantics; stored revision contents remain unchanged.
19. Browser scenarios were executed by the agent, not independently by a teacher. Finalization freezes a document; it does not certify mathematical correctness or completeness of locally entered expected results and durations.
20. Vite reports a 505.29 kB JavaScript chunk; build succeeds. No bundle architecture refactoring was added.
21. Historical migration 0001 builds from current ORM metadata. Guarded additive migrations support both that fresh-install path and existing databases; upgrade paths were tested, downgrade paths were not exercised.
