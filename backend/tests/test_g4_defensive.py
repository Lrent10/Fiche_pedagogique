"""Defensive contract checks only: no filesystem-access payloads or bypasses."""
import hashlib

import pytest
from sqlalchemy import select

from app import models as m
from app.database import SessionLocal
from app.exporter import compile_pdf, document_preamble, safe_latex, snapshot_content
from app.latex_safety import ensure_safe_latex
from app.schemas import AddLocalResource, BlockUpdate, FlowItemUpdate
from test_resource_library import ADMIN_HEADERS, curriculum, mutate_json, package_bytes, rewrite_package, user_payload


def post_package(client, raw, route):
    return client.post(f"/api/admin/resource-packages/{route}", headers=ADMIN_HEADERS,
                       files={"package": ("defensive.zip", raw, "application/zip")})


def assert_controlled(client, raw):
    dry = post_package(client, raw, "dry-run")
    assert dry.status_code == 200
    report = dry.json()
    assert report["can_import"] is False
    assert report["validation_errors"]
    for error in report["validation_errors"]:
        assert {"code", "file", "line", "field", "message"} <= error.keys()
    assert post_package(client, raw, "import").status_code == 422
    assert not any(name in dry.text for name in ("UnicodeEncodeError", "UnicodeDecodeError", "Traceback", "TypeError"))


@pytest.mark.parametrize("content", [
    "Écrire une égalité.", r"$x^2+x_1$", r"$\frac{a}{b}+\sqrt{x}$",
    r"$\mathbb{R}, a\leq b, a\geq b$", r"$\sum_i a_i+\prod_i b_i$",
    r"\[\begin{aligned}a&=b\\c&=d\end{aligned}\]",
    r"$\begin{pmatrix}1&2\\3&4\end{pmatrix}$",
    r"\begin{tikzpicture}[scale=0.55]\draw[thick] (0,0) rectangle (2,2);\node at (1,1) {$a^2$};\end{tikzpicture}",
])
def test_g4_allowed_math_package_and_policy(client, content):
    assert ensure_safe_latex(content) == content
    dry = post_package(client, package_bytes(content=content), "dry-run")
    assert dry.status_code == 200 and dry.json()["can_import"] is True


def test_g4_allowed_math_renders_with_real_engine(tmp_path):
    content = (r"$x^2,x_1,\frac{a}{b},\sqrt{x},\mathbb{R},\leq,\geq,\sum,\prod$"
               r"\[\begin{aligned}a&=b\\c&=d\end{aligned}\]"
               r"$\begin{pmatrix}1&2\\3&4\end{pmatrix}$"
               r"\begin{tikzpicture}\draw[thick] (0,0) rectangle (2,2);\node at (1,1) {$a^2$};\end{tikzpicture}")
    output = tmp_path / "allowed-math.pdf"
    engine, log = compile_pdf(document_preamble("Mathématiques") + safe_latex(content) + r"\end{document}", output)
    assert engine == "LATEX", log
    assert output.stat().st_size > 1000


@pytest.mark.parametrize("content", [
    r"\unapprovedmath{x}", r"\newcommand{\example}{x}",
    r"\renewcommand{\example}{x}", r"\documentclass{article}",
    r"\usepackage{amsmath}", r"\begin{document}x\end{document}",
    r"\begin{unknownenvironment}x\end{unknownenvironment}",
    r"\begin{aligned}x\end{matrix}", r"\frac{a}{b", "x\x00y",
    r"\begin{tikzpicture}[unapproved=1]\draw (0,0)--(1,1);\end{tikzpicture}",
    r"\begin{tikzpicture}\draw[unapproved] (0,0)--(1,1);\end{tikzpicture}",
])
def test_g4_outside_subset_rejected_without_compilation(client, content):
    with pytest.raises(ValueError):
        ensure_safe_latex(content)
    assert_controlled(client, package_bytes(content=content))


def test_g4_shared_policy_real_entry_routes(client):
    content = r"\unapprovedmath{x}"
    result = client.post("/api/pedagogical-resources/user", json=user_payload(content=content))
    assert result.status_code == 422
    good = client.post("/api/pedagogical-resources/user", json=user_payload())
    assert good.status_code == 201
    resource_id = good.json()["id"]
    assert client.put(f"/api/pedagogical-resources/user/{resource_id}", json=user_payload(content=content)).status_code == 422
    instruction_id, _, _, _ = curriculum()
    payload = {"title": "Local", "level": "4e", "instruction_ids": [instruction_id],
               "source_ref": "Test", "source_version": "1",
               "blocks": [{"block_type": "CONSIGNE", "title": "Local", "content_latex": content}]}
    assert client.post("/api/authoring/resources", json=payload).status_code == 422
    # Local creation/update endpoints use the same shared input models.
    for model, payload in [(AddLocalResource, {"title": "Local", "content_latex": content}),
                           (BlockUpdate, {"content_latex": content}),
                           (FlowItemUpdate, {"expected_result_latex": content})]:
        with pytest.raises(ValueError):
            model.model_validate(payload)
    assert client.post("/api/sheets/99999/resources/local", json={"title": "Local", "content_latex": content}).status_code == 422
    assert client.put("/api/sheets/99999/blocks/99999", json={"content_latex": content}).status_code == 422
    assert client.put("/api/supports/99999/blocks/99999", json={"content_latex": content}).status_code == 422


@pytest.mark.parametrize("newline", ["\n", "\r", "\r\n"])
def test_g4_comments_do_not_skip_following_fragment_validation(newline):
    assert ensure_safe_latex("% Note" + newline + r"$\frac{a}{b}$")
    with pytest.raises(ValueError):
        ensure_safe_latex("% Note" + newline + r"\unapprovedmath{x}")


