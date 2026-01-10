import pytest
from unittest.mock import MagicMock, patch, call

from latex.resume import Resume


# -------------------------
# Fixtures
# -------------------------


@pytest.fixture
def mock_json_datasource():
    with patch("latex.resume.JSONDataSource") as mock:
        instance = mock.return_value
        instance.load.return_value = None
        yield instance


@pytest.fixture
def resume_instance(mock_json_datasource):
    with patch.multiple(
        "latex.resume",
        HeaderSection=MagicMock(),
        SkillsSection=MagicMock(),
        ExperienceSection=MagicMock(),
        EducationSection=MagicMock(),
        ProjectsSection=MagicMock(),
        CertificatesSection=MagicMock(),
        InterestsSection=MagicMock(),
    ):
        r = Resume("fake.json")
        return r


@pytest.fixture(autouse=True)
def disable_latex_file_writes():
    with patch("latex.resume.LateX.load_template"):
        yield


# -------------------------
# Initialization
# -------------------------


def test_resume_initialization_loads_json(mock_json_datasource):
    Resume("fake.json")
    mock_json_datasource.load.assert_called_once()


def test_all_sections_initialized(resume_instance):
    assert resume_instance.header_sec
    assert resume_instance.skills_sec
    assert resume_instance.experience_sec
    assert resume_instance.education_sec
    assert resume_instance.projects_sec
    assert resume_instance.certificates_sec
    assert resume_instance.interests_sec


# -------------------------
# _render_section
# -------------------------


def test_render_section_lazy_loads_datasource(resume_instance):
    fake_ds = MagicMock()
    fake_ds.data = {"foo": "bar"}

    with patch.dict(
        Resume.SECTION_CLASSES,
        {"skills": (MagicMock(), MagicMock(return_value=fake_ds))},
        clear=False,
    ):
        resume_instance.skills_sec.add_skills = MagicMock()
        resume_instance._render_section("skills")

    assert "skills" in resume_instance._data_sources
    resume_instance.skills_sec.add_skills.assert_called_once_with(fake_ds.data)


def test_render_section_passes_select_for_selectable_sections(resume_instance):
    fake_ds = MagicMock()
    fake_ds.data = ["a", "b", "c"]

    with patch.dict(
        Resume.SECTION_CLASSES,
        {"experience": (MagicMock(), MagicMock(return_value=fake_ds))},
        clear=False,
    ):
        resume_instance.experience_sec.add_experiences = MagicMock()
        resume_instance._render_section("experience", select=2)

    resume_instance.experience_sec.add_experiences.assert_called_once_with(
        fake_ds.data, select=2
    )


def test_render_section_does_not_pass_select_for_fixed_sections(resume_instance):
    fake_ds = MagicMock()
    fake_ds.data = {"first_name": "A", "last_name": "B"}

    with patch.dict(
        Resume.SECTION_CLASSES,
        {"header": (MagicMock(), MagicMock(return_value=fake_ds))},
        clear=False,
    ):
        resume_instance.header_sec.add_header = MagicMock()
        resume_instance._render_section("header")

    resume_instance.header_sec.add_header.assert_called_once_with(**fake_ds.data)


# -------------------------
# Convenience methods
# -------------------------


def test_create_experiences_delegates(resume_instance):
    resume_instance._render_section = MagicMock()
    resume_instance.create_experiences(select=3)
    resume_instance._render_section.assert_called_once_with("experience", select=3)


def test_create_interests_delegates(resume_instance):
    resume_instance._render_section = MagicMock()
    resume_instance.create_interests()
    resume_instance._render_section.assert_called_once_with("interests")


# -------------------------
# create_resume
# -------------------------


def test_invalid_section_raises(resume_instance):
    with pytest.raises(ValueError):
        resume_instance.create_resume(sections_to_render=["bogus"])


def test_header_rendered_before_document_body(resume_instance):
    tracker = MagicMock()

    resume_instance.create_document_head = tracker.create_document_head
    resume_instance.create_header = tracker.create_header
    resume_instance.begin_document = tracker.begin_document
    resume_instance.end_document = tracker.end_document
    resume_instance.create_pdf = tracker.create_pdf
    resume_instance._render_section = tracker._render_section

    resume_instance.create_resume(sections_to_render=["header", "skills"])

    assert tracker.mock_calls.index(call.create_header()) < tracker.mock_calls.index(
        call.begin_document()
    )


def test_section_order_preserved(resume_instance):
    resume_instance.create_document_head = MagicMock()
    resume_instance.create_header = MagicMock()
    resume_instance.begin_document = MagicMock()
    resume_instance.end_document = MagicMock()
    resume_instance.create_pdf = MagicMock()
    resume_instance._render_section = MagicMock()

    resume_instance.create_resume(sections_to_render=["header", "skills", "projects"])

    resume_instance._render_section.assert_has_calls(
        [
            call("skills", select=None),
            call("projects", select=None),
        ]
    )


def test_selection_parameters_mapped_correctly(resume_instance):
    resume_instance.create_document_head = MagicMock()
    resume_instance.create_header = MagicMock()
    resume_instance.begin_document = MagicMock()
    resume_instance.end_document = MagicMock()
    resume_instance.create_pdf = MagicMock()
    resume_instance._render_section = MagicMock()

    resume_instance.create_resume(
        select_experiences=2,
        select_projects=[1],
        sections_to_render=["header", "experience", "projects"],
    )

    resume_instance._render_section.assert_has_calls(
        [
            call("experience", select=2),
            call("projects", select=[1]),
        ]
    )


def test_pdf_compilation_called(resume_instance):
    resume_instance.create_document_head = MagicMock()
    resume_instance.create_header = MagicMock()
    resume_instance.begin_document = MagicMock()
    resume_instance.end_document = MagicMock()
    resume_instance.create_pdf = MagicMock()
    resume_instance._render_section = MagicMock()

    resume_instance.create_resume(sections_to_render=["skills"])

    resume_instance.create_pdf.assert_called_once()
