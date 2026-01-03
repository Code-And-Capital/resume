from latex.core import LateX
from typing import Dict, List, Optional, Union


# ============================================================
# Shared Utilities
# ============================================================


def apply_selection(
    items: List[Dict],
    select: Union[int, List[int], None],
    *,
    name: str,
) -> List[Dict]:
    """
    Apply index-based selection to a list of dictionaries.

    This utility ensures consistent behavior for selecting a subset
    of items across different resume sections. It supports three selection modes:
    returning all items, returning the first N items, or returning specific items
    by their indices.

    Parameters
    ----------
    items : List[Dict]
        Full list of items to select from.
    select : int | List[int] | None
        Selection rule:
        - None: return all items
        - int: return first N items (e.g., 3 returns items[0:3])
        - List[int]: return items at given indices (e.g., [0, 2, 4])
    name : str
        Name of the section being selected from, used in error messages
        for better debugging (e.g., "Experience", "Education").

    Returns
    -------
    List[Dict]
        Subset of items after applying selection. Order is preserved
        when using list-based selection.

    Raises
    ------
    ValueError
        If `select` is a negative integer.
    TypeError
        If `select` is not int, List[int], or None, or if list elements
        are not all integers.
    IndexError
        If any index in a list selection is out of bounds (negative or
        >= len(items)).

    Examples
    --------
    >>> items = [{"id": 1}, {"id": 2}, {"id": 3}]
    >>> apply_selection(items, None, name="Test")
    [{"id": 1}, {"id": 2}, {"id": 3}]
    >>> apply_selection(items, 2, name="Test")
    [{"id": 1}, {"id": 2}]
    >>> apply_selection(items, [0, 2], name="Test")
    [{"id": 1}, {"id": 3}]
    """
    if select is None:
        return items

    if isinstance(select, int):
        if select < 0:
            raise ValueError(
                f"'{name}' selection count must be non-negative, got {select}"
            )
        return items[:select]

    if isinstance(select, list):
        if not all(isinstance(i, int) for i in select):
            raise TypeError(f"All {name} selection indices must be integers")
        if any(i < 0 or i >= len(items) for i in select):
            raise IndexError(
                f"{name} selection index out of bounds. "
                f"Valid range: 0-{len(items)-1}, got indices: {select}"
            )
        return [items[i] for i in select]

    raise TypeError(
        f"'{name}' select parameter must be int, List[int], or None, "
        f"got {type(select).__name__}"
    )


def render_bullets(bullets: List[str]) -> str:
    """
    Render a compact LaTeX itemize environment with bullets.

    The spacing between items is tightened (-6pt) for resume aesthetics,
    creating a more compact and professional appearance suitable for
    fitting more content on a single page.

    Parameters
    ----------
    bullets : List[str]
        Bullet point strings. Each string should be valid LaTeX text
        (special characters like &, %, $ should be escaped if needed).

    Returns
    -------
    str
        LaTeX string representing the itemized bullets, including
        begin/end itemize tags and spacing adjustments.

    Examples
    --------
    >>> bullets = ["Led team of 5 engineers", "Increased efficiency by 40%"]
    >>> print(render_bullets(bullets))
    \\begin{itemize}
    \\itemsep -6pt {}
    \\item Led team of 5 engineers
    \\item Increased efficiency by 40%
    \\end{itemize}
    """
    block = "\n\\begin{itemize}\n\\itemsep -6pt {}"
    for bullet in bullets:
        block += f"\n\\item {bullet}"
    block += "\n\\end{itemize}"
    return block


# ============================================================
# Header Section
# ============================================================


