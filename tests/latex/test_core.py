import pytest
from pathlib import Path
from latex.core import LateX


@pytest.fixture
def latex(tmp_path):
    """
    Provide a LateX instance with isolated output and templates folders.
    """
    ltx = LateX("test_doc")
    ltx.output_folder = tmp_path / "outputs"
    ltx.templates_folder = tmp_path / "templates"
    ltx.tex_path = ltx.output_folder / ltx.tex_file

    ltx.output_folder.mkdir()
    ltx.templates_folder.mkdir()
    return ltx


# -----------------------------
# Template loading
# -----------------------------


def test_load_template_copies_cls_and_sets_documentclass(latex):
    # Arrange
    cls_file = latex.templates_folder / "resume.cls"
    cls_file.write_text("% dummy resume class")

    # Act
    latex.load_template("resume")

    # Assert
    assert "\\documentclass{resume}" in latex.tex
    assert (latex.output_folder / "resume.cls").exists()


def test_load_template_raises_if_missing(latex):
    with pytest.raises(FileNotFoundError):
        latex.load_template("nonexistent")


# -----------------------------
# Document structure
# -----------------------------


def test_add_packages(latex):
    latex.add_packages(["amsmath", "graphicx"])
    assert "\\usepackage{amsmath}" in latex.tex
    assert "\\usepackage{graphicx}" in latex.tex


def test_margins(latex):
    latex.margins(left_margin=1, top_margin=1.5, right_margin=2, bottom_margin=2.5)
    assert "left=1in" in latex.tex
    assert "top=1.5in" in latex.tex
    assert "right=2in" in latex.tex
    assert "bottom=2.5in" in latex.tex


def test_begin_end_document(latex):
    latex.begin_document()
    latex.end_document()
    assert "\\begin{document}" in latex.tex
    assert "\\end{document}" in latex.tex


def test_begin_section(latex):
    latex.begin_section("Intro")
    latex.begin_section("Background", section_type="subsection")
    assert "\\section{Intro}" in latex.tex
    assert "\\subsection{Background}" in latex.tex


def test_vspace(latex):
    latex.vspace(2.5)
    assert "\\vspace{2.5em}" in latex.tex


# -----------------------------
# Commands
# -----------------------------


def test_add_command(latex):
    latex.add_command("mycmd", "\\textbf{#1}")
    assert "\\newcommand{\\mycmd}[1]{\\textbf{#1}}" in latex.tex


def test_indent_no_indent_commands(latex):
    latex.indent_command()
    latex.no_indent_command()

    assert "\\newcommand{\\tab}[1]{\\hspace{0.2667\\textwidth}}" in latex.tex
    assert "\\newcommand{\\itab}[1]{\\hspace{0em}}" in latex.tex


def test_footnote_command(latex):
    latex.footnote_command()
    assert "\\newcommand\\blfootnote[1]" in latex.tex
    assert "\\renewcommand\\thefootnote{}\\footnote{#1}" in latex.tex


# -----------------------------
# Utilities
# -----------------------------


def test_add_raw_tex(latex):
    latex.add_raw_tex("\\textbf{Hello}")
    assert "\\textbf{Hello}" in latex.tex


# -----------------------------
# File output
# -----------------------------


def test_compile_tex_file(latex):
    latex.tex = "Test content"
    latex.compile_tex_file()

    assert latex.tex_path.exists()
    assert "Test content" in latex.tex_path.read_text()


def test_create_pdf_writes_tex_only(tmp_path, monkeypatch):
    latex = LateX("pdf_doc")
    latex.output_folder = tmp_path
    latex.templates_folder = tmp_path
    latex.tex_path = tmp_path / "pdf_doc.tex"
    latex.tex = "PDF content"

    # Prevent actual pdflatex execution
    monkeypatch.setattr("os.system", lambda _: 0)

    latex.create_pdf(clean_aux=False)

    assert (tmp_path / "pdf_doc.tex").exists()