def test_g4_export_route_stops_unknown_fragment_before_engine(client, monkeypatch):
    # A stored legacy fragment must be checked again at export.
    with SessionLocal() as db:
        sheet = m.TeacherSessionSheet(code="G4-EXPORT", title="G4", level="4e")
        db.add(sheet); db.flush()
        revision = m.TeacherSheetRevision(sheet_id=sheet.id, revision_number=1)
        db.add(revision); db.flush()
        resource = m.SheetResourceInstance(teacher_revision_id=revision.id, title="G4", origin="LOCAL_ORIGINAL", position=1)
        db.add(resource); db.flush()
        block = m.SheetBlockInstance(resource_instance_id=resource.id, block_type="CONSIGNE", title="G4",
                                     content_latex=r"\unapprovedmath{x}", position=1)
        db.add(block); db.flush()
        db.add(m.FlowItem(teacher_revision_id=revision.id, block_instance_id=block.id, phase_code="REALISATION", position=1))
        db.commit()
        revision_id = revision.id
    calls = []
    def unexpected_compiler(*args, **kwargs):
        calls.append(True)
        pytest.fail("Unapproved fragment reached compiler")
    monkeypatch.setattr("app.exporter.subprocess.run", unexpected_compiler)
    from app.config import settings
    before = set(settings.export_dir.glob("*.pdf"))
    response = client.post("/api/exports", json={"document_family": "TEACHER", "revision_id": revision_id})
    assert response.status_code == 400
    assert not calls
    assert set(settings.export_dir.glob("*.pdf")) == before


@pytest.mark.parametrize("file_name,field", [
    ("manifest.json", "package_version"), ("manifest.json", "producer"), ("manifest.json", "provenance_notice"),
    ("sources.jsonl", "title"), ("sources.jsonl", "authority"), ("sources.jsonl", "file_name"), ("sources.jsonl", "document_type"),
    ("resources.jsonl", "content"), ("resources.jsonl", "title"), ("resources.jsonl", "author"),
    ("resources.jsonl", "source_page"), ("resources.jsonl", "license_or_usage_note"),
    ("resource_instruction_links.jsonl", "relevance"), ("resource_instruction_links.jsonl", "validation_status"),
])
@pytest.mark.parametrize("text", ["\ud800", "\udfff"])
def test_g4_surrogates_controlled_in_package_text(client, file_name, field, text):
    assert_controlled(client, mutate_json(package_bytes(), file_name, {field: text}))


@pytest.mark.parametrize("file_name,field,value", [
    ("resources.jsonl", "metadata", {"nested": [{"name": "\ud800"}]}),
    ("resources.jsonl", "metadata", {"\ud800": "value"}),
    ("resource_instruction_links.jsonl", "provenance", {"nested": ["\udfff"]}),
    ("resource_instruction_links.jsonl", "provenance", {"\udfff": None}),
    ("manifest.json", "\ud800", "unknown key"),
    ("sources.jsonl", "\udfff", "unknown key"),
])
def test_g4_extensions_and_error_paths_remain_utf8_safe(client, file_name, field, value):
    assert_controlled(client, mutate_json(package_bytes(), file_name, {field: value}))


@pytest.mark.parametrize("file_name", ["manifest.json", "sources.jsonl", "resources.jsonl", "resource_instruction_links.jsonl"])
def test_g4_invalid_utf8_bytes_rejected(client, file_name):
    # Build hashes while the manifest is valid, then corrupt only the requested byte stream.
    raw = package_bytes()
    if file_name == "manifest.json":
        import io
        import zipfile
        with zipfile.ZipFile(io.BytesIO(raw)) as archive:
            files = {name: archive.read(name) for name in archive.namelist()}
        files[file_name] = b'\xff'
        output = io.BytesIO()
        with zipfile.ZipFile(output, "w") as archive:
            for name, data in files.items():
                archive.writestr(name, data)
        raw = output.getvalue()
    else:
        raw = rewrite_package(raw, lambda files: files.update({file_name: b'\xff'}))
    assert_controlled(client, raw)


def test_g4_legitimate_unicode_preserved_without_normalization(client):
    content = "Égalité : ∀ x ∈ ℝ, x² ≥ 0 ; e\u0301 ; enseignant 李."
    raw = mutate_json(package_bytes(content=content), "resources.jsonl", {"content_format": "TEXT", "author": "Adélaïde 李"})
    raw = mutate_json(raw, "sources.jsonl", {"title": "Géométrie — 李", "authority": "Équipe béninoise"})
    assert post_package(client, raw, "dry-run").json()["can_import"] is True
    assert post_package(client, raw, "import").status_code == 200
    with SessionLocal() as db:
        resource = db.scalar(select(m.PedagogicalResource).where(m.PedagogicalResource.code == "PKG-P3-001"))
        assert resource.content == content
        assert resource.content_hash == hashlib.sha256(content.encode("utf-8")).hexdigest()


def test_g4_text_mode_exact_escaping():
    raw = '#$%&_{}~^\\'
    expected = r'\#\$\%\&\_\{\}\textasciitilde{}\textasciicircum{}\textbackslash{}'
    assert snapshot_content({"content_format": "TEXT", "content": raw}) == expected


def test_g4_import_revalidates_changed_unicode(client):
    raw = package_bytes()
    assert post_package(client, raw, "dry-run").json()["can_import"] is True
    changed = mutate_json(raw, "sources.jsonl", {"authority": "\ud800"})
    assert post_package(client, changed, "import").status_code == 422
