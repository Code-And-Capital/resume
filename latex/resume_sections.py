from latex.core import LateX
from typing import Dict, List, Optional, Union


class HeaderSection:
    """
    Render the document header section.

    Responsible for generating the resume header including:
    - Full name
    - Contact information
    - Web presence (email, optional LinkedIn)

    Expected LaTeX commands (provided by the template):
    - \\name{}
    - \\address{}
    - \\href{}
    """

    def __init__(self, latex: LateX) -> None:
        """
        Initialize the HeaderSection.

        Parameters
        ----------
        latex : LateX
            An active LateX document builder instance.
        """
        self.latex = latex

    # -----------------------------
    # Internal helpers
    # -----------------------------

    def _add_name(self, full_name: str) -> None:
        """Render the name line."""
        self.latex.tex += f"\n\\name{{{full_name}}}"

    def _add_address_block(self, line1: str, line2: Optional[str] = None) -> None:
        """
        Render an address block with one or two lines.

        Parameters
        ----------
        line1 : str
            First line.
        line2 : Optional[str]
            Second line (optional).
        """
        if line2:
            self.latex.tex += f"\n\\address{{{line1} \\\\ {line2}}}"
        else:
            self.latex.tex += f"\n\\address{{{line1}}}"

    def _add_web_contact(self, email: str, linkedin: Optional[str]) -> None:
        """
        Render web contact information.

        Email is always rendered.
        LinkedIn is rendered only if provided.
        """
        email_link = f"\\href{{mailto:{email}}}{{{email}}}"

        if linkedin:
            linkedin_link = f"\\href{{{linkedin}}}{{{linkedin}}}"
            self._add_address_block(email_link, linkedin_link)
        else:
            self._add_address_block(email_link)

    # -----------------------------
    # Public API
    # -----------------------------

    def add_header(
        self,
        *,
        first_name: str,
        last_name: str,
        phone: str,
        location: str,
        email: str,
        linkedin: Optional[str] = None,
    ) -> None:
        """
        Render the complete resume header.

        Layout order:
        1. Full name
        2. Phone and location
        3. Email and optional LinkedIn

        Parameters
        ----------
        first_name : str
            First name.
        last_name : str
            Last name.
        phone : str
            Phone number.
        location : str
            City/state or country.
        email : str
            Email address.
        linkedin : Optional[str], optional
            LinkedIn profile URL. If None, omitted.
        """
        full_name = f"{first_name} {last_name}"

        self._add_name(full_name)
        self._add_address_block(phone, location)
        self._add_web_contact(email, linkedin)

        # Space after header
        self.latex.tex += "\n\n"


class SkillsSection:
    """
    Render the SKILLS section of the resume.

    Skills are displayed in a two-column table:
    - Left column: skill category (bold)
    - Right column: comma-separated list of skills

    The second column uses a fixed-width paragraph column to allow
    automatic line wrapping for long skill lists.
    """

    def __init__(self, latex: LateX) -> None:
        """
        Initialize the SkillsSection.

        Parameters
        ----------
        latex : LateX
            An active LateX document builder instance.
        """
        self.latex = latex

    # -----------------------------
    # Internal helpers
    # -----------------------------

    def _validate_skill(self, skill: Dict[str, List[str]]) -> None:
        """
        Validate a single skill entry.

        Raises
        ------
        KeyError
            If required keys are missing.
        TypeError
            If values have incorrect types.
        """
        if "category" not in skill or "items" not in skill:
            raise KeyError("Each skill must have 'category' and 'items' keys")

        if not isinstance(skill["category"], str):
            raise TypeError("'category' must be a string")

        if not isinstance(skill["items"], list):
            raise TypeError("'items' must be a list of strings")

    def _skill_row(self, category: str, items: List[str]) -> str:
        """
        Format a single table row for a skill category.

        Parameters
        ----------
        category : str
            Skill category name.
        items : List[str]
            List of skills in this category.

        Returns
        -------
        str
            LaTeX table row.
        """
        items_str = ", ".join(items)
        return f"\n{category} & {items_str}\\\\"

    # -----------------------------
    # Public API
    # -----------------------------

    def add_skills(self, skills: List[Dict[str, List[str]]]) -> None:
        """
        Render the SKILLS section.

        Parameters
        ----------
        skills : List[Dict[str, List[str]]]
            List of skill dictionaries of the form:
            {
                "category": "Languages",
                "items": ["Python", "SQL"]
            }
        """
        self.latex.begin_section("SKILLS", section_type="rSection")

        table = (
            "\\begin{tabular}{ @{} >{\\bfseries}l @{\\hspace{6ex}} "
            "p{0.8\\textwidth} }"
        )

        for skill in skills:
            self._validate_skill(skill)
            table += self._skill_row(skill["category"], skill["items"])

        table += "\n\\end{tabular}"

        self.latex.tex += table
        self.latex.end_section(section_type="rSection")


