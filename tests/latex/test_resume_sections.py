import pytest
from latex.core import LateX
from latex.resume_sections import HeaderSection, SkillsSection, ExperienceSection
from types import SimpleNamespace


@pytest.fixture
def latex():
    return LateX("test_doc")


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
    assert (
        "\\href{https://linkedin.com/in/janedoe}{https://linkedin.com/in/janedoe}"
        in latex.tex
    )


def test_header_without_linkedin(header, latex):
    header.add_header(
        first_name="Jane",
        last_name="Doe",
        phone="123-456-7890",
        location="Boston, MA",
        email="jane.doe@email.com",
    )

    assert "\\name{Jane Doe}" in latex.tex
    assert "\\address{123-456-7890 \\\\ Boston, MA}" in latex.tex
    assert "\\href{mailto:jane.doe@email.com}{jane.doe@email.com}" in latex.tex

    # Ensure LinkedIn is not accidentally rendered
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


@pytest.fixture
def skills_section(latex):
    return SkillsSection(latex)


def test_add_skills_basic(skills_section, latex):
    skills = [
        {"category": "Languages", "items": ["Python", "SQL"]},
        {"category": "Tools", "items": ["Git", "Docker"]},
    ]

    skills_section.add_skills(skills)

    assert "\\section" not in latex.tex  # uses rSection
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

    # Ensure paragraph column is used for wrapping
    assert "p{0.8\\textwidth}" in latex.tex


def test_invalid_skill_missing_keys(skills_section):
    with pytest.raises(KeyError):
        skills_section.add_skills([{"category": "Languages"}])


def test_invalid_skill_wrong_types(skills_section):
    with pytest.raises(TypeError):
        skills_section.add_skills([{"category": "Languages", "items": "Python"}])


@pytest.fixture
def mock_latex():
    return SimpleNamespace(
        tex="",
        begin_section=lambda *args, **kwargs: None,
        end_section=lambda *args, **kwargs: None,
    )


@pytest.fixture
def sample_experiences():
    return [
        {
            "role": "Engineer",
            "company": "ABC Corp",
            "start_date": "Jan 2020",
            "end_date": "Dec 2021",
            "location": "NY",
            "bullets": ["Did X", "Improved Y"],
        },
        {
            "role": "Manager",
            "company": "XYZ Inc",
            "start_date": "Jan 2019",
            "end_date": None,
            "location": "CA",
            "bullets": ["Led team", "Launched project"],
        },
    ]


def test_add_all_experiences(mock_latex, sample_experiences):
    section = ExperienceSection(mock_latex)
    section.add_experiences(sample_experiences)
    assert "Engineer" in mock_latex.tex
    assert "Manager" in mock_latex.tex


def test_select_int(mock_latex, sample_experiences):
    section = ExperienceSection(mock_latex)
    section.add_experiences(sample_experiences, select=1)
    assert "Engineer" in mock_latex.tex
    assert "Manager" not in mock_latex.tex


def test_select_list(mock_latex, sample_experiences):
    section = ExperienceSection(mock_latex)
    section.add_experiences(sample_experiences, select=[1])
    assert "Engineer" not in mock_latex.tex
    assert "Manager" in mock_latex.tex


def test_invalid_select_type(mock_latex, sample_experiences):
    section = ExperienceSection(mock_latex)
    with pytest.raises(TypeError):
        section.add_experiences(sample_experiences, select="invalid")


def test_invalid_index(mock_latex, sample_experiences):
    section = ExperienceSection(mock_latex)
    with pytest.raises(IndexError):
        section.add_experiences(sample_experiences, select=[5])
