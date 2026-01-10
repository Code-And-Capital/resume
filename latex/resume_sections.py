from latex.core import LateX
from typing import Dict, List, Optional, Union, Callable


# ============================================================
# Header Section
# ============================================================


class HeaderSection:
    """
    Render the resume header section with contact information.

    Creates a professionally formatted header at the top of the resume
    containing the candidate's name and all contact details. The header
    uses LaTeX commands from the resume document class for consistent
    styling.

    Layout:
    - Line 1: Full name (large, bold, centered)
    - Line 2+: Contact info (phone, location, LinkedIn, email)

    Attributes
    ----------
    latex : LateX
        Reference to the LaTeX document builder instance.

    Examples
    --------
    >>> latex = LateX()
    >>> header = HeaderSection(latex)
    >>> header.add_header(
    ...     first_name="John",
    ...     last_name="Smith",
    ...     phone="+1-555-1234",
    ...     location="New York, NY",
    ...     email="john.smith@email.com",
    ...     linkedin="https://linkedin.com/in/johnsmith"
    ... )
    """

    def __init__(self, latex: LateX) -> None:
        """
        Initialize the HeaderSection.

        Parameters
        ----------
        latex : LateX
            LaTeX document builder instance that accumulates resume content.
        """
        self.latex = latex

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
        Generate and add the resume header with all contact information.

        All contact information is formatted with proper LaTeX commands and
        hyperlinks. The email becomes a mailto: link, and the LinkedIn URL
        (if provided) becomes a clickable web link.

        Parameters
        ----------
        first_name : str
            Candidate's first name.
        last_name : str
            Candidate's last name.
        phone : str
            Phone number in any format (e.g., "+1-555-0123", "(555) 123-4567").
        location : str
            City and state/country (e.g., "San Francisco, CA").
        email : str
            Email address for contact.
        linkedin : Optional[str], default=None
            Full LinkedIn profile URL. Should start with https://.
            If None, LinkedIn is omitted from the header.

        Notes
        -----
        All contact information is combined into a single LaTeX \\address{}
        command, with items separated by \\\\ for line breaks.

        Examples
        --------
        >>> # Header with LinkedIn
        >>> header.add_header(
        ...     first_name="Jane",
        ...     last_name="Doe",
        ...     phone="+1-555-0123",
        ...     location="Boston, MA",
        ...     email="jane.doe@example.com",
        ...     linkedin="https://linkedin.com/in/janedoe"
        ... )
        >>>
        >>> # Header without LinkedIn
        >>> header.add_header(
        ...     first_name="Bob",
        ...     last_name="Wilson",
        ...     phone="(555) 987-6543",
        ...     location="Seattle, WA",
        ...     email="bob.wilson@email.com"
        ... )
        """
        # Add name
        self.latex.tex += f"\n\\name{{{first_name} {last_name}}}"

        # First line: phone and location
        self.latex.tex += f"\n\\address{{{phone} \\\\ {location}}}"

        # Second line: email and optional LinkedIn
        email_link = f"\\href{{mailto:{email}}}{{{email}}}"
        if linkedin:
            linkedin_link = f"\\href{{{linkedin}}}{{{linkedin}}}"
            self.latex.tex += f"\n\\address{{{email_link} \\\\ {linkedin_link}}}"
        else:
            self.latex.tex += f"\n\\address{{{email_link}}}"

        self.latex.tex += "\n\n"


# ============================================================
# Skills Section
# ============================================================


class SkillsSection:
    """
    Render the SKILLS section as a two-column table.

    Skills are organized by category (e.g., "Programming Languages", "Tools")
    with comma-separated items. The table uses a bold left column for categories
    and a wrapping right column for skill items.

    Table format:
    - Left column: Bold category names, fixed width
    - Right column: 80% text width with automatic wrapping
    - Spacing: 6ex between columns

    Attributes
    ----------
    latex : LateX
        Reference to the LaTeX document builder instance.

    Examples
    --------
    >>> latex = LateX()
    >>> skills_section = SkillsSection(latex)
    >>> skills = [
    ...     {
    ...         "category": "Programming Languages",
    ...         "items": ["Python", "JavaScript", "Go"]
    ...     },
    ...     {
    ...         "category": "Frameworks",
    ...         "items": ["React", "Django", "FastAPI"]
    ...     }
    ... ]
    >>> skills_section.add_skills(skills)
    """

    def __init__(self, latex: LateX) -> None:
        """
        Initialize the SkillsSection.

        Parameters
        ----------
        latex : LateX
            LaTeX document builder instance.
        """
        self.latex = latex

    def _validate_skill(self, skill: Dict[str, Union[str, List[str]]]) -> None:
        """
        Validate a single skill entry structure and types.

        Parameters
        ----------
        skill : Dict[str, Union[str, List[str]]]
            Skill dictionary to validate. Must contain 'category' (str)
            and 'items' (List[str]) keys.

        Raises
        ------
        KeyError
            If 'category' or 'items' keys are missing.
        TypeError
            If 'category' is not a string or 'items' is not a list of strings.
        """
        if "category" not in skill or "items" not in skill:
            raise KeyError("Each skill must have 'category' and 'items'")
        if not isinstance(skill["category"], str):
            raise TypeError("'category' must be str")
        if not isinstance(skill["items"], list) or not all(
            isinstance(i, str) for i in skill["items"]
        ):
            raise TypeError("'items' must be a list of strings")

    def _skill_row(self, skill: Dict[str, Union[str, List[str]]]) -> str:
        """
        Render a single table row for a skill category.

        Parameters
        ----------
        skill : Dict[str, Union[str, List[str]]]
            Skill dictionary with 'category' and 'items'.

        Returns
        -------
        str
            LaTeX table row with category and comma-separated items.
        """
        return f"\n{skill['category']} & {', '.join(skill['items'])}\\\\"

    def add_skills(self, skills: List[Dict[str, Union[str, List[str]]]]) -> None:
        """
        Generate and add the complete SKILLS section.

        Creates a two-column table with all skill categories and items.
        The table uses special LaTeX formatting for proper alignment and
        text wrapping in the items column.

        Parameters
        ----------
        skills : List[Dict[str, Union[str, List[str]]]]
            List of skill dictionaries. Each must have:
            - 'category' (str): Category name (e.g., "Programming Languages")
            - 'items' (List[str]): List of skills in that category

        Raises
        ------
        KeyError
            If any skill dictionary is missing required keys.
        TypeError
            If skill data types are incorrect.

        Notes
        -----
        If the skills list is empty, the section is not rendered at all.

        Examples
        --------
        >>> skills_data = [
        ...     {"category": "Languages", "items": ["Python", "Java", "C++"]},
        ...     {"category": "Databases", "items": ["PostgreSQL", "MongoDB"]},
        ...     {"category": "Cloud", "items": ["AWS", "Azure", "GCP"]}
        ... ]
        >>> skills_section.add_skills(skills_data)
        """
        if not skills:
            return

        # Validate all skills before rendering
        for skill in skills:
            self._validate_skill(skill)

        # Begin SKILLS section
        self.latex.begin_section("SKILLS", section_type="rSection")

        # Create table with bold left column and wrapping right column
        table = (
            "\\begin{tabular}{ @{} >{\\bfseries}l @{\\hspace{6ex}} p{0.75\\textwidth} }"
        )
        table += "".join(self._skill_row(s) for s in skills)
        table += "\n\\end{tabular}"

        self.latex.tex += table
        self.latex.end_section(section_type="rSection")


# ============================================================
# Generic List-Based Sections
# ============================================================


class ListSection:
    """
    Abstract base class for sections with variable-length entry lists.

    Provides shared functionality for sections that display multiple similar
    entries (experiences, education, projects, certificates). Handles common
    operations like entry selection, bullet point rendering, validation,
    and LaTeX formatting.

    This base class eliminates code duplication across similar sections by
    providing generic methods that can be customized through subclass-specific
    rendering functions and validation logic.

    Subclasses must implement:
    - Validation methods for their specific entry structure
    - Block rendering methods to format individual entries
    - Public add_* methods that call add_section with appropriate parameters

    Attributes
    ----------
    latex : LateX
        Reference to the LaTeX document builder instance.
    section_name : str
        Display name of the section (e.g., "PROFESSIONAL EXPERIENCE", "EDUCATION").

    Examples
    --------
    >>> # ListSection is not used directly, but through subclasses
    >>> exp_section = ExperienceSection(latex)
    >>> edu_section = EducationSection(latex)
    """

    def __init__(self, latex: LateX, section_name: str) -> None:
        """
        Initialize a ListSection.

        Parameters
        ----------
        latex : LateX
            LaTeX document builder instance.
        section_name : str
            Display name for the section header (e.g., "PROJECTS", "CERTIFICATIONS").
        """
        self.latex = latex
        self.section_name = section_name

    # ---------------------------
    # Helper Functions
    # ---------------------------

    @staticmethod
    def _validate_bullets_field(item: Dict, name: str) -> None:
        """
        Validate that the 'bullets' field, if present, is a list of strings.

        This is a common validation used by multiple section types.

        Parameters
        ----------
        item : Dict
            Dictionary that may contain a 'bullets' field.
        name : str
            Name of the section type, used in error messages (e.g., "Experience").

        Raises
        ------
        TypeError
            If 'bullets' exists but is not a list of strings.
        """
        bullets = item.get("bullets")
        if bullets is not None:
            if not isinstance(bullets, list) or not all(
                isinstance(b, str) for b in bullets
            ):
                raise TypeError(f"{name} 'bullets' must be a list of strings or None")

    @staticmethod
    def apply_selection(
        items: List[Dict], select: Union[int, List[int], None], *, name: str
    ) -> List[Dict]:
        """
        Apply index-based selection to a list of entry dictionaries.

        Provides consistent selection behavior across all list-based sections.
        Supports three modes: all items, first N items, or specific items by index.

        Parameters
        ----------
        items : List[Dict]
            Full list of entries to select from.
        select : int | List[int] | None
            Selection rule:
            - None: return all items
            - int: return first N items
            - List[int]: return items at specific indices
        name : str
            Section name for error messages (e.g., "Experience", "Project").

        Returns
        -------
        List[Dict]
            Selected subset of items, preserving order.

        Raises
        ------
        ValueError
            If select is a negative integer.
        TypeError
            If select is not int, List[int], or None, or if list contains non-integers.
        IndexError
            If any index is out of bounds.

        Examples
        --------
        >>> items = [{"id": 1}, {"id": 2}, {"id": 3}]
        >>> ListSection.apply_selection(items, None, name="Test")
        [{"id": 1}, {"id": 2}, {"id": 3}]
        >>> ListSection.apply_selection(items, 2, name="Test")
        [{"id": 1}, {"id": 2}]
        >>> ListSection.apply_selection(items, [0, 2], name="Test")
        [{"id": 1}, {"id": 3}]
        """
        if select is None:
            return items

        if isinstance(select, int):
            if select < 0:
                raise ValueError(
                    f"{name} selection count must be non-negative, got {select}"
                )
            return items[:select]

        if isinstance(select, list):
            if not all(isinstance(i, int) for i in select):
                raise TypeError(f"All {name} selection indices must be integers")
            if any(i < 0 or i >= len(items) for i in select):
                raise IndexError(
                    f"{name} selection index out of bounds (0-{len(items)-1}): {select}"
                )
            return [items[i] for i in select]

        raise TypeError(f"{name} select parameter must be int, list of int, or None")

    @staticmethod
    def render_bullets(bullets: List[str]) -> str:
        """
        Render a compact LaTeX itemize environment for bullet points.

        Creates a tightly-spaced bullet list suitable for resume formatting.
        The spacing between items is reduced (-6pt) for a more compact
        appearance that fits more content on a page.

        Parameters
        ----------
        bullets : List[str]
            List of bullet point strings. Each string should be valid LaTeX text.

        Returns
        -------
        str
            LaTeX code for the bullet list, or empty string if bullets is empty.

        Examples
        --------
        >>> bullets = ["Led team of 5 engineers", "Increased efficiency by 40%"]
        >>> print(ListSection.render_bullets(bullets))
        \\begin{itemize}
        \\itemsep -6pt {}
        \\item Led team of 5 engineers
        \\item Increased efficiency by 40%
        \\end{itemize}
        """
        if not bullets:
            return ""
        return (
            "\n\\begin{itemize}\n\\itemsep -6pt {}\n"
            + "\n".join(f"\\item {b}" for b in bullets)
            + "\n\\end{itemize}"
        )

    @staticmethod
    def render_itemized_section(
        items: List[Dict], block_renderer: Callable[[Dict], str]
    ) -> str:
        """
        Render a complete itemized list section.

        Used for sections where each entry is an item in a LaTeX itemize
        environment (e.g., Projects, Certificates).

        Parameters
        ----------
        items : List[Dict]
            List of entry dictionaries to render.
        block_renderer : Callable[[Dict], str]
            Function that converts a single entry dict to LaTeX \\item string.

        Returns
        -------
        str
            Complete LaTeX itemize environment, or empty string if no items.

        Notes
        -----
        This is different from render_bullets - render_bullets creates bullets
        within an entry, while render_itemized_section creates an itemize list
        where each entry is an item.
        """
        if not items:
            return ""
        latex_block = "\n\\begin{itemize}"
        for item in items:
            latex_block += block_renderer(item)
        latex_block += "\n\\end{itemize}"
        return latex_block

    # ---------------------------
    # Generic add_section
    # ---------------------------

    def add_section(
        self,
        items: List[Dict],
        select: Union[int, List[int], None] = None,
        block_renderer: Optional[Callable[[Dict], str]] = None,
    ) -> None:
        """
        Generic method to add a list-based section to the document.

        This is the core rendering method that handles:
        1. Entry selection based on the select parameter
        2. Section begin/end LaTeX commands
        3. Rendering of individual entries using the provided block_renderer

        Parameters
        ----------
        items : List[Dict]
            Full list of entry dictionaries for this section.
        select : int | List[int] | None, default=None
            Selection mode for which entries to include.
        block_renderer : Callable[[Dict], str] | None, default=None
            Function that converts a single entry dict to LaTeX string.
            If None, uses render_itemized_section with render_bullets.

        Notes
        -----
        This method is called by subclass-specific add_* methods after
        validation. It should not be called directly by users.

        The method handles two rendering patterns:
        - Custom block rendering (Experience, Education): Each entry is a
          standalone block with its own formatting
        - Itemized rendering (Projects, Certificates): Entries are items
          in an itemize environment
        """
        selected = self.apply_selection(items, select, name=self.section_name)
        if not selected:
            return

        self.latex.begin_section(self.section_name, section_type="rSection")

        if block_renderer:
            # Custom block rendering (Experience, Education)
            for item in selected:
                self.latex.tex += block_renderer(item)
        else:
            # Itemized rendering (Projects, Certificates)
            self.latex.tex += self.render_itemized_section(
                selected, self.render_bullets
            )

        self.latex.end_section(section_type="rSection")


# ============================================================
# Experience Section
# ============================================================


class ExperienceSection(ListSection):
    """
    Render the PROFESSIONAL EXPERIENCE section with work history.

    Each experience entry includes role, company, employment dates, location,
    and optional bullet points describing responsibilities and achievements.

    Entry format:
    - Line 1: Bold role title | Right-aligned dates
    - Line 2: Company name | Right-aligned italic location
    - Lines 3+: Bullet points (if provided)

    Attributes
    ----------
    latex : LateX
        Reference to the LaTeX document builder instance.
    section_name : str
        Always "PROFESSIONAL EXPERIENCE".

    Examples
    --------
    >>> exp_section = ExperienceSection(latex)
    >>> experiences = [
    ...     {
    ...         "role": "Senior Software Engineer",
    ...         "company": "Tech Corp",
    ...         "start_date": "Jan 2020",
    ...         "end_date": "Dec 2023",
    ...         "location": "San Francisco, CA",
    ...         "bullets": [
    ...             "Led development of microservices architecture",
    ...             "Mentored 5 junior engineers"
    ...         ]
    ...     }
    ... ]
    >>> exp_section.add_experiences(experiences, select=3)
    """

    def __init__(self, latex: LateX) -> None:
        """
        Initialize the ExperienceSection.

        Parameters
        ----------
        latex : LateX
            LaTeX document builder instance.
        """
        super().__init__(latex, section_name="PROFESSIONAL EXPERIENCE")

    def _validate_experience(self, exp: Dict) -> None:
        """
        Validate an experience entry for required fields and correct types.

        Parameters
        ----------
        exp : Dict
            Experience dictionary to validate.

        Raises
        ------
        KeyError
            If any required field is missing.
        TypeError
            If any field has incorrect type.
        """
        required = {
            "role": str,
            "company": str,
            "start_date": str,
            "end_date": (str, type(None)),
            "location": str,
        }
        for k, t in required.items():
            if k not in exp:
                raise KeyError(f"Experience entry missing required field '{k}'")
            if not isinstance(exp[k], t):
                raise TypeError(
                    f"Experience field '{k}' must be of type {t}, "
                    f"got {type(exp[k]).__name__}"
                )
        self._validate_bullets_field(exp, "Experience")

    def _experience_block(self, exp: Dict) -> str:
        """
        Render a single experience entry with all details.

        Parameters
        ----------
        exp : Dict
            Experience dictionary with all required fields.

        Returns
        -------
        str
            LaTeX-formatted experience block.
        """
        period = f"{exp['start_date']} - {exp['end_date'] or 'Present'}"
        block = (
            f"\n\\textbf{{{exp['role']}}} \\hfill {period}\\\\\n"
            f"{exp['company']} \\hfill \\textit{{{exp['location']}}}\n"
            "\\vspace{-0.5em}"
        )
        if exp.get("bullets"):
            block += self.render_bullets(exp["bullets"])
        return block

    def add_experiences(
        self, experiences: List[Dict], select: Union[int, List[int], None] = None
    ) -> None:
        """
        Generate and add the PROFESSIONAL EXPERIENCE section.

        Parameters
        ----------
        experiences : List[Dict]
            List of experience dictionaries. Each must contain:
            - 'role' (str): Job title
            - 'company' (str): Company name
            - 'start_date' (str): Start date (e.g., "Jan 2020")
            - 'end_date' (str | None): End date or None for current position
            - 'location' (str): Job location
            - 'bullets' (List[str] | None): Achievement bullets (optional)
        select : int | List[int] | None, default=None
            Selection mode:
            - None: all experiences
            - int: first N experiences
            - List[int]: experiences at specific indices

        Raises
        ------
        KeyError
            If any experience entry is missing required fields.
        TypeError
            If any field has incorrect type.
        ValueError, IndexError
            If selection parameters are invalid.

        Examples
        --------
        >>> # Include all experiences
        >>> exp_section.add_experiences(all_experiences)
        >>>
        >>> # Include first 3 most recent experiences
        >>> exp_section.add_experiences(all_experiences, select=3)
        >>>
        >>> # Include specific experiences
        >>> exp_section.add_experiences(all_experiences, select=[0, 2, 5])
        """
        # Validate all experiences before rendering
        for exp in experiences:
            self._validate_experience(exp)

        self.add_section(
            experiences, select=select, block_renderer=self._experience_block
        )


# ============================================================
# Education Section
# ============================================================


class EducationSection(ListSection):
    """
    Render the EDUCATION section with academic credentials.

    Each education entry includes degree type, subject/major, institution,
    years attended, location, and optional bullet points for honors,
    coursework, or achievements.

    Entry format:
    - Line 1: Bold degree + subject | Right-aligned years
    - Line 2: Institution name | Right-aligned italic location
    - Lines 3+: Bullet points (if provided)

    Attributes
    ----------
    latex : LateX
        Reference to the LaTeX document builder instance.
    section_name : str
        Always "EDUCATION".

    Examples
    --------
    >>> edu_section = EducationSection(latex)
    >>> education = [
    ...     {
    ...         "degree": "Bachelor of Science",
    ...         "subject": "Computer Science",
    ...         "school": "Stanford University",
    ...         "start_year": 2016,
    ...         "end_year": 2020,
    ...         "location": "Stanford, CA",
    ...         "bullets": ["GPA: 3.9/4.0", "Dean's List all semesters"]
    ...     }
    ... ]
    >>> edu_section.add_education(education)
    """

    def __init__(self, latex: LateX) -> None:
        """
        Initialize the EducationSection.

        Parameters
        ----------
        latex : LateX
            LaTeX document builder instance.
        """
        super().__init__(latex, section_name="EDUCATION")

    def _validate_education(self, edu: Dict) -> None:
        """
        Validate an education entry for required fields and correct types.

        Parameters
        ----------
        edu : Dict
            Education dictionary to validate.

        Raises
        ------
        KeyError
            If any required field is missing.
        TypeError
            If any field has incorrect type.
        """
        required = {
            "degree": str,
            "subject": str,
            "school": str,
            "start_year": int,
            "end_year": (int, type(None)),
            "location": str,
        }
        for k, t in required.items():
            if k not in edu:
                raise KeyError(f"Education entry missing required field '{k}'")
            if not isinstance(edu[k], t):
                raise TypeError(
                    f"Education field '{k}' must be of type {t}, "
                    f"got {type(edu[k]).__name__}"
                )
        self._validate_bullets_field(edu, "Education")

    def _education_block(self, edu: Dict) -> str:
        """
        Render a single education entry with all details.

        Parameters
        ----------
        edu : Dict
            Education dictionary with all required fields.

        Returns
        -------
        str
            LaTeX-formatted education block.
        """
        period = f"{edu['start_year']} - {edu['end_year'] or 'Present'}"
        block = (
            f"\n\\textbf{{{edu['degree']} {edu['subject']}}} \\hfill {period}\\\\\n"
            f"{edu['school']} \\hfill \\textit{{{edu['location']}}}\n"
            "\\vspace{-0.5em}"
        )
        if edu.get("bullets"):
            block += self.render_bullets(edu["bullets"])
        return block

    def add_education(
        self, educations: List[Dict], select: Union[int, List[int], None] = None
    ) -> None:
        """
        Generate and add the EDUCATION section.

        Parameters
        ----------
        educations : List[Dict]
            List of education dictionaries. Each must contain:
            - 'degree' (str): Degree type (e.g., "Bachelor of Science", "M.S.")
            - 'subject' (str): Major/field of study
            - 'school' (str): Institution name
            - 'start_year' (int): Year started
            - 'end_year' (int | None): Graduation year or None if ongoing
            - 'location' (str): School location
            - 'bullets' (List[str] | None): Additional details (optional)
        select : int | List[int] | None, default=None
            Selection mode (same as ExperienceSection).

        Raises
        ------
        KeyError
            If any education entry is missing required fields.
        TypeError
            If any field has incorrect type.
        ValueError, IndexError
            If selection parameters are invalid.

        Examples
        --------
        >>> # Include all education
        >>> edu_section.add_education(all_education)
        >>>
        >>> # Include only highest degree
        >>> edu_section.add_education(all_education, select=1)
        >>>
        >>> # Include undergraduate and graduate degrees
        >>> edu_section.add_education(all_education, select=[0, 1])
        """
        # Validate all education entries before rendering
        for edu in educations:
            self._validate_education(edu)

        self.add_section(
            educations, select=select, block_renderer=self._education_block
        )


# ============================================================
# Projects Section
# ============================================================


class ProjectsSection(ListSection):
    """
    (docstring unchanged)
    """

    def __init__(self, latex: LateX) -> None:
        super().__init__(latex, section_name="PROJECTS")

    def _validate_project(self, proj: Dict) -> None:
        if "name" not in proj or "bullets" not in proj:
            raise KeyError("Project must include 'name' and 'bullets'")
        if not isinstance(proj["name"], str):
            raise TypeError("Project 'name' must be a string")
        if not isinstance(proj["bullets"], list) or not proj["bullets"]:
            raise TypeError("Project 'bullets' must be a non-empty list of strings")
        if not all(isinstance(b, str) for b in proj["bullets"]):
            raise TypeError("All project bullets must be strings")
        link = proj.get("link")
        if link is not None and not isinstance(link, str):
            raise TypeError("Project 'link' must be a string or None")

    def _project_block(self, proj: Dict) -> str:
        description = proj["bullets"][0]
        if proj.get("link"):
            description += f" \\href{{{proj['link']}}}{{(See more here)}}"
        return f"\\item \\textbf{{{proj['name']}}} {description}"

    def add_projects(
        self, projects: List[Dict], select: Union[int, List[int], None] = None
    ) -> None:
        # Validate projects
        for proj in projects:
            self._validate_project(proj)

        # Handle selection
        if select is None:
            selected = projects
        elif isinstance(select, int):
            selected = projects[:select]
        elif isinstance(select, list):
            selected = [projects[i] for i in select]
        else:
            raise ValueError("Invalid select argument")

        # Render each project item
        items_str = "\n".join(self._project_block(proj) for proj in selected)

        # Add section header and itemize block
        self.latex.tex += f"\n\\rSection{{{self.section_name}}}\n\\vspace{{-0.3em}}\n\\begin{{itemize}}\n\\itemsep -6pt {{}}\n{items_str}\n\\end{{itemize}}\n"


# ============================================================
# Certificates Section
# ============================================================


class CertificatesSection(ListSection):
    """
    (docstring unchanged)
    """

    def __init__(self, latex: LateX) -> None:
        super().__init__(latex, section_name="CERTIFICATIONS")

    def _validate_certificate(self, cert: Dict) -> None:
        if "name" not in cert or "bullets" not in cert:
            raise KeyError("Certificate must include 'name' and 'bullets'")
        if not isinstance(cert["name"], str):
            raise TypeError("Certificate 'name' must be a string")
        if not isinstance(cert["bullets"], list) or not cert["bullets"]:
            raise TypeError("Certificate 'bullets' must be a non-empty list of strings")
        if not all(isinstance(b, str) for b in cert["bullets"]):
            raise TypeError("All certificate bullets must be strings")
        link = cert.get("link")
        if link is not None and not isinstance(link, str):
            raise TypeError("Certificate 'link' must be a string or None")

    def _certificate_block(self, cert: Dict) -> str:
        description = cert["bullets"][0]
        if cert.get("link"):
            description += f" \\href{{{cert['link']}}}{{(See more here)}}"
        return f"\\item \\textbf{{{cert['name']}}} {description}"

    def add_certificates(
        self, certificates: List[Dict], select: Union[int, List[int], None] = None
    ) -> None:
        # Validate certificates
        for cert in certificates:
            self._validate_certificate(cert)

        # Handle selection
        if select is None:
            selected = certificates
        elif isinstance(select, int):
            selected = certificates[:select]
        elif isinstance(select, list):
            selected = [certificates[i] for i in select]
        else:
            raise ValueError("Invalid select argument")

        # Render each certificate item
        items_str = "\n".join(self._certificate_block(cert) for cert in selected)

        # Add section header and itemize block
        self.latex.tex += f"\n\\rSection{{{self.section_name}}}\n\\vspace{{-0.3em}}\n\\begin{{itemize}}\n\\itemsep -6pt {{}}\n{items_str}\n\\end{{itemize}}\n"


# ============================================================
# Interests Section
# ============================================================


class InterestsSection:
    """
    Render the INTERESTS section with hobbies and personal interests.

    Displays personal interests as comma-separated text. Unlike other sections,
    interests are simply listed as plain text without bullets or complex
    formatting. Multiple interest groups can be specified.

    Attributes
    ----------
    latex : LateX
        Reference to the LaTeX document builder instance.

    Examples
    --------
    >>> interests_section = InterestsSection(latex)
    >>> interests = [
    ...     {"items": ["Photography", "Hiking", "Reading science fiction"]},
    ...     {"items": ["Open source contribution", "Technical blogging"]}
    ... ]
    >>> interests_section.add_interests(interests)
    """

    def __init__(self, latex: LateX) -> None:
        """
        Initialize the InterestsSection.

        Parameters
        ----------
        latex : LateX
            LaTeX document builder instance.
        """
        self.latex = latex

    def add_interests(self, interests: List[Dict[str, List[str]]]) -> None:
        """
        Generate and add the INTERESTS section.

        Renders interests as comma-separated text. Each interest group
        is displayed on its own line.

        Parameters
        ----------
        interests : List[Dict[str, List[str]]]
            List of interest group dictionaries. Each must contain:
            - 'items' (List[str]): List of interest strings

        Raises
        ------
        KeyError
            If any interest group is missing the 'items' key.
        TypeError
            If 'items' is not a list of strings.

        Notes
        -----
        If the interests list is empty, the section is not rendered at all.
        This section does not support entry selection - all interests are
        always displayed.

        Examples
        --------
        >>> # Single group of interests
        >>> interests_data = [
        ...     {"items": ["Photography", "Hiking", "Cooking", "Chess"]}
        ... ]
        >>> interests_section.add_interests(interests_data)
        >>>
        >>> # Multiple groups (will be on separate lines)
        >>> interests_data = [
        ...     {"items": ["Outdoor activities", "Travel", "Photography"]},
        ...     {"items": ["Technical writing", "Mentoring"]}
        ... ]
        >>> interests_section.add_interests(interests_data)
        """
        if not interests:
            return

        self.latex.begin_section("INTERESTS", section_type="rSection")

        for group in interests:
            if "items" not in group:
                raise KeyError("Each interest entry must have an 'items' key")
            if not isinstance(group["items"], list) or not all(
                isinstance(i, str) for i in group["items"]
            ):
                raise TypeError("'items' must be a list of strings")

            # Render as comma-separated text
            self.latex.tex += ", ".join(group["items"]) + "\n\n"

        self.latex.end_section(section_type="rSection")
