import pytest

from app.exporter import compile_pdf, document_preamble, safe_latex, support_tex, teacher_tex


def test_safe_latex_accepts_math_and_tikz():
    content = r"$(a+b)^2=a^2+2ab+b^2$\begin{tikzpicture}\draw (0,0)--(1,1);\end{tikzpicture}"
    assert safe_latex(content) == content


def test_safe_latex_rejects_file_input():
    with pytest.raises(ValueError):
        safe_latex(r"\input{secret.txt}")


def test_teacher_template_contains_three_required_sections():
    detail = {
        "code": "TEST",
        "revision_number": 1,
        "title": "Test",
        "identification": {"classe": "4e"},
        "planning": {"séquence": "Séquence 8"},
        "segments": [{"text": "Développer un produit."}],
        "resources": [{"blocks": [{"id": 1, "content_latex": r"$(a+b)^2$"}]}],
        "flow": [{"block_instance_id": 1, "phase_code": "RÉALISATION", "teacher_action": "Guide", "learner_action": "Cherche", "duration_minutes": 10}],
    }
    tex = teacher_tex(detail)
    assert "I. ÉLÉMENTS D'IDENTIFICATION" in tex
    assert "II. ÉLÉMENTS DE PLANIFICATION" in tex
    assert "III. DÉROULEMENT" in tex


def test_support_template_hides_non_visible_blocks():
    detail = {"code": "SUP", "revision_number": 1, "title": "Support", "resources": [{"title": "R", "blocks": [{"title": "Caché", "content_latex": "SECRET", "visible": False, "block_type": "PROPERTY"}]}]}
    assert "SECRET" not in support_tex(detail)


def test_real_tikz_compilation_when_tex_is_available(tmp_path):
    tex = document_preamble("Test TikZ") + r"\begin{tikzpicture}\draw[thick] (0,0) rectangle (2,2);\node at (1,1) {$a^2$};\end{tikzpicture}\end{document}"
    output = tmp_path / "tikz.pdf"
    engine, _ = compile_pdf(tex, output)
    assert engine == "LATEX"
    assert output.is_file() and output.stat().st_size > 1000
