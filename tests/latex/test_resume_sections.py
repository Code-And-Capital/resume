import pytest
from types import SimpleNamespace

from latex.core import LateX
from latex.resume_sections import (
    HeaderSection,
    SkillsSection,
    ExperienceSection,
    EducationSection,
    ProjectsSection,
    CertificatesSection,
    apply_selection,
    render_bullets,
)


# ======================================================
# Shared test infrastructure
# ======================================================


class MockLateX:
    """
    Minimal LaTeX mock that records rendered content
    and enforces correct section boundaries.
    """

    def __init__(self):
        self.tex = ""
        self.sections = []

    def begin_section(self, title, section_type=None):
        self.sections.append(("begin", title, section_type))

    def end_section(self, section_type=None):
        self.sections.append(("end", section_type))


@pytest.fixture
def latex():
    return LateX("test_doc")


@pytest.fixture
def mock_latex():
    return MockLateX()


# ======================================================
# apply_selection tests
# ======================================================


@pytest.fixture
def sample_items():
    return [{"id": i} for i in range(5)]


def test_apply_selection_none_returns_all(sample_items):
    result = apply_selection(sample_items, None, name="Test")
    assert result == sample_items


def test_apply_selection_int(sample_items):
    result = apply_selection(sample_items, 3, name="Test")
    assert result == sample_items[:3]


def test_apply_selection_int_negative_raises(sample_items):
    with pytest.raises(ValueError):
        apply_selection(sample_items, -1, name="Test")


def test_apply_selection_list_valid(sample_items):
    result = apply_selection(sample_items, [0, 2, 4], name="Test")
    assert result == [sample_items[0], sample_items[2], sample_items[4]]


def test_apply_selection_list_invalid_index(sample_items):
    with pytest.raises(IndexError):
        apply_selection(sample_items, [10], name="Test")


def test_apply_selection_list_non_int(sample_items):
    with pytest.raises(TypeError):
        apply_selection(sample_items, [1, "a"], name="Test")


def test_apply_selection_invalid_type(sample_items):
    with pytest.raises(TypeError):
        apply_selection(sample_items, "bad", name="Test")


# ======================================================
# render_bullets tests
# ======================================================


def test_render_bullets_basic():
    bullets = ["Item 1", "Item 2"]
    latex_block = render_bullets(bullets)
    assert "\\begin{itemize}" in latex_block
    assert "\\item Item 1" in latex_block
    assert "\\item Item 2" in latex_block
    assert "\\end{itemize}" in latex_block


def test_render_bullets_special_characters():
    bullets = ["50% increase", "Used & managed $budget"]
    latex_block = render_bullets(bullets)
    assert "50% increase" in latex_block
    assert "Used & managed $budget" in latex_block


# ======================================================
# HeaderSection tests
# ======================================================


@pytest.fixture
def header(latex):
    return HeaderSection(latex)


def test_header_with_linkedin(header, latex):
    header.add_header(
        first_name="Jane",
        last_name="Doe",
        phone="123-456-7890",
        location="Boston, MA",
        email="jane.doe@email.com",
        linkedin="https://linkedin.com/in/janedoe",
    )

    assert "\\name{Jane Doe}" in latex.tex
    assert "\\address{123-456-7890 \\\\ Boston, MA}" in latex.tex
    assert "\\href{mailto:jane.doe@email.com}{jane.doe@email.com}" in latex.tex
    assert "linkedin.com/in/janedoe" in latex.tex


def test_header_without_linkedin(header, latex):
    header.add_header(
        first_name="Jane",
        last_name="Doe",
        phone="123-456-7890",
        location="Boston, MA",
        email="jane.doe@email.com",
    )
    assert "linkedin.com" not in latex.tex


def test_header_spacing(header, latex):
    header.add_header(
        first_name="Jane",
        last_name="Doe",
        phone="123-456-7890",
        location="Boston, MA",
        email="jane.doe@email.com",
    )
    assert latex.tex.endswith("\n\n")


# ======================================================
# SkillsSection tests
# ======================================================


@pytest.fixture
def skills_section(latex):
    return SkillsSection(latex)


def test_add_skills_basic(skills_section, latex):
    skills = [
        {"category": "Languages", "items": ["Python", "SQL"]},
        {"category": "Tools", "items": ["Git", "Docker"]},
    ]
    skills_section.add_skills(skills)
    assert "\\begin{tabular}" in latex.tex
    assert "Languages & Python, SQL\\\\" in latex.tex
    assert "Tools & Git, Docker\\\\" in latex.tex
    assert "\\end{tabular}" in latex.tex


def test_skills_column_wrap_enabled(skills_section, latex):
    skills = [
        {
            "category": "Medical",
            "items": [
                "Venipuncture",
                "Comprehensive Adult physical examinations",
                "Excellent Collaboration with Supervising Physicians",
            ],
        }
    ]
    skills_section.add_skills(skills)
    assert "p{0.8\\textwidth}" in latex.tex


