import pytest
from types import SimpleNamespace
from typing import List, Dict

from latex.resume_sections import (
    HeaderSection,
    SkillsSection,
    ListSection,
    ExperienceSection,
    EducationSection,
    ProjectsSection,
    CertificatesSection,
    InterestsSection,
)


# --------------------------
# Mock LaTeX class
# --------------------------
class MockLateX:
    def __init__(self):
        self.tex = ""
        self.sections_started = []
        self.sections_ended = []

    def begin_section(self, name, section_type=None):
        self.sections_started.append(name)
        self.tex += f"BEGIN:{name}\n"

    def end_section(self, section_type=None):
        self.sections_ended.append(True)
        self.tex += "END\n"


# --------------------------
# HeaderSection Tests
# --------------------------


def test_header_basic():
    latex = MockLateX()
    header = HeaderSection(latex)
    header.add_header(
        first_name="Alice",
        last_name="Doe",
        phone="+1-123",
        location="Test City",
        email="alice@example.com",
        linkedin="https://linkedin.com/alice",
    )
    assert "Alice Doe" in latex.tex
    assert "alice@example.com" in latex.tex
    assert "linkedin.com" in latex.tex


def test_header_no_linkedin():
    latex = MockLateX()
    header = HeaderSection(latex)
    header.add_header(
        first_name="Bob",
        last_name="Smith",
        phone="555-321",
        location="City",
        email="bob@example.com",
    )
    assert "bob@example.com" in latex.tex
    assert "href" in latex.tex  # mailto link
    assert "linkedin" not in latex.tex


def test_header_empty_strings():
    latex = MockLateX()
    header = HeaderSection(latex)
    header.add_header(first_name="", last_name="", phone="", location="", email="")
    assert "\\name{ }" in latex.tex


# --------------------------
# SkillsSection Tests
# --------------------------


def test_skills_basic():
    latex = MockLateX()
    skills = SkillsSection(latex)
    data = [{"category": "Lang", "items": ["Python", "Go"]}]
    skills.add_skills(data)
    assert "Lang" in latex.tex
    assert "Python" in latex.tex


def test_skills_empty_list():
    latex = MockLateX()
    skills = SkillsSection(latex)
    skills.add_skills([])
    assert latex.tex == ""  # section not rendered


def test_skills_validation():
    latex = MockLateX()
    skills = SkillsSection(latex)
    with pytest.raises(KeyError):
        skills.add_skills([{}])
    with pytest.raises(TypeError):
        skills.add_skills([{"category": 123, "items": ["x"]}])
    with pytest.raises(TypeError):
        skills.add_skills([{"category": "X", "items": [1]}])


def test_skills_multiple_calls():
    latex = MockLateX()
    skills = SkillsSection(latex)
    skills.add_skills([{"category": "Lang", "items": ["Python"]}])
    skills.add_skills([{"category": "Tools", "items": ["Git"]}])
    assert "Lang" in latex.tex and "Tools" in latex.tex


# --------------------------
# ListSection Helpers
# --------------------------


def test_apply_selection():
    items = [{"id": i} for i in range(5)]
    # None returns all
    assert ListSection.apply_selection(items, None, name="Test") == items
    # int selection
    assert ListSection.apply_selection(items, 3, name="Test") == items[:3]
    # list selection
    assert ListSection.apply_selection(items, [0, 2], name="Test") == [
        items[0],
        items[2],
    ]
    # negative int
    with pytest.raises(ValueError):
        ListSection.apply_selection(items, -1, name="Test")
    # invalid types
    with pytest.raises(TypeError):
        ListSection.apply_selection(items, "abc", name="Test")
    with pytest.raises(TypeError):
        ListSection.apply_selection(items, [0, "1"], name="Test")
    # out of bounds
    with pytest.raises(IndexError):
        ListSection.apply_selection(items, [10], name="Test")


def test_render_bullets():
    bullets = ["item1", "item2"]
    out = ListSection.render_bullets(bullets)
    assert "item1" in out and "item2" in out
    # empty bullets
    assert ListSection.render_bullets([]) == ""


def test_render_itemized_section():
    items = [{"text": "x"}, {"text": "y"}]

    def renderer(i):
        return f"\\item {i['text']}"

    out = ListSection.render_itemized_section(items, renderer)
    assert "\\item x" in out and "\\item y" in out
    assert out.startswith("\n\\begin{itemize}")
    assert out.endswith("\\end{itemize}")


# --------------------------
# ExperienceSection
# --------------------------


def make_experience():
    return [
        {
            "role": "Eng",
            "company": "C",
            "start_date": "Jan 2020",
            "end_date": "Dec 2021",
            "location": "City",
            "bullets": ["Did stuff"],
        },
        {
            "role": "Mgr",
            "company": "D",
            "start_date": "Jan 2022",
            "end_date": None,
            "location": "City2",
            "bullets": [],
        },
    ]


