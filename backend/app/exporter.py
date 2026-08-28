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
    r"\\(write18|write|input|include(?!graphics)|openout|read|usepackage|documentclass|begin\s*\{document\}|end\s*\{document\}|scantokens|immediate)",
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
    return rf"""\documentclass[10pt,a4paper]{{article}}
\usepackage[utf8]{{inputenc}}
\usepackage[T1]{{fontenc}}
\usepackage[french]{{babel}}
\usepackage{{geometry}}
\usepackage{{amsmath,amssymb,array,longtable,tabularx,multicol,fancyhdr,graphicx,tikz}}
\geometry{{top=1.05cm,bottom=1.15cm,left=1.15cm,right=1.15cm}}
\setlength{{\parindent}}{{0pt}}
\setlength{{\parskip}}{{2pt}}
\setlength{{\emergencystretch}}{{2em}}
\begin{{document}}
\begin{{center}}
{{\large\bfseries {escape_text(title)}}}
\end{{center}}
"""


def field_value(values: dict, key: str, *aliases: str) -> str:
    for candidate in (key, *aliases):
        value = values.get(candidate)
        if value not in (None, ""):
            return str(value)
    return ""


def labelled(label: str, value: object) -> str:
    return rf"\textbf{{{escape_text(label)} :}} {escape_text(value)}"


def teacher_tex(detail: dict) -> str:
    identification = detail["identification"]
    planning = detail["planning"]
    course_title = field_value(identification, "titre du cours") or detail["title"]
    sheet_number = field_value(identification, "numéro fiche pédagogique") or detail["code"]
    parts = [document_preamble(f"COURS DE MATHÉMATIQUES - {course_title}")]
    parts.append(rf"\begin{{center}}\textbf{{FICHE PÉDAGOGIQUE {escape_text(sheet_number)}}}\end{{center}}")
    parts.append(r"\hrule\vspace{2pt}\hrule\smallskip")
    parts.append(r"\begin{center}\textbf{I. ÉLÉMENTS D'IDENTIFICATION}\end{center}")
    identity_rows = [
        (("Établissement", field_value(identification, "établissement")), ("Année scolaire", field_value(identification, "année scolaire"))),
        (("Discipline", field_value(identification, "discipline") or "Mathématiques"), ("Date", field_value(identification, "date"))),
        (("Classe", field_value(identification, "classe")), ("Effectif", field_value(identification, "effectif"))),
        (("Nom du professeur", field_value(identification, "nom du professeur", "professeur")), ("Nombre de groupes", field_value(identification, "nombre de groupes", "groupes"))),
        (("SA", field_value(identification, "SA", "situation_apprentissage")), ("Titre SA", field_value(identification, "titre SA"))),
        (("Durée curriculaire SA", field_value(identification, "durée curriculaire SA")), ("Séquence", field_value(identification, "séquence"))),
        (("Titre séquence", field_value(identification, "titre séquence")), ("Durée de la séance", field_value(identification, "durée de la séance", "durée"))),
        (("Numéro de séance", field_value(identification, "numéro de séance", "numéro séance")), ("Titre du cours", course_title)),
    ]
    parts.append(r"\small\begin{tabularx}{\linewidth}{@{}X X@{}}")
    for left, right in identity_rows:
        parts.append(f"{labelled(*left)} & {labelled(*right)} " + r"\\")
    parts.append(r"\end{tabularx}")
    parts.append(r"\begin{center}\textbf{II. ÉLÉMENTS DE PLANIFICATION}\end{center}")
    planning_fields = [
        ("1. Contenus de formation", "contenus de formation"),
        ("2.a Compétences disciplinaires", "compétences disciplinaires"),
        ("2.b Compétence transdisciplinaire", "compétence transdisciplinaire"),
        ("2.c Compétences transversales", "compétences transversales"),
        ("3. Connaissances et techniques", "connaissances et techniques"),
        ("4. Stratégie objet d'apprentissage", "stratégie objet d'apprentissage"),
        ("5. Durée", "durée"),
        ("6. Stratégies d'enseignement/apprentissage", "stratégies d'enseignement/apprentissage", "stratégies"),
        ("7. Matériels apprenants", "matériels apprenants"),
        ("8. Matériels enseignant", "matériels enseignant"),
    ]
    for item in planning_fields:
        value = field_value(planning, item[1], *item[2:])
        parts.append(rf"\textbf{{{escape_text(item[0])} :}} {escape_text(value)}\par")
    if detail["segments"]:
        parts.append(r"\textbf{Instructions du guide mises en œuvre :}\begin{enumerate}")
        for segment in detail["segments"]:
            parts.append(rf"\item {safe_latex(segment['text'])}")
        parts.append(r"\end{enumerate}")
    parts.append(r"\begin{center}\textbf{III. DÉROULEMENT}\end{center}")
    block_lookup = {block["id"]: block for resource in detail["resources"] for block in resource["blocks"]}
    for index, flow in enumerate(detail["flow"], 1):
        block = block_lookup.get(flow["block_instance_id"])
        content = safe_latex(block["content_latex"]) if block else ""
        title = block.get("title", f"Élément {index}") if block else f"Élément {index}"
        kind = block.get("block_type", "SECTION").replace("_", " ").title() if block else "Section"
        parts.append(r"\par\smallskip\hrule\smallskip")
        parts.append(rf"\textbf{{{escape_text(kind)} {index} - {escape_text(title)}}}\hfill \textbf{{{flow['duration_minutes']} min}}\par")
        parts.append(content + r"\par")
        if flow.get("strategy"):
            parts.append(labelled("Stratégie", flow["strategy"]) + r"\par")
        if flow.get("teacher_action"):
            parts.append(labelled("Activité enseignant", flow["teacher_action"]) + r"\par")
        if flow.get("learner_action"):
            parts.append(labelled("Activité apprenant", flow["learner_action"]) + r"\par")
        expected = flow.get("expected_result_latex", "")
        if expected:
            parts.append(r"\textbf{Résultats attendus :}\par " + safe_latex(expected) + r"\par")
    parts.append(r"\vfill{\footnotesize Révision figée et générée localement. Les références de source restent consultables dans l'application.}")
    parts.append(r"\end{document}")
    return "\n".join(parts)


