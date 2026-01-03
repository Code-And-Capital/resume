import pytest
from unittest.mock import patch
from pathlib import Path
from latex.core import LateX


@pytest.fixture
def latex():
    return LateX("test_doc")


def test_load_template(latex):
    latex.load_template("article")
    assert "\\documentclass{article}" in latex.tex


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
    latex.begin_section("Introduction")
    latex.begin_section("Background", section_type="subsection")
    assert "\\section{Introduction}" in latex.tex
    assert "\\subsection{Background}" in latex.tex


def test_vspace(latex):
    latex.vspace(2.5)
    assert "\\vspace{2.5em}" in latex.tex


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


def test_add_raw_tex(latex):
    latex.add_raw_tex("\\textbf{Hello}")
    assert "\\textbf{Hello}" in latex.tex


def test_compile_tex_file(tmp_path):
    latex = LateX("tmp_doc")
    latex.tex = "Test content"
    latex.output_folder = tmp_path
    latex.tex_path = tmp_path / "tmp_doc.tex"
    latex.compile_tex_file()
    file_content = (tmp_path / "tmp_doc.tex").read_text()
    assert "Test content" in file_content


@patch("os.system")
def test_create_pdf_calls_pdflatex(mock_system, tmp_path):
    latex = LateX("pdf_doc")
    latex.tex = "PDF content"
    latex.output_folder = tmp_path
    latex.tex_path = tmp_path / "pdf_doc.tex"

    latex.create_pdf(clean_aux=False)

    # Check that pdflatex was called
    expected_cmd = f"pdflatex -interaction=nonstopmode {latex.tex_file}"
    mock_system.assert_called_with(expected_cmd)

    # Ensure .tex file was written
    assert (tmp_path / "pdf_doc.tex").exists()