def test_experience_blocks():
    latex = MockLateX()
    exp_sec = ExperienceSection(latex)
    exps = make_experience()
    exp_sec.add_experiences(exps)
    # Should contain both roles and bullets
    assert "Eng" in latex.tex
    assert "Mgr" in latex.tex
    assert "Did stuff" in latex.tex


def test_experience_selection():
    latex = MockLateX()
    exp_sec = ExperienceSection(latex)
    exps = make_experience()
    exp_sec.add_experiences(exps, select=1)
    assert "Mgr" not in latex.tex


def test_experience_validation():
    latex = MockLateX()
    exp_sec = ExperienceSection(latex)
    bad_exp = [{"role": 1}]
    with pytest.raises(KeyError):
        exp_sec.add_experiences([{}])
    with pytest.raises(TypeError):
        exp_sec.add_experiences(bad_exp)


# --------------------------
# EducationSection
# --------------------------


def make_education():
    return [
        {
            "degree": "BSc",
            "subject": "CS",
            "school": "U",
            "start_year": 2010,
            "end_year": 2014,
            "location": "X",
            "bullets": ["Top student"],
        },
        {
            "degree": "MSc",
            "subject": "AI",
            "school": "V",
            "start_year": 2015,
            "end_year": None,
            "location": "Y",
            "bullets": [],
        },
    ]


def test_education_blocks():
    latex = MockLateX()
    edu_sec = EducationSection(latex)
    edu_sec.add_education(make_education())
    assert "BSc" in latex.tex
    assert "MSc" in latex.tex


def test_education_selection():
    latex = MockLateX()
    edu_sec = EducationSection(latex)
    edu_sec.add_education(make_education(), select=[0])
    assert "MSc" not in latex.tex


def test_education_validation():
    latex = MockLateX()
    edu_sec = EducationSection(latex)
    with pytest.raises(KeyError):
        edu_sec.add_education([{}])
    with pytest.raises(TypeError):
        edu_sec.add_education(
            [
                {
                    "degree": 1,
                    "subject": "X",
                    "school": "S",
                    "start_year": 2000,
                    "end_year": 2001,
                    "location": "L",
                }
            ]
        )


# --------------------------
# ProjectsSection
# --------------------------


def make_projects():
    return [
        {"name": "P1", "bullets": ["Do X"], "link": "http://a.com"},
        {"name": "P2", "bullets": ["Do Y"]},
    ]


def test_projects_basic():
    latex = MockLateX()
    proj_sec = ProjectsSection(latex)
    proj_sec.add_projects(make_projects())
    assert "P1" in latex.tex
    assert "P2" in latex.tex


def test_projects_validation():
    latex = MockLateX()
    proj_sec = ProjectsSection(latex)
    with pytest.raises(KeyError):
        proj_sec.add_projects([{}])
    with pytest.raises(TypeError):
        proj_sec.add_projects([{"name": 1, "bullets": ["x"]}])


def test_projects_selection():
    latex = MockLateX()
    proj_sec = ProjectsSection(latex)
    proj_sec.add_projects(make_projects(), select=1)
    assert "P2" not in latex.tex


# --------------------------
# CertificatesSection
# --------------------------


def make_certs():
    return [
        {"name": "Cert1", "bullets": ["Learned X"], "link": None},
        {"name": "Cert2", "bullets": ["Learned Y"], "link": "http://b.com"},
    ]


def test_certificates_basic():
    latex = MockLateX()
    cert_sec = CertificatesSection(latex)
    cert_sec.add_certificates(make_certs())
    assert "Cert1" in latex.tex
    assert "Cert2" in latex.tex


def test_certificates_validation():
    latex = MockLateX()
    cert_sec = CertificatesSection(latex)
    with pytest.raises(KeyError):
        cert_sec.add_certificates([{}])
    with pytest.raises(TypeError):
        cert_sec.add_certificates([{"name": 1, "bullets": ["x"]}])


def test_certificates_selection():
    latex = MockLateX()
    cert_sec = CertificatesSection(latex)
    cert_sec.add_certificates(make_certs(), select=1)
    assert "Cert2" not in latex.tex


# --------------------------
# InterestsSection
# --------------------------


def test_interests_basic():
    latex = MockLateX()
    interests_sec = InterestsSection(latex)
    data = [{"items": ["A", "B"]}, {"items": ["C"]}]
    interests_sec.add_interests(data)
    assert "A, B" in latex.tex
    assert "C" in latex.tex


def test_interests_validation():
    latex = MockLateX()
    interests_sec = InterestsSection(latex)
    with pytest.raises(KeyError):
        interests_sec.add_interests([{}])
    with pytest.raises(TypeError):
        interests_sec.add_interests([{"items": [1]}])


def test_interests_empty():
    latex = MockLateX()
    interests_sec = InterestsSection(latex)
    interests_sec.add_interests([])
    assert latex.tex == ""
