# Known limitations

These limitations are non-blocking for the local 4e pilot.

1. SQLite is the tested local database. The model uses SQLAlchemy/Alembic and remains PostgreSQL-oriented, but no live PostgreSQL run was possible in this environment.
2. The loaded curriculum slice is SA1 / Sequence 8 only. Findings F-02..F-07 are preserved as open `SourceIssue`, but their complete out-of-slice curricula are not ingested.
3. KaTeX previews ordinary mathematics in the browser. TikZ is identified in the editor and rendered by the real LaTeX PDF compiler, not by KaTeX.
4. Strict transition validation across multiple sequences or successive SAs is not exercised by the one-sequence pilot. Ordered segments are persisted, but the future multi-SA validator remains partial.
5. `ProposedContent`, block-level source occurrences, phase-derived duration and repeated support use are represented in persistence; their dedicated administration screens remain outside this lean MVP.
6. Invalid LaTeX is deliberately preserved. The export reports a visible fallback PDF instead of destroying the source.
7. The app has no authentication and binds only to `127.0.0.1`; it is a personal local MVP, not a public deployment.
8. The current demo learner support contains only two short activities; its QA page is therefore sparse even though the long-document template flows through two columns and multiple pages.
9. The support creation screen currently defaults to the first pilot sequence. It displays the exact SA/sequence scope, but choosing another scope remains outside the one-sequence pilot.
10. Source expected results and solutions can remain visible in the resource/support context, but V2 intentionally provides no one-click copy into the teacher's manual result field.
11. Wide figures are scaled to the current column. A dedicated full-page-width figure placement remains a non-blocking enhancement for a later resource-enrichment lot.