def test_invalid_skill_missing_keys(skills_section):
    with pytest.raises(KeyError):
        skills_section.add_skills([{"category": "Languages"}])


def test_invalid_skill_wrong_types(skills_section):
    with pytest.raises(TypeError):
        skills_section.add_skills([{"category": "Languages", "items": "Python"}])


# ======================================================
# ExperienceSection tests
# ======================================================


@pytest.fixture
def sample_experiences():
    return [
        {
            "role": "Engineer",
            "company": "ABC Corp",
            "start_date": "2020-01",
            "end_date": "2021-12",
            "location": "NY",
            "bullets": ["Did X", "Improved Y"],
        },
        {
            "role": "Manager",
            "company": "XYZ Inc",
            "start_date": "2019-01",
            "end_date": None,
            "location": "CA",
            "bullets": ["Led team", "Launched project"],
        },
    ]


def test_experience_renders_all(mock_latex, sample_experiences):
    section = ExperienceSection(mock_latex)
    section.add_experiences(sample_experiences)
    assert "Engineer" in mock_latex.tex
    assert "Manager" in mock_latex.tex
    assert ("begin", "PROFESSIONAL EXPERIENCE", "rSection") in mock_latex.sections


def test_experience_select_first_n(mock_latex, sample_experiences):
    section = ExperienceSection(mock_latex)
    section.add_experiences(sample_experiences, select=1)
    assert "Engineer" in mock_latex.tex
    assert "Manager" not in mock_latex.tex


def test_experience_select_by_index(mock_latex, sample_experiences):
    section = ExperienceSection(mock_latex)
    section.add_experiences(sample_experiences, select=[1])
    assert "Engineer" not in mock_latex.tex
    assert "Manager" in mock_latex.tex


def test_experience_validation_missing_field(mock_latex):
    section = ExperienceSection(mock_latex)
    bad = {"company": "ABC Corp", "start_date": "2020", "location": "NY"}
    with pytest.raises(KeyError):
        section.add_experiences([bad])


def test_experience_validation_bad_bullets(mock_latex, sample_experiences):
    sample_experiences[0]["bullets"] = "not-a-list"
    section = ExperienceSection(mock_latex)
    with pytest.raises(TypeError):
        section.add_experiences(sample_experiences)


# ======================================================
# EducationSection tests
# ======================================================


@pytest.fixture
def sample_educations():
    return [
        {
            "degree": "BSc",
            "subject": "Math",
            "school": "Univ A",
            "start_year": 2018,
            "end_year": 2022,
            "location": "Boston, MA",
            "bullets": ["Honors", "Coursework"],
        },
        {
            "degree": "MSc",
            "subject": "CS",
            "school": "Univ B",
            "start_year": 2022,
            "end_year": None,
            "location": "NY, NY",
        },
    ]


def test_education_renders_all(mock_latex, sample_educations):
    section = EducationSection(mock_latex)
    section.add_education(sample_educations)
    assert "BSc Math" in mock_latex.tex
    assert "MSc CS" in mock_latex.tex
    assert ("begin", "EDUCATION", "rSection") in mock_latex.sections


def test_education_select_first(mock_latex, sample_educations):
    section = EducationSection(mock_latex)
    section.add_education(sample_educations, select=1)
    assert "BSc Math" in mock_latex.tex
    assert "MSc CS" not in mock_latex.tex


def test_education_validation_bad_bullets(mock_latex, sample_educations):
    sample_educations[0]["bullets"] = "invalid"
    section = EducationSection(mock_latex)
    with pytest.raises(TypeError):
        section.add_education(sample_educations)


# ======================================================
# ProjectsSection tests
# ======================================================


@pytest.fixture
def sample_projects():
    return [
        {"name": "Proj1", "bullets": ["Do X"], "link": "http://link1.com"},
        {"name": "Proj2", "bullets": ["Do Y"], "link": None},
    ]


def test_projects_render_all(mock_latex, sample_projects):
    section = ProjectsSection(mock_latex)
    section.add_projects(sample_projects)
    assert "Proj1" in mock_latex.tex
    assert "Proj2" in mock_latex.tex
    assert ("begin", "PROJECTS", "rSection") in mock_latex.sections


def test_projects_validation_bad_bullets(mock_latex):
    section = ProjectsSection(mock_latex)
    bad = {"name": "Broken", "bullets": "not-a-list", "link": None}
    with pytest.raises(TypeError):
        section.add_projects([bad])


# ======================================================
# CertificatesSection tests
# ======================================================


@pytest.fixture
def sample_certificates():
    return [
        {"name": "Cert1", "bullets": ["Valid"], "link": "http://link.com"},
        {"name": "Cert2", "bullets": ["Valid2"], "link": None},
    ]


def test_certificates_render_all(mock_latex, sample_certificates):
    section = CertificatesSection(mock_latex)
    section.add_certificates(sample_certificates)
    assert "Cert1" in mock_latex.tex
    assert "Cert2" in mock_latex.tex
    assert ("begin", "CERTIFICATIONS", "rSection") in mock_latex.sections
