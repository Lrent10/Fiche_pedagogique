from __future__ import annotations

import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from sqlalchemy import select
from sqlalchemy.orm import Session

from . import models as m
from .config import settings
from .services import sheet_detail, support_detail


FORBIDDEN_LATEX = re.compile(
    r"\\(write18|write|input|include|openout|read|usepackage|documentclass|begin\s*\{document\}|end\s*\{document\}|scantokens|immediate)",
    re.IGNORECASE,
)


def escape_text(value: object) -> str:
    text = str(value)
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(replacements.get(char, char) for char in text)


def safe_latex(value: str) -> str:
    if FORBIDDEN_LATEX.search(value):
        raise ValueError("Commande LaTeX interdite dans le contenu utilisateur.")
    return value


def document_preamble(title: str) -> str:
    return rf"""\documentclass[11pt,a4paper]{{article}}
\usepackage[utf8]{{inputenc}}
\usepackage[T1]{{fontenc}}
\usepackage[french]{{babel}}
\usepackage{{geometry}}
\usepackage{{amsmath,amssymb,array,longtable,xcolor,tikz}}
\geometry{{margin=1.5cm}}
\definecolor{{primary}}{{HTML}}{{174A5B}}
\definecolor{{soft}}{{HTML}}{{EAF2F3}}
\setlength{{\parindent}}{{0pt}}
\setlength{{\parskip}}{{4pt}}
\newcommand{{\sectionbar}}[1]{{\par\medskip\noindent\colorbox{{primary}}{{\parbox{{0.96\linewidth}}{{\color{{white}}\bfseries #1}}}}\par\smallskip}}
\begin{{document}}
\begin{{center}}
{{\Large\bfseries {escape_text(title)}}}\\[2pt]
{{\small Mathématiques — Classe de 4e — Bénin}}
\end{{center}}
"""


def teacher_tex(detail: dict) -> str:
    parts = [document_preamble("FICHE PÉDAGOGIQUE DE L'ENSEIGNANT")]
    parts.append(r"\sectionbar{I. ÉLÉMENTS D'IDENTIFICATION}")
    parts.append(r"\begin{tabular}{|p{0.28\linewidth}|p{0.64\linewidth}|}\hline")
    for key, value in detail["identification"].items():
        parts.append(f"\\textbf{{{escape_text(key.capitalize())}}} & {escape_text(value)} \\\\ \\hline")
    parts.append(r"\end{tabular}")
    parts.append(r"\sectionbar{II. ÉLÉMENTS DE PLANIFICATION}")
    parts.append(r"\begin{tabular}{|p{0.28\linewidth}|p{0.64\linewidth}|}\hline")
    for key, value in detail["planning"].items():
        parts.append(f"\\textbf{{{escape_text(key.replace('_', ' ').capitalize())}}} & {escape_text(value)} \\\\ \\hline")
    parts.append(r"\end{tabular}")
    parts.append(r"\subsection*{Instructions du guide mises en œuvre}")
    parts.append(r"\begin{enumerate}")
    for segment in detail["segments"]:
        parts.append(f"\\item {safe_latex(segment['text'])}")
    parts.append(r"\end{enumerate}")
    parts.append(r"\sectionbar{III. DÉROULEMENT}")
    parts.append(r"\footnotesize\begin{longtable}{|>{\raggedright\arraybackslash}p{0.13\linewidth}|>{\raggedright\arraybackslash}p{0.28\linewidth}|>{\raggedright\arraybackslash}p{0.20\linewidth}|>{\raggedright\arraybackslash}p{0.19\linewidth}|>{\raggedright\arraybackslash}p{0.07\linewidth}|}\hline")
    parts.append(r"\textbf{Phase} & \textbf{Contenu / consigne} & \textbf{Activité enseignant} & \textbf{Activité apprenant} & \textbf{Durée} \\ \hline")
    block_lookup = {block["id"]: block for resource in detail["resources"] for block in resource["blocks"]}
    for flow in detail["flow"]:
        block = block_lookup.get(flow["block_instance_id"])
        content = safe_latex(block["content_latex"]) if block else ""
        parts.append(
            f"{escape_text(flow['phase_code'].replace('_', ' ').title())} & {content} & {escape_text(flow['teacher_action'])} & "
            f"{escape_text(flow['learner_action'])} & {flow['duration_minutes']} min \\\\ \\hline"
        )
    parts.append(r"\end{longtable}")
    parts.append(r"\vfill{\footnotesize Document généré localement. Les références de source restent consultables dans l'application.}")
    parts.append(r"\end{document}")
    return "\n".join(parts)


