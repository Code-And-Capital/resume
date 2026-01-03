from latex.core import LateX
from latex.resume_sections import (
    HeaderSection,
    SkillsSection,
    EducationSection,
    ExperienceSection,
    ProjectsSection,
    CertificatesSection,
)
from data_loader.json_loader import JSONDataSource
from data_loader.section_loader import (
    HeaderDataSource,
    SkillsDataSource,
    ExperienceDataSource,
)


class Resume(LateX):
    """
    Resume class orchestrating all sections.
    """

    def __init__(self, file_path) -> None:
        super().__init__(tex_name="resume")

        self.datasource = JSONDataSource(file_path=file_path)
        self.datasource.load()

        self.header = HeaderSection(self)
        self.skills_sec = SkillsSection(self)
        self.education_sec = EducationSection(self)
        self.experience_sec = ExperienceSection(self)
        self.projects_sec = ProjectsSection(self)
        self.certificates_sec = CertificatesSection(self)

    def create_document_head(self) -> None:
        """Add document head with template, margins, footnote, and commands."""
        self.load_template("resume")
        self.margins()
        self.footnote_command()
        self.indent_command()
        self.no_indent_command()

    def create_header(self):
        self.header_data = HeaderDataSource(json_source=self.datasource)
        self.header.add_header(**self.header_data.data)

    def create_skills(self):
        self.skill_data = SkillsDataSource(json_source=self.datasource)
        self.skills_sec.add_skills(self.skill_data.data)

    def create_experiences(self, select):
        self.experience_data = ExperienceDataSource(json_source=self.datasource)
        self.experience_sec.add_experiences(self.experience_data.data, select=select)

    def create_resume(self, select_experiences=None):
        self.create_document_head()
        self.create_header()
        self.begin_document()
        self.create_skills()
        self.create_experiences(select=select_experiences)
        self.end_document()
        self.create_pdf()