class HeaderSection:
    """
    Render the resume header section including name, contact info,
    and web presence (email, optional LinkedIn).

    This section uses LaTeX commands from the resume document class:
    - \\name{}: Renders the candidate's full name in large, bold text
    - \\address{}: Renders contact information in a structured format
    - \\href{}: Creates clickable hyperlinks for email and LinkedIn

    The header is typically the first section of a resume and contains
    essential contact information in a visually prominent layout.

    Attributes
    ----------
    latex : LateX
        Reference to the LaTeX document builder instance that accumulates
        the resume content.

    Examples
    --------
    >>> latex = LateX()
    >>> header = HeaderSection(latex)
    >>> header.add_header(
    ...     first_name="John",
    ...     last_name="Smith",
    ...     phone="+1-555-1234",
    ...     location="New York, NY",
    ...     email="john.smith@email.com"
    ... )
    """

    def __init__(self, latex: LateX) -> None:
        """
        Initialize a HeaderSection.

        Parameters
        ----------
        latex : LateX
            LaTeX document builder instance that will accumulate
            the rendered header content.
        """
        self.latex = latex

    def _add_name(self, full_name: str) -> None:
        """
        Render the full name of the candidate using LaTeX \\name command.

        Parameters
        ----------
        full_name : str
            Complete name of the candidate (typically first + last name).
        """
        self.latex.tex += f"\n\\name{{{full_name}}}"

    def _add_address_block(self, line1: str, line2: Optional[str] = None) -> None:
        """
        Render an address block (single or two-line).

        Creates a structured address block using the LaTeX \\address command.
        When two lines are provided, they are separated by \\\\ for proper
        line breaking in LaTeX.

        Parameters
        ----------
        line1 : str
            First line of address (e.g., phone number).
        line2 : Optional[str], default=None
            Optional second line (e.g., location or email).
        """
        if line2:
            self.latex.tex += f"\n\\address{{{line1} \\\\ {line2}}}"
        else:
            self.latex.tex += f"\n\\address{{{line1}}}"

    def _add_web_contact(self, email: str, linkedin: Optional[str]) -> None:
        """
        Render email and optional LinkedIn link as clickable hyperlinks.

        The email address is rendered as a mailto: hyperlink, and the
        LinkedIn URL (if provided) is rendered as a clickable web link.

        Parameters
        ----------
        email : str
            Email address of the candidate.
        linkedin : Optional[str]
            LinkedIn profile URL (optional). Should be a complete URL
            starting with https://.
        """
        email_link = f"\\href{{mailto:{email}}}{{{email}}}"
        if linkedin:
            self._add_address_block(
                email_link,
                f"\\href{{{linkedin}}}{{{linkedin}}}",
            )
        else:
            self._add_address_block(email_link)

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
        Render the complete resume header with all contact information.

        This is the main public method for adding a header. It combines
        name, phone, location, email, and optional LinkedIn into a
        professionally formatted header block.

        Layout order:
        1. Full name (large, bold)
        2. Phone number and location (same line)
        3. Email and optional LinkedIn (same line)

        Parameters
        ----------
        first_name : str
            Candidate's first name.
        last_name : str
            Candidate's last name.
        phone : str
            Phone number (e.g., "+1-555-0123" or "(555) 123-4567").
        location : str
            City and state/country (e.g., "San Francisco, CA").
        email : str
            Email address for contact.
        linkedin : Optional[str], default=None
            Full LinkedIn profile URL. Should start with https://.

        Examples
        --------
        >>> header.add_header(
        ...     first_name="Jane",
        ...     last_name="Doe",
        ...     phone="+1-555-0123",
        ...     location="Boston, MA",
        ...     email="jane.doe@example.com",
        ...     linkedin="https://linkedin.com/in/janedoe"
        ... )
        """
        self._add_name(f"{first_name} {last_name}")
        self._add_address_block(phone, location)
        self._add_web_contact(email, linkedin)
        self.latex.tex += "\n\n"


# ============================================================
# Skills Section
# ============================================================


class SkillsSection:
    """
    Render the SKILLS section in a two-column table format.

    Skills are displayed in a tabular layout with categories in the left
    column (bold) and comma-separated skill items in the right column.
    The right column uses automatic text wrapping for long skill lists.

    The table uses:
    - Left column: Bold category names (e.g., "Programming Languages")
    - Right column: 80% text width with automatic wrapping for skill items

    Attributes
    ----------
    latex : LateX
        Reference to the LaTeX document builder instance.

    Examples
    --------
    >>> skills = SkillsSection(latex)
    >>> skills.add_skills([
    ...     {
    ...         "category": "Programming Languages",
    ...         "items": ["Python", "JavaScript", "Go", "Rust"]
    ...     },
    ...     {
    ...         "category": "Frameworks",
    ...         "items": ["React", "Django", "FastAPI"]
    ...     }
    ... ])
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
        Validate a single skill entry for required fields and correct types.

        Parameters
        ----------
        skill : Dict[str, Union[str, List[str]]]
            Skill dictionary to validate.

        Raises
        ------
        KeyError
            If 'category' or 'items' keys are missing.
        TypeError
            If 'category' is not a string or 'items' is not a list of strings.
        """
        if "category" not in skill or "items" not in skill:
            raise KeyError("Each skill must have 'category' and 'items' keys")
        if not isinstance(skill["category"], str):
            raise TypeError("'category' must be a string")
        if not isinstance(skill["items"], list) or not all(
            isinstance(i, str) for i in skill["items"]
        ):
            raise TypeError("'items' must be a list of strings")

    def _skill_row(self, category: str, items: List[str]) -> str:
        """
        Render a single table row for a skill category.

        Parameters
        ----------
        category : str
            Skill category name (e.g., "Programming Languages").
        items : List[str]
            List of specific skills in this category.

        Returns
        -------
        str
            LaTeX table row with category and comma-separated items.
        """
        return f"\n{category} & {', '.join(items)}\\\\"

    def add_skills(self, skills: List[Dict[str, Union[str, List[str]]]]) -> None:
        """
        Render the complete SKILLS section with all skill categories.

        Creates a two-column table where each row represents a skill category
        with its associated items. The table uses special formatting for
        proper alignment and text wrapping.

        Parameters
        ----------
        skills : List[Dict[str, Union[str, List[str]]]]
            List of skill dictionaries. Each dictionary must have:
            - 'category' (str): Category name (e.g., "Tools & Technologies")
            - 'items' (List[str]): List of skills in that category

        Raises
        ------
        KeyError
            If any skill dictionary is missing required keys.
        TypeError
            If skill data types are incorrect.

        Examples
        --------
        >>> skills_data = [
        ...     {"category": "Languages", "items": ["Python", "Java"]},
        ...     {"category": "Databases", "items": ["PostgreSQL", "MongoDB"]}
        ... ]
        >>> skills_section.add_skills(skills_data)
        """
        if not skills:
            return

        for skill in skills:
            self._validate_skill(skill)

        self.latex.begin_section("SKILLS", section_type="rSection")

        # Create table with bold left column and wrapping right column
        table = (
            "\\begin{tabular}{ @{} >{\\bfseries}l @{\\hspace{6ex}} "
            "p{0.8\\textwidth} }"
        )

        for skill in skills:
            table += self._skill_row(skill["category"], skill["items"])

        table += "\n\\end{tabular}"
        self.latex.tex += table
        self.latex.end_section(section_type="rSection")


# ============================================================
# Experience Section
# ============================================================


class ExperienceSection:
    """
    Render the PROFESSIONAL EXPERIENCE section with work history entries.

    Each experience entry includes role, company, dates, location, and
    optional bullet points describing responsibilities and achievements.
    Supports optional selection to include only specific entries or limit
    the number of entries shown.

    Attributes
    ----------
    latex : LateX
        Reference to the LaTeX document builder instance.

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
    >>> exp_section.add_experiences(experiences, select=3)  # First 3 entries
    """

    def __init__(self, latex: LateX) -> None:
        """
        Initialize the ExperienceSection.

        Parameters
        ----------
        latex : LateX
            LaTeX document builder instance.
        """
        self.latex = latex

    def _validate_experience(self, exp: Dict) -> None:
        """
        Validate an experience dictionary for required fields and types.

        Parameters
        ----------
        exp : Dict
            Experience dictionary to validate.

        Raises
        ------
        KeyError
            If any required field is missing.
        TypeError
            If any field has an incorrect type.
        """
        required = {
            "role": str,
            "company": str,
            "start_date": str,
            "end_date": (str, type(None)),
            "location": str,
        }
        for k, expected_type in required.items():
            if k not in exp:
                raise KeyError(f"Experience entry missing required field '{k}'")
            if not isinstance(exp[k], expected_type):
                raise TypeError(
                    f"Experience field '{k}' must be of type {expected_type}, "
                    f"got {type(exp[k]).__name__}"
                )

        bullets = exp.get("bullets")
        if bullets is not None and (
            not isinstance(bullets, list)
            or not all(isinstance(b, str) for b in bullets)
        ):
            raise TypeError("Experience 'bullets' must be a list of strings or None")

    def _experience_block(self, exp: Dict) -> str:
        """
        Render a single experience entry with all details.

        Parameters
        ----------
        exp : Dict
            Experience dictionary with role, company, dates, location,
            and optional bullets.

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
            block += render_bullets(exp["bullets"])
        return block

    def add_experiences(
        self,
        experiences: List[Dict],
        select: Union[int, List[int], None] = None,
    ) -> None:
        """
        Render the PROFESSIONAL EXPERIENCE section with optional selection.

        Parameters
        ----------
        experiences : List[Dict]
            List of experience dictionaries. Each must contain:
            - 'role' (str): Job title
            - 'company' (str): Company name
            - 'start_date' (str): Start date (e.g., "Jan 2020")
            - 'end_date' (str | None): End date or None for current role
            - 'location' (str): Job location
            - 'bullets' (List[str] | None): Achievement bullets (optional)
        select : int | List[int] | None, default=None
            Selection mode:
            - None: include all experiences
            - int: include first N experiences
            - List[int]: include experiences at specific indices

        Raises
        ------
        KeyError
            If any experience entry is missing required fields.
        TypeError
            If any field has an incorrect type.
        ValueError, IndexError
            If selection parameters are invalid.

        Examples
        --------
        >>> # Include all experiences
        >>> exp_section.add_experiences(all_experiences)
        >>>
        >>> # Include only first 3 experiences
        >>> exp_section.add_experiences(all_experiences, select=3)
        >>>
        >>> # Include specific experiences by index
        >>> exp_section.add_experiences(all_experiences, select=[0, 2, 5])
        """
        selected = apply_selection(experiences, select, name="Experience")
        if not selected:
            return

        self.latex.begin_section("PROFESSIONAL EXPERIENCE", section_type="rSection")
        for exp in selected:
            self._validate_experience(exp)
            self.latex.tex += self._experience_block(exp)
        self.latex.end_section(section_type="rSection")


