import os
import pathlib
from typing import List
import shutil


class LateX:
    """
    A utility class to build and compile LaTeX documents programmatically.

    Features:
    - Add document class, margins, sections, commands, vertical spacing
    - Load templates
    - Compile .tex file and optionally generate PDF
    - Add footnotes, custom commands, and indentation helpers

    Parameters
    ----------
    tex_name : str
        Name of the LaTeX file (without extension)
    """

    def __init__(self, tex_name: str) -> None:
        """
        Initialize a LaTeX document generator.

        Parameters
        ----------
        tex_name : str
            Name of the LaTeX document (without extension)
        """
        self.tex_name = tex_name
        self.tex_file = f"{tex_name}.tex"
        self.tex = ""

        # Base folder is the directory where this script lives
        base_folder = pathlib.Path(__file__).parent.parent.resolve()

        # Output and templates folders relative to base folder
        self.output_folder = base_folder / "outputs"
        self.templates_folder = base_folder / "templates"
        self.tex_path = self.output_folder / self.tex_file

        # Ensure folders exist
        self.output_folder.mkdir(parents=True, exist_ok=True)
        self.templates_folder.mkdir(parents=True, exist_ok=True)

    # -----------------------------
    # Document structure methods
    # -----------------------------

    def load_template(self, template: str) -> None:
        """
        Set document class using a template (.cls file).

        The template is copied from the templates folder into the output
        directory so LaTeX can resolve it during compilation.

        Parameters
        ----------
        template : str
            Name of the LaTeX document class (without .cls)
        """
        cls_name = f"{template}.cls"
        src = self.templates_folder / cls_name
        dst = self.output_folder / cls_name

        if not src.exists():
            raise FileNotFoundError(
                f"Template '{cls_name}' not found in {self.templates_folder}"
            )

        # Copy template if not already present or if updated
        if not dst.exists() or src.stat().st_mtime > dst.stat().st_mtime:
            shutil.copy(src, dst)

        self.tex += f"\\documentclass{{{template}}}\n"

    def add_packages(self, packages: List[str]) -> None:
        """
        Include LaTeX packages.

        Parameters
        ----------
        packages : List[str]
            List of package names to include with \\usepackage{}
        """
        for pkg in packages:
            self.tex += f"\\usepackage{{{pkg}}}\n"

    def margins(
        self,
        left_margin: float = 0.4,
        top_margin: float = 0.4,
        right_margin: float = 0.4,
        bottom_margin: float = 0.4,
    ) -> None:
        """
        Set document margins.

        Parameters
        ----------
        left_margin : float, optional
        top_margin : float, optional
        right_margin : float, optional
        bottom_margin : float, optional
            Margins in inches
        """
        self.tex += (
            f"\\usepackage[left={left_margin}in, top={top_margin}in, "
            f"right={right_margin}in, bottom={bottom_margin}in]{{geometry}}\n"
        )

    def begin_document(self) -> None:
        """Start the document environment."""
        self.tex += "\\begin{document}\n"

    def end_document(self) -> None:
        """End the document environment."""
        self.tex += "\\end{document}\n"

    # -----------------------------
    # Section & spacing helpers
    # -----------------------------
    def begin_section(self, title: str, section_type: str = "section") -> None:
        """
        Start a new section or subsection.

        Parameters
        ----------
        title : str
            Section title
        section_type : str, optional
            LaTeX section type (default: 'section')
        """
        self.tex += f"\\{section_type}{{{title}}}\n"

    def end_section(self) -> None:
        """End of section is implicit in LaTeX; method exists for API consistency."""
        pass

    def vspace(self, space: float) -> None:
        """
        Insert vertical space.

        Parameters
        ----------
        space : float
            Space in em units
        """
        self.tex += f"\\vspace{{{space}em}}\n"

    # -----------------------------
    # Custom commands
    # -----------------------------
    def add_command(self, command_name: str, command_text: str) -> None:
        """
        Add a new LaTeX command.

        Parameters
        ----------
        command_name : str
            Name of the command
        command_text : str
            LaTeX text the command will expand to
        """
        self.tex += f"\\newcommand{{\\{command_name}}}[1]{{{command_text}}}\n"

    def indent_command(self) -> None:
        """Add a 'tab' command for standard indentation."""
        self.add_command("tab", "\\hspace{0.2667\\textwidth}")

    def no_indent_command(self) -> None:
        """Add an 'itab' command for no indentation."""
        self.add_command("itab", "\\hspace{0em}")

    def footnote_command(self) -> None:
        """Add a reusable footnote command without numbering."""
        command = (
            "\\newcommand\\blfootnote[1]{%\n"
            "  \\begingroup\n"
            "  \\renewcommand\\thefootnote{}\\footnote{#1}%\n"
            "  \\addtocounter{footnote}{-1}%\n"
            "  \\endgroup\n"
            "}\n"
        )
        self.tex += command

    # -----------------------------
    # File operations
    # -----------------------------
    def compile_tex_file(self) -> None:
        """Write the .tex file to the output folder."""
        with self.tex_path.open("w", encoding="utf-8") as f:
            f.write(self.tex)

    def create_pdf(self, clean_aux: bool = True) -> None:
        """
        Compile PDF using pdflatex.

        Parameters
        ----------
        clean_aux : bool, optional
            Delete intermediate files like .aux, .log, .out (default: True)
        """
        # Ensure .tex is written
        self.compile_tex_file()

        # Compile PDF
        cwd = os.getcwd()
        os.chdir(self.output_folder)
        os.system(f"pdflatex -interaction=nonstopmode {self.tex_file}")
        os.chdir(cwd)

        if clean_aux:
            for ext in [".aux", ".log", ".out", ".cls"]:
                path = self.output_folder / f"{self.tex_name}{ext}"
                if path.exists():
                    path.unlink()

    # -----------------------------
    # Utilities
    # -----------------------------
    def add_raw_tex(self, tex_code: str) -> None:
        """
        Append raw LaTeX code to the document.

        Parameters
        ----------
        tex_code : str
            LaTeX code snippet
        """
        self.tex += tex_code + "\n"