class ExperienceSection:
    """
    Render the PROFESSIONAL EXPERIENCE section of a LaTeX resume.

    Each experience entry includes:
        - Role
        - Company
        - Time period
        - Location
        - Optional bullet points describing responsibilities or achievements

    This class supports selecting which experiences to render by either an integer (first N)
    or a list of indices.
    """

    def __init__(self, latex: "LateX") -> None:
        """
        Initialize the ExperienceSection with a LaTeX builder instance.

        Parameters
        ----------
        latex : LateX
            An active LaTeX document builder instance. Must have 'begin_section', 'end_section',
            and 'tex' attributes.
        """
        self.latex = latex

    # -----------------------------
    # Internal helpers
    # -----------------------------

    def _validate_experience(self, experience: Dict) -> None:
        """
        Validate the structure and types of an experience dictionary.

        Parameters
        ----------
        experience : dict
            A dictionary representing a professional experience.

        Raises
        ------
        KeyError
            If a required field is missing.
        TypeError
            If a field has an incorrect type.
        """
        required_fields = {
            "role": str,
            "company": str,
            "start_date": str,
            "location": str,
            "end_date": (str, type(None)),  # end_date may be None
        }

        for field, field_type in required_fields.items():
            if field not in experience:
                raise KeyError(f"Missing required field '{field}'")
            if not isinstance(experience[field], field_type):
                raise TypeError(f"'{field}' must be of type {field_type}")

        # Validate bullets if present
        bullets = experience.get("bullets")
        if bullets is not None:
            if not isinstance(bullets, list) or not all(
                isinstance(b, str) for b in bullets
            ):
                raise TypeError("'bullets' must be a list of strings or None")

    def _format_period(self, start_date: str, end_date: Optional[str]) -> str:
        """
        Format a start and end date into a period string.

        Parameters
        ----------
        start_date : str
            Start date string.
        end_date : str or None
            End date string. If None, displays 'current'.

        Returns
        -------
        str
            Formatted period string.
        """
        return f"{start_date} - {end_date or 'current'}"

    def _header_block(
        self,
        role: str,
        company: str,
        period: str,
        location: str,
    ) -> str:
        """
        Render the header block for a single experience.

        Returns
        -------
        str
            LaTeX code for the header of an experience entry.
        """
        return (
            f"\n\\textbf{{{role}}} \\hfill {period}\\\\\n"
            f"{company} \\hfill \\textit{{{location}}}\n"
            "\\vspace{-0.5em}"
        )

    def _bullet_block(self, bullets: List[str]) -> str:
        """
        Render bullet points for an experience entry.

        Parameters
        ----------
        bullets : List[str]
            Bullet point descriptions.

        Returns
        -------
        str
            LaTeX itemize environment.
        """
        block = "\n\\begin{itemize}\n\\itemsep -6pt {}"
        for bullet in bullets:
            block += f"\n\\item {bullet}"
        block += "\n\\end{itemize}"
        return block

    def _experience_block(self, experience: Dict) -> str:
        """
        Render a complete experience entry in LaTeX.

        Parameters
        ----------
        experience : dict
            Experience dictionary.

        Returns
        -------
        str
            LaTeX representation of the experience.
        """
        period = self._format_period(experience["start_date"], experience["end_date"])
        block = self._header_block(
            role=experience["role"],
            company=experience["company"],
            period=period,
            location=experience["location"],
        )
        bullets = experience.get("bullets")
        if bullets:
            block += self._bullet_block(bullets)
        return block

    # -----------------------------
    # Public API
    # -----------------------------

    def add_experiences(
        self, experiences: List[Dict], select: Union[int, List[int], None] = None
    ) -> None:
        """
        Render the PROFESSIONAL EXPERIENCE section with optional selection.

        Parameters
        ----------
        experiences : List[Dict]
            List of experience dictionaries.
        select : int or List[int], optional
            If int, take the first `select` experiences.
            If list of ints, take experiences at these indices.
            If None, take all experiences.

        Raises
        ------
        TypeError
            If 'select' is neither an int, list of ints, nor None.
        IndexError
            If any index in a list selection is out of bounds.
        """
        # Determine which experiences to render
        if select is None:
            selected_experiences = experiences
        elif isinstance(select, int):
            if select < 0:
                raise ValueError("Integer 'select' must be non-negative")
            selected_experiences = experiences[:select]
        elif isinstance(select, list):
            if not all(isinstance(i, int) for i in select):
                raise TypeError("All elements of 'select' list must be integers")
            if any(i < 0 or i >= len(experiences) for i in select):
                raise IndexError("One or more indices in 'select' are out of bounds")
            selected_experiences = [experiences[i] for i in select]
        else:
            raise TypeError("'select' must be an int, list of ints, or None")

        self.latex.begin_section("PROFESSIONAL EXPERIENCE", section_type="rSection")
        for exp in selected_experiences:
            self._validate_experience(exp)
            self.latex.tex += self._experience_block(exp)
        self.latex.end_section(section_type="rSection")


