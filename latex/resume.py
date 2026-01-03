from typing import Union, List, Optional, Dict, Tuple, Type
from latex.core import LateX
from latex.resume_sections import (
    HeaderSection,
    SkillsSection,
    EducationSection,
    ExperienceSection,
    ProjectsSection,
    CertificatesSection,
    InterestsSection,
)
from data_loader.json_loader import JSONDataSource
from data_loader.section_loader import (
    HeaderDataSource,
    SkillsDataSource,
    ExperienceDataSource,
    EducationDataSource,
    ProjectsDataSource,
    CertificatesDataSource,
    InterestsDataSource,
)


class Resume(LateX):
    """
    High-level resume generator with dynamic section management.

    Orchestrates LaTeX document creation, data loading, section rendering,
    and PDF compilation from a structured JSON file. Provides fine-grained
    control over which sections to include and how many entries to show
    in variable-length sections.

    The class uses a registry pattern for section management, allowing
    extensibility and reducing code duplication through generic rendering logic.

    Attributes
    ----------
    SECTION_CLASSES : Dict[str, Tuple[Type, Type]]
        Registry mapping section names to their (SectionBuilder, DataSource) classes.
        This enables dynamic section instantiation and rendering.
    SECTIONS_WITH_SELECT : set
        Set of section names that support entry selection (e.g., limiting to
        first N items or selecting specific indices).
    datasource : JSONDataSource
        Primary data source containing all resume information loaded from JSON.
    header_sec : HeaderSection
        Section builder for contact information header.
    skills_sec : SkillsSection
        Section builder for skills table.
    experience_sec : ExperienceSection
        Section builder for professional experience.
    education_sec : EducationSection
        Section builder for education entries.
    projects_sec : ProjectsSection
        Section builder for project entries.
    certificates_sec : CertificatesSection
        Section builder for certifications.
    interests_sec : InterestsSection
        Section builder for interests/hobbies.
    _data_sources : Dict[str, Any]
        Cache of loaded data sources to avoid redundant parsing.
    _file_path : str
        Path to the source JSON file.

    Parameters
    ----------
    file_path : str
        Path to JSON file containing structured resume data.

    Raises
    ------
    FileNotFoundError
        If the specified JSON file does not exist.
    JSONDecodeError
        If the file contains invalid JSON syntax.
    KeyError
        If required data sections are missing from the JSON.

    Examples
    --------
    >>> # Generate complete resume
    >>> resume = Resume("my_resume.json")
    >>> resume.create_resume()
    >>>
    >>> # Generate targeted resume with specific sections
    >>> resume = Resume("my_resume.json")
    >>> resume.create_resume(
    ...     select_experiences=5,
    ...     select_projects=[0, 1, 3],
    ...     sections_to_render=["header", "skills", "experience", "projects"]
    ... )
    >>>
    >>> # Generate academic resume
    >>> resume = Resume("my_resume.json")
    >>> resume.create_resume(
    ...     select_experiences=2,
    ...     select_education=None,
    ...     select_projects=None,
    ...     sections_to_render=["header", "education", "experience", "projects"]
    ... )

    Notes
    -----
    The Resume class follows the Template Method pattern, where the overall
    structure is defined in `create_resume()` but individual sections can be
    customized through parameters and the section registry.
    """

    # Section registry mapping section names to (SectionClass, DataSourceClass)
    SECTION_CLASSES = {
        "header": (HeaderSection, HeaderDataSource),
        "skills": (SkillsSection, SkillsDataSource),
        "experience": (ExperienceSection, ExperienceDataSource),
        "education": (EducationSection, EducationDataSource),
        "projects": (ProjectsSection, ProjectsDataSource),
        "certificates": (CertificatesSection, CertificatesDataSource),
        "interests": (InterestsSection, InterestsDataSource),
    }

    # Sections that support selection of individual entries
    SECTIONS_WITH_SELECT = {"experience", "education", "projects", "certificates"}

    def __init__(self, file_path: str) -> None:
        """
        Initialize the Resume builder with data from a JSON file.

        Sets up the document, loads data, and initializes all section builders
        and data source caching.

        Parameters
        ----------
        file_path : str
            Path to JSON file containing structured resume data.
            Expected structure includes top-level keys for each section:
            header, skills, experiences, education, projects, certificates, interests.

        Raises
        ------
        FileNotFoundError
            If the specified JSON file does not exist.
        JSONDecodeError
            If the file contains invalid JSON syntax.
        """
        super().__init__(tex_name="resume")
        self._file_path = file_path

        # Load resume data from JSON
        self.datasource = JSONDataSource(file_path=file_path)
        self.datasource.load()

        # Initialize all section builders
        self.header_sec = HeaderSection(self)
        self.skills_sec = SkillsSection(self)
        self.experience_sec = ExperienceSection(self)
        self.education_sec = EducationSection(self)
        self.projects_sec = ProjectsSection(self)
        self.certificates_sec = CertificatesSection(self)
        self.interests_sec = InterestsSection(self)

        # Cache for loaded data sources to avoid redundant parsing
        self._data_sources: Dict[str, any] = {}

    # ===============================
    # Document preamble
    # ===============================
    def create_document_head(self) -> None:
        """
        Create the LaTeX document preamble with template and formatting commands.

        This method sets up the document structure before content begins:
        - Loads the resume LaTeX template (document class, packages)
        - Configures page margins for professional resume layout
        - Defines custom footnote formatting
        - Sets up indentation control commands

        These commands prepare the document for proper resume formatting with
        appropriate spacing, margins, and typographic controls.

        Notes
        -----
        This must be called before any content is added to the document.
        The method modifies the internal LaTeX string buffer.
        """
        self.load_template("resume")
        self.margins()
        self.footnote_command()
        self.indent_command()
        self.no_indent_command()

    # ===============================
    # Generic section rendering
    # ===============================
    def _render_section(
        self, section_name: str, select: Union[int, List[int], None] = None
    ) -> None:
        """
        Render a section dynamically using the section registry.

        This is the core rendering method that uses reflection and the
        SECTION_CLASSES registry to instantiate data sources and call
        the appropriate section builder methods. This approach eliminates
        code duplication across similar section rendering methods.

        Parameters
        ----------
        section_name : str
            Name of the section to render. Must be a key in SECTION_CLASSES.
        select : int | List[int] | None, default=None
            Optional selection parameter for sections that support it.
            - None: include all entries
            - int: include first N entries
            - List[int]: include entries at specific indices

        Raises
        ------
        KeyError
            If section_name is not in SECTION_CLASSES registry.
        AttributeError
            If the section instance doesn't have the expected method.
        TypeError, ValueError
            If data validation fails or select parameter is invalid.

        Notes
        -----
        This method uses lazy loading - data sources are only instantiated
        the first time a section is rendered, then cached for subsequent calls.
        """
        SectionClass, DataSourceClass = self.SECTION_CLASSES[section_name]

        # Lazy load and cache data source
        if section_name not in self._data_sources:
            self._data_sources[section_name] = DataSourceClass(
                json_source=self.datasource
            )

        section_data = self._data_sources[section_name].data
        section_instance = getattr(self, f"{section_name}_sec")

        # Map section names to their add methods
        method_name_map = {
            "header": "add_header",
            "skills": "add_skills",
            "experience": "add_experiences",
            "education": "add_education",
            "projects": "add_projects",
            "certificates": "add_certificates",
            "interests": "add_interests",
        }

        method_name = method_name_map[section_name]
        add_method = getattr(section_instance, method_name)

        # Call method with appropriate arguments based on section type
        if section_name in self.SECTIONS_WITH_SELECT:
            # Sections with entry selection support
            add_method(section_data, select=select)
        else:
            # Fixed sections (header, skills, interests)
            if section_name == "header":
                # Header unpacks data as keyword arguments
                add_method(**section_data)
            else:
                # Skills and interests pass data directly
                add_method(section_data)

    # ===============================
    # Section-specific convenience methods
    # ===============================
    def create_header(self) -> None:
        """
        Generate and add the resume header section.

        Renders the contact information header including name, phone,
        location, email, and optional LinkedIn profile.

        Raises
        ------
        KeyError
            If required header fields are missing from the data source.
        TypeError
            If header data fields have incorrect types.
        """
        self._render_section("header")

    def create_skills(self) -> None:
        """
        Generate and add the SKILLS section.

        Renders skills organized by category in a two-column table format.
        All skills are always included (no selection parameter).

        Raises
        ------
        KeyError
            If skills data is missing or improperly structured.
        TypeError
            If skills data has incorrect types.
        """
        self._render_section("skills")

    def create_experiences(self, select: Union[int, List[int], None] = None) -> None:
        """
        Generate and add the PROFESSIONAL EXPERIENCE section.

        Renders work experience entries with optional selection.

        Parameters
        ----------
        select : int | List[int] | None, default=None
            Selection mode:
            - None: include all experiences
            - int: include first N experiences
            - List[int]: include experiences at specific indices

        Raises
        ------
        KeyError
            If experience data is missing required fields.
        TypeError
            If experience data has incorrect types.
        ValueError, IndexError
            If selection parameters are invalid.

        Examples
        --------
        >>> resume.create_experiences()  # All experiences
        >>> resume.create_experiences(select=3)  # First 3
        >>> resume.create_experiences(select=[0, 2, 5])  # Specific ones
        """
        self._render_section("experience", select=select)

    def create_education(self, select: Union[int, List[int], None] = None) -> None:
        """
        Generate and add the EDUCATION section.

        Renders education entries with optional selection.

        Parameters
        ----------
        select : int | List[int] | None, default=None
            Selection mode (same as create_experiences).

        Raises
        ------
        KeyError
            If education data is missing required fields.
        TypeError
            If education data has incorrect types.
        ValueError, IndexError
            If selection parameters are invalid.

        Examples
        --------
        >>> resume.create_education()  # All education
        >>> resume.create_education(select=1)  # Highest degree only
        """
        self._render_section("education", select=select)

    def create_projects(self, select: Union[int, List[int], None] = None) -> None:
        """
        Generate and add the PROJECTS section.

        Renders project entries with optional selection.

        Parameters
        ----------
        select : int | List[int] | None, default=None
            Selection mode (same as create_experiences).

        Raises
        ------
        KeyError
            If project data is missing required fields.
        TypeError
            If project data has incorrect types.
        ValueError, IndexError
            If selection parameters are invalid.

        Examples
        --------
        >>> resume.create_projects(select=5)  # Top 5 projects
        >>> resume.create_projects(select=[0, 3, 7])  # Specific projects
        """
        self._render_section("projects", select=select)

    def create_certificates(self, select: Union[int, List[int], None] = None) -> None:
        """
        Generate and add the CERTIFICATIONS section.

        Renders certification entries with optional selection.

        Parameters
        ----------
        select : int | List[int] | None, default=None
            Selection mode (same as create_experiences).

        Raises
        ------
        KeyError
            If certificate data is missing required fields.
        TypeError
            If certificate data has incorrect types.
        ValueError, IndexError
            If selection parameters are invalid.

        Examples
        --------
        >>> resume.create_certificates()  # All certifications
        >>> resume.create_certificates(select=3)  # Most recent 3
        """
        self._render_section("certificates", select=select)

    def create_interests(self) -> None:
        """
        Generate and add the INTERESTS section.

        Renders personal interests or hobbies. All interests are always
        included (no selection parameter).

        Raises
        ------
        KeyError
            If interests data is missing or improperly structured.
        TypeError
            If interests data has incorrect types.
        """
        self._render_section("interests")

    # ===============================
    # Full resume generation
    # ===============================
    def create_resume(
        self,
        select_experiences: Union[int, List[int], None] = None,
        select_education: Union[int, List[int], None] = None,
        select_projects: Union[int, List[int], None] = None,
        select_certificates: Union[int, List[int], None] = None,
        sections_to_render: Optional[List[str]] = None,
    ) -> None:
        """
        Generate the complete resume document and compile to PDF.

        This is the main entry point for resume generation. It orchestrates
        the complete workflow:
        1. Create document preamble with formatting commands
        2. Add header with contact information (outside document body)
        3. Begin LaTeX document body
        4. Add requested sections with optional entry selection
        5. End document
        6. Compile LaTeX to PDF

        The method provides fine-grained control over:
        - Which sections to include
        - How many entries to show in each variable-length section
        - Which specific entries to include using index-based selection

        Parameters
        ----------
        select_experiences : int | List[int] | None, default=None
            Selection for professional experience entries.
            - None: all experiences
            - int: first N experiences
            - List[int]: experiences at specific indices
        select_education : int | List[int] | None, default=None
            Selection for education entries (same format as select_experiences).
        select_projects : int | List[int] | None, default=None
            Selection for project entries (same format as select_experiences).
        select_certificates : int | List[int] | None, default=None
            Selection for certification entries (same format as select_experiences).
        sections_to_render : List[str] | None, default=None
            List of section names to include in the resume. If None, all
            sections are included. Valid section names are:
            - "header"
            - "skills"
            - "experience"
            - "education"
            - "projects"
            - "certificates"
            - "interests"

        Raises
        ------
        ValueError
            If sections_to_render contains unknown section names.
        FileNotFoundError
            If the LaTeX template file is not found.
        subprocess.CalledProcessError
            If LaTeX compilation fails.
        KeyError, TypeError, ValueError, IndexError
            If data validation or selection fails for any section.

        Notes
        -----
        - The header section is always rendered first, before the document body
        - Skills and interests sections do not support entry selection
        - The PDF is created in the same directory as the LaTeX file
        - Section order in the output follows the order in sections_to_render

        Examples
        --------
        >>> # Generate complete resume with all sections and entries
        >>> resume = Resume("data.json")
        >>> resume.create_resume()
        >>>
        >>> # Generate targeted resume for job application
        >>> resume = Resume("data.json")
        >>> resume.create_resume(
        ...     select_experiences=3,
        ...     select_education=1,
        ...     select_projects=[0, 2, 5],
        ...     select_certificates=5,
        ...     sections_to_render=["header", "skills", "experience",
        ...                         "education", "projects"]
        ... )
        >>>
        >>> # Generate academic CV with all research and education
        >>> resume = Resume("data.json")
        >>> resume.create_resume(
        ...     select_experiences=[0, 2],  # Research positions only
        ...     select_education=None,       # All degrees
        ...     select_projects=None,        # All research projects
        ...     sections_to_render=["header", "education", "experience",
        ...                         "projects", "certificates"]
        ... )
        >>>
        >>> # Generate minimal resume with only essential sections
        >>> resume = Resume("data.json")
        >>> resume.create_resume(
        ...     select_experiences=5,
        ...     sections_to_render=["header", "skills", "experience"]
        ... )
        """
        # Initialize document preamble
        self.create_document_head()

        # Default to all sections if none specified
        if sections_to_render is None:
            sections_to_render = list(self.SECTION_CLASSES.keys())

        # Validate that all requested sections exist
        invalid = set(sections_to_render) - set(self.SECTION_CLASSES.keys())
        if invalid:
            raise ValueError(
                f"Unknown section(s) requested: {invalid}. "
                f"Valid sections are: {list(self.SECTION_CLASSES.keys())}"
            )

        # Map section names to their selection parameters
        section_select_map = {
            "experience": select_experiences,
            "education": select_education,
            "projects": select_projects,
            "certificates": select_certificates,
        }

        # Render header first (before document body) if requested
        if "header" in sections_to_render:
            self.create_header()
            # Remove header from the list so it's not rendered again
            sections_to_render = [s for s in sections_to_render if s != "header"]

        # Begin LaTeX document body
        self.begin_document()

        # Render remaining sections in specified order
        for section_name in sections_to_render:
            select_value = section_select_map.get(section_name, None)
            self._render_section(section_name, select=select_value)

        # End document and compile to PDF
        self.end_document()
        self.create_pdf()