def support_tex(detail: dict) -> str:
    parts = [document_preamble("FICHE DE L'APPRENANT")]
    parts.append(f"\\textbf{{Titre :}} {escape_text(detail['title'])}")
    parts.append(r"\sectionbar{ACTIVITÉS ET CONSIGNES}")
    for resource in detail["resources"]:
        parts.append(f"\\subsection*{{{escape_text(resource['title'])}}}")
        for block in resource["blocks"]:
            if not block["visible"]:
                continue
            parts.append(f"\\par\\medskip\\textbf{{{escape_text(block['title'])}}}\\par")
            parts.append(safe_latex(block["content_latex"]))
            parts.append(r"\par\smallskip")
            if block["block_type"] in {"INSTRUCTION", "APPLICATION"}:
                parts.append(r"\vspace{1.4cm}")
    parts.append(r"\vfill{\footnotesize Support de travail — Mathématiques 4e.}")
    parts.append(r"\end{document}")
    return "\n".join(parts)


def fallback_pdf(path: Path, title: str, lines: list[str]) -> None:
    pdf = canvas.Canvas(str(path), pagesize=A4)
    width, height = A4
    y = height - 55
    pdf.setFont("Helvetica-Bold", 15)
    pdf.drawString(45, y, title)
    y -= 30
    pdf.setFont("Helvetica", 9)
    for raw_line in lines:
        line = re.sub(r"\\[a-zA-Z]+|[{}$]", "", raw_line)
        while line:
            chunk, line = line[:105], line[105:]
            if y < 55:
                pdf.showPage()
                pdf.setFont("Helvetica", 9)
                y = height - 55
            pdf.drawString(45, y, chunk)
            y -= 12
    pdf.save()


def compile_pdf(tex: str, output: Path) -> tuple[str, str]:
    output.parent.mkdir(parents=True, exist_ok=True)
    pdflatex = shutil.which("pdflatex")
    if not pdflatex:
        fallback_pdf(output, "Document pédagogique", tex.splitlines())
        return "REPORTLAB_FALLBACK", "pdflatex indisponible"
    with tempfile.TemporaryDirectory(prefix="fiche_pdf_") as temp_name:
        temp = Path(temp_name)
        tex_path = temp / "document.tex"
        tex_path.write_text(tex, encoding="utf-8")
        command = [pdflatex, "-interaction=nonstopmode", "-halt-on-error", "-no-shell-escape", tex_path.name]
        try:
            result = subprocess.run(command, cwd=temp, capture_output=True, text=True, timeout=90)
        except (subprocess.TimeoutExpired, OSError) as exc:
            fallback_pdf(output, "Document pédagogique", tex.splitlines())
            return "REPORTLAB_FALLBACK", str(exc)
        generated = temp / "document.pdf"
        if result.returncode == 0 and generated.exists():
            shutil.copy2(generated, output)
            return "LATEX", result.stdout[-1000:]
        fallback_pdf(output, "Document pédagogique", tex.splitlines())
        return "REPORTLAB_FALLBACK", (result.stdout + result.stderr)[-2000:]


def export_document(db: Session, family: str, revision_id: int, target: str | None = None) -> m.DocumentExport:
    if family == "TEACHER":
        target = "TEACHER"
        detail = sheet_detail(db, revision_id)
        tex = teacher_tex(detail)
        file_name = f"fiche_enseignant_{detail['code']}_r{detail['revision_number']}.pdf"
    else:
        target = target or "LEARNER_INITIAL"
        if target not in {"LEARNER_INITIAL", "LEARNER_COMPLETED"}:
            raise ValueError("Cible incompatible avec un support apprenant.")
        detail = support_detail(db, revision_id)
        for resource in detail["resources"]:
            for block in resource["blocks"]:
                if block.get("source_block_id"):
                    variant = db.scalar(select(m.BlockVariant).where(m.BlockVariant.block_id == block["source_block_id"], m.BlockVariant.target == target))
                    if variant:
                        block["content_latex"] = variant.content_latex
        tex = support_tex(detail)
        suffix = "initiale" if target == "LEARNER_INITIAL" else "completee"
        file_name = f"fiche_apprenant_{suffix}_{detail['code']}_r{detail['revision_number']}.pdf"
    output = settings.export_dir / file_name
    engine, log = compile_pdf(tex, output)
    log_path = output.with_suffix(".log")
    log_path.write_text(f"ENGINE={engine}\n{log}", encoding="utf-8")
    record = m.DocumentExport(
        document_family=family,
        teacher_revision_id=revision_id if family == "TEACHER" else None,
        support_revision_id=revision_id if family == "LEARNER" else None,
        target=target,
        file_path=str(output),
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record