# ============================================================
# Education Section
# ============================================================


class EducationSection:
    """
    Render the EDUCATION section with academic credentials.

    Each education entry includes degree, subject/major, school name,
    years attended, location, and optional bullet points for honors,
    relevant coursework, or achievements.

    Attributes
    ----------
    latex : LateX
        Reference to the LaTeX document builder instance.

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
        self.latex = latex

    def _validate_education(self, edu: Dict) -> None:
        """
        Validate an education dictionary for required fields and types.

        Parameters
        ----------
        edu : Dict
            Education dictionary to validate.

        Raises
        ------
        KeyError
            If any required field is missing.
        TypeError
            If any field has an incorrect type.
        """
        required = {
            "degree": str,
            "subject": str,
            "school": str,
            "start_year": int,
            "end_year": (int, type(None)),
            "location": str,
        }
        for k, expected_type in required.items():
            if k not in edu:
                raise KeyError(f"Education entry missing required field '{k}'")
            if not isinstance(edu[k], expected_type):
                raise TypeError(
                    f"Education field '{k}' must be of type {expected_type}, "
                    f"got {type(edu[k]).__name__}"
                )

        bullets = edu.get("bullets")
        if bullets is not None and (
            not isinstance(bullets, list)
            or not all(isinstance(b, str) for b in bullets)
        ):
            raise TypeError("Education 'bullets' must be a list of strings or None")

    def _education_block(self, edu: Dict) -> str:
        """
        Render a single education entry with all details.

        Parameters
        ----------
        edu : Dict
            Education dictionary with degree, subject, school, years,
            location, and optional bullets.

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
            block += render_bullets(edu["bullets"])
        return block

    def add_education(
        self,
        educations: List[Dict],
        select: Union[int, List[int], None] = None,
    ) -> None:
        """
        Render the EDUCATION section with optional selection.

        Parameters
        ----------
        educations : List[Dict]
            List of education dictionaries. Each must contain:
            - 'degree' (str): Degree type (e.g., "Bachelor of Science")
            - 'subject' (str): Major/field of study
            - 'school' (str): Institution name
            - 'start_year' (int): Year started
            - 'end_year' (int | None): Year graduated or None if ongoing
            - 'location' (str): School location
            - 'bullets' (List[str] | None): Additional details (optional)
        select : int | List[int] | None, default=None
            Selection mode (see apply_selection for details).

        Raises
        ------
        KeyError
            If any education entry is missing required fields.
        TypeError
            If any field has an incorrect type.

        Examples
        --------
        >>> edu_data = [
        ...     {
        ...         "degree": "M.S.",
        ...         "subject": "Data Science",
        ...         "school": "MIT",
        ...         "start_year": 2020,
        ...         "end_year": 2022,
        ...         "location": "Cambridge, MA"
        ...     }
        ... ]
        >>> edu_section.add_education(edu_data)
        """
        selected = apply_selection(educations, select, name="Education")
        if not selected:
            return

        self.latex.begin_section("EDUCATION", section_type="rSection")
        for edu in selected:
            self._validate_education(edu)
            self.latex.tex += self._education_block(edu)
        self.latex.end_section(section_type="rSection")