def support_tex(detail: dict, target: str = "LEARNER_INITIAL") -> str:
    sequence = detail.get("sequence") or {}
    situation = detail.get("situation") or {}
    parts = [rf"""\documentclass[10pt,a4paper]{{article}}
\usepackage[utf8]{{inputenc}}
\usepackage[T1]{{fontenc}}
\usepackage[french]{{babel}}
\usepackage{{geometry,amsmath,amssymb,array,multicol,fancyhdr,graphicx,tikz}}
\geometry{{top=1.25cm,bottom=1.25cm,left=1.2cm,right=1.2cm}}
\setlength{{\parindent}}{{0pt}}
\setlength{{\parskip}}{{2pt}}
\setlength{{\columnsep}}{{0.65cm}}
\setlength{{\columnseprule}}{{0.25pt}}
\setlength{{\emergencystretch}}{{2em}}
\pagestyle{{fancy}}\fancyhf{{}}
\lhead{{\small Mathématiques - 4e}}
\rhead{{\small {escape_text(detail['title'])}}}
\cfoot{{\thepage}}
\renewcommand{{\headrulewidth}}{{0.3pt}}
\renewcommand{{\footrulewidth}}{{0.3pt}}
\newcommand{{\SequenceTitle}}[1]{{\par\medskip\hrule\smallskip\textbf{{\large #1}}\smallskip\hrule\medskip}}
\newcommand{{\ActivityTitle}}[1]{{\par\medskip\textbf{{\fbox{{Activité}} #1}}\par\smallskip}}
\newcommand{{\InstructionTitle}}[1]{{\par\smallskip\textbf{{Consigne - #1}}\par}}
\newcommand{{\DefinitionBlock}}[2]{{\par\smallskip\textbf{{Définition - #1}}\par\emph{{#2}}\par}}
\newcommand{{\PropertyBlock}}[2]{{\par\smallskip\textbf{{Propriété - #1}}\par\emph{{#2}}\par}}
\newcommand{{\RemarkBlock}}[2]{{\par\smallskip\textbf{{Remarque - #1}}\par #2\par}}
\newcommand{{\MethodBlock}}[2]{{\par\smallskip\textbf{{Méthode - #1}}\par #2\par}}
\newcommand{{\RememberBlock}}[2]{{\par\smallskip\textbf{{Retenons - #1}}\par\textbf{{#2}}\par}}
\newcommand{{\ExerciseBlock}}[2]{{\par\smallskip\textbf{{Exercice - #1}}\par #2\par}}
\newcommand{{\Separator}}{{\par\smallskip\noindent\dotfill\par\smallskip}}
\begin{{document}}
\begin{{center}}\textbf{{\Large {escape_text(detail['title'])}}}\\
\small {escape_text(situation.get('code', ''))} {escape_text(situation.get('title', ''))} - {escape_text(sequence.get('code', ''))} {escape_text(sequence.get('title', ''))}
\end{{center}}
\begin{{multicols}}{{2}}
"""]
    teacher_only = {"EXPECTED_RESULT", "EXPECTED_TRACE", "SOLUTION", "CORRECTION", "TEACHER_NOTE"}
    for resource in detail["resources"]:
        parts.append(f"\\ActivityTitle{{{escape_text(resource['title'])}}}")
        for block in resource["blocks"]:
            if not block["visible"]:
                continue
            if target == "LEARNER_INITIAL" and block["block_type"] in teacher_only:
                continue
            title = escape_text(block["title"])
            content = safe_latex(block["content_latex"])
            block_type = block["block_type"]
            if block_type in {"INSTRUCTION", "CONSIGNE"}:
                parts.append(rf"\InstructionTitle{{{title}}}{content}")
            elif block_type == "DEFINITION":
                parts.append(rf"\DefinitionBlock{{{title}}}{{{content}}}")
            elif block_type == "PROPERTY":
                parts.append(rf"\PropertyBlock{{{title}}}{{{content}}}")
            elif block_type == "REMARK":
                parts.append(rf"\RemarkBlock{{{title}}}{{{content}}}")
            elif block_type == "METHOD":
                parts.append(rf"\MethodBlock{{{title}}}{{{content}}}")
            elif block_type in {"REMEMBER", "EXPECTED_RESULT", "EXPECTED_TRACE", "SOLUTION", "CORRECTION"}:
                parts.append(rf"\RememberBlock{{{title}}}{{{content}}}")
            elif block_type in {"EXERCISE", "APPLICATION"}:
                parts.append(rf"\ExerciseBlock{{{title}}}{{{content}}}")
            elif block_type in {"FIGURE", "TIKZ", "IMAGE"}:
                parts.append(rf"\par\textbf{{{title}}}\par\begin{{center}}\resizebox{{\columnwidth}}{{!}}{{{content}}}\end{{center}}")
            else:
                parts.append(rf"\par\smallskip\textbf{{{title}}}\par {content}\par")
            parts.append(r"\Separator")
    parts.append(r"\end{multicols}")
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
        tex = support_tex(detail, target)
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
