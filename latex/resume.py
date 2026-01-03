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
    EducationDataSource,
    ProjectsDataSource,
    CertificatesDataSource,
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

    def create_education(self, select):
        self.education_data = EducationDataSource(json_source=self.datasource)
        self.education_sec.add_education(self.education_data.data, select=select)

    def create_projects(self, select):
        self.project_data = ProjectsDataSource(json_source=self.datasource)
        self.projects_sec.add_projects(self.project_data.data, select=select)

    def create_certificates(self, select):
        self.certificates_data = CertificatesDataSource(json_source=self.datasource)
        self.certificates_sec.add_certificates(
            self.certificates_data.data, select=select
        )

    def create_resume(
        self,
        select_experiences=None,
        select_education=None,
        select_projects=None,
        select_certificates=None,
    ):
        self.create_document_head()
        self.create_header()
        self.begin_document()
        self.create_skills()
        self.create_experiences(select=select_experiences)
        self.create_education(select=select_education)
        self.create_projects(select=select_projects)
        self.create_certificates(select=select_certificates)
        self.end_document()
        self.create_pdf()