# ============================================================
# Projects Section
# ============================================================


class ProjectsSection:
    """
    Render the PROJECTS section showcasing personal or professional projects.

    Each project includes a name, description (first bullet point), and
    optional link. Projects are displayed in an itemized list format,
    making them visually distinct from work experience.

    Attributes
    ----------
    latex : LateX
        Reference to the LaTeX document builder instance.

    Examples
    --------
    >>> proj_section = ProjectsSection(latex)
    >>> projects = [
    ...     {
    ...         "name": "Open Source ML Library",
    ...         "bullets": ["Built scalable machine learning toolkit"],
    ...         "link": "https://github.com/user/ml-lib"
    ...     }
    ... ]
    >>> proj_section.add_projects(projects, select=5)
    """

    def __init__(self, latex: LateX) -> None:
        """
        Initialize the ProjectsSection.

        Parameters
        ----------
        latex : LateX
            LaTeX document builder instance.
        """
        self.latex = latex

    def _validate_project(self, proj: Dict) -> None:
        """
        Validate a project dictionary for required fields and types.

        Parameters
        ----------
        proj : Dict
            Project dictionary to validate.

        Raises
        ------
        KeyError
            If 'name' or 'bullets' keys are missing.
        TypeError
            If fields have incorrect types or 'bullets' is empty.
        """
        if "name" not in proj or "bullets" not in proj:
            raise KeyError("Project must include 'name' and 'bullets' keys")
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
        """
        Render a single project item.

        Uses the first bullet point as the main description and appends
        a hyperlink if provided.

        Parameters
        ----------
        proj : Dict
            Project dictionary with name, bullets, and optional link.

        Returns
        -------
        str
            LaTeX-formatted project item.
        """
        description = proj["bullets"][0]
        if proj.get("link"):
            description += f" \\href{{{proj['link']}}}{{(See more here)}}"
        return f"\n\\item \\textbf{{{proj['name']}}} {description}"

    def add_projects(
        self,
        projects: List[Dict],
        select: Union[int, List[int], None] = None,
    ) -> None:
        """
        Render the PROJECTS section with optional selection.

        Parameters
        ----------
        projects : List[Dict]
            List of project dictionaries. Each must contain:
            - 'name' (str): Project name
            - 'bullets' (List[str]): Project descriptions (first used as main)
            - 'link' (str | None): Optional URL to project (optional)
        select : int | List[int] | None, default=None
            Selection mode (see apply_selection for details).

        Raises
        ------
        KeyError
            If any project is missing required fields.
        TypeError
            If any field has an incorrect type.

        Examples
        --------
        >>> projects_data = [
        ...     {
        ...         "name": "E-commerce Platform",
        ...         "bullets": ["Built full-stack web application"],
        ...         "link": "https://example.com"
        ...     }
        ... ]
        >>> proj_section.add_projects(projects_data)
        """
        selected = apply_selection(projects, select, name="Project")
        if not selected:
            return

        self.latex.begin_section("PROJECTS", section_type="rSection")
        self.latex.tex += "\n\\begin{itemize}"
        for proj in selected:
            self._validate_project(proj)
            self.latex.tex += self._project_block(proj)
        self.latex.tex += "\n\\end{itemize}"
        self.latex.end_section(section_type="rSection")


