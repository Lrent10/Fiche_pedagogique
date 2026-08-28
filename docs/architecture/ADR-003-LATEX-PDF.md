# ADR-003 - LaTeX source, KaTeX preview, TeX PDF

Decision: persist LaTeX/TikZ source independently, preview ordinary math with KaTeX, and compile exports with local MiKTeX when safe. Use ReportLab only as a visible fallback.

Security: compilation uses a generated template, no shell escape, server-owned paths and a deny-list for document/file commands.

Status: ACCEPTED.