class EducationSection:
    """Handle education section."""

    def __init__(self, latex: LateX):
        self.latex = latex

    def add_education(self, education_dict: Dict[str, Dict]) -> None:
        self.latex.begin_section("EDUCATION", section_type="rSection")
        for _, edu in education_dict.items():
            degree_subject = f"{edu['degree']} {edu['subject']}"
            year = f"{edu['year_start']} - {edu['year_end']}"
            row = (
                f"\n\\textbf{{{degree_subject}}} \\hfill {year}\\\\\n"
                f"{edu['school']} \\hfill \\textit{{{edu['location']}}}\n"
                "\\vspace{-0.5em}\n\\begin{itemize}\n\\itemsep -6pt {}"
            )
            for bullet in edu["bullet"]:
                row += f"\n\\item {bullet}"
            row += "\n\\end{itemize}"
            self.latex.tex += row
        self.latex.end_section("rSection")


class ProjectsSection:
    """Handle projects section."""

    def __init__(self, latex: LateX):
        self.latex = latex

    def add_projects(self, projects_dict: Dict[str, Dict]) -> None:
        self.latex.begin_section("PROJECTS", section_type="rSection")
        self.latex.vspace(-1.75)
        for _, proj in projects_dict.items():
            row = f"\n\\item \\textbf{{{proj['name']}}} {{{proj['bullet'][0]} \\href{{{proj['link']}}}{{(See more here)}}}}"
            self.latex.tex += row
        self.latex.end_section("rSection")


class CertificatesSection:
    """Handle certificates section."""

    def __init__(self, latex: LateX):
        self.latex = latex

    def add_certificates(self, cert_dict: Dict[str, Dict]) -> None:
        self.latex.begin_section("CERTIFICATIONS", section_type="rSection")
        self.latex.vspace(-1.75)
        for _, cert in cert_dict.items():
            link = cert.get("link", "")
            row = f"\n\\item \\textbf{{{cert['name']}}} {{{cert['bullet'][0]} \\href{{{link}}}{{(See more here)}}}}"
            self.latex.tex += row
        self.latex.end_section("rSection")