# ============================================================
# Certificates Section
# ============================================================


class CertificatesSection:
    """
    Render the CERTIFICATIONS section with professional certifications.

    Each certification includes a name, description (first bullet point),
    and optional verification link. Certifications are displayed in an
    itemized list format similar to projects.

    Attributes
    ----------
    latex : LateX
        Reference to the LaTeX document builder instance.

    Examples
    --------
    >>> cert_section = CertificatesSection(latex)
    >>> certs = [
    ...     {
    ...         "name": "AWS Solutions Architect",
    ...         "bullets": ["Professional level certification"],
    ...         "link": "https://aws.amazon.com/verification/XXX"
    ...     }
    ... ]
    >>> cert_section.add_certificates(certs)
    """

    def __init__(self, latex: LateX) -> None:
        """
        Initialize the CertificatesSection.

        Parameters
        ----------
        latex : LateX
            LaTeX document builder instance.
        """
        self.latex = latex

    def _validate_certificate(self, cert: Dict) -> None:
        """
        Validate a certificate dictionary for required fields and types.

        Parameters
        ----------
        cert : Dict
            Certificate dictionary to validate.

        Raises
        ------
        KeyError
            If 'name' or 'bullets' keys are missing.
        TypeError
            If fields have incorrect types or 'bullets' is empty.
        """
        if "name" not in cert or "bullets" not in cert:
            raise KeyError("Certificate must include 'name' and 'bullets' keys")
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
        """
        Render a single certificate item.

        Uses the first bullet point as the main description and appends
        a verification hyperlink if provided.

        Parameters
        ----------
        cert : Dict
            Certificate dictionary with name, bullets, and optional link.

        Returns
        -------
        str
            LaTeX-formatted certificate item.
        """
        description = cert["bullets"][0]
        if cert.get("link"):
            description += f" \\href{{{cert['link']}}}{{(See more here)}}"
        return f"\n\\item \\textbf{{{cert['name']}}} {description}"

    def add_certificates(
        self,
        certificates: List[Dict],
        select: Union[int, List[int], None] = None,
    ) -> None:
        """
        Render the CERTIFICATIONS section with optional selection.

        Parameters
        ----------
        certificates : List[Dict]
            List of certificate dictionaries. Each must contain:
            - 'name' (str): Certification name
            - 'bullets' (List[str]): Certificate descriptions (first used as main)
            - 'link' (str | None): Optional verification URL (optional)
        select : int | List[int] | None, default=None
            Selection mode (see apply_selection for details).

        Raises
        ------
        KeyError
            If any certificate is missing required fields.
        TypeError
            If any field has an incorrect type.

        Examples
        --------
        >>> certs_data = [
        ...     {
        ...         "name": "Google Cloud Professional",
        ...         "bullets": ["Cloud architecture certification"],
        ...         "link": "https://google.com/verify/123"
        ...     }
        ... ]
        >>> cert_section.add_certificates(certs_data)
        """
        selected = apply_selection(certificates, select, name="Certificate")
        if not selected:
            return

        self.latex.begin_section("CERTIFICATIONS", section_type="rSection")
        self.latex.tex += "\n\\begin{itemize}"
        for cert in selected:
            self._validate_certificate(cert)
            self.latex.tex += self._certificate_block(cert)
        self.latex.tex += "\n\\end{itemize}"
        self.latex.end_section(section_type="rSection")
