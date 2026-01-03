import json
import pytest
from pathlib import Path
from data_loader.json_loader import JSONDataSource
from data_loader.section_loader import (
    HeaderDataSource,
    EducationDataSource,
    ExperienceDataSource,
    SkillsDataSource,
    ProjectsDataSource,
    CertificatesDataSource,
    InterestsDataSource,
    SectionDataSource
)

# -----------------------------
# Sample valid JSON (fake data)
# -----------------------------

VALID_JSON = {
    "header": {
        "first_name": "Alex",
        "last_name": "Johnson",
        "email": "alex.johnson@example.com",
        "phone": "+1-212-555-7890",
        "location": "New York, NY",
        "linkedin": "https://linkedin.com/in/alexjohnson"
    },
    "education": [
        {
            "school": "NY University",
            "degree": "BSc",
            "subject": "Computer Science",
            "start_year": 2015,
            "end_year": 2019,
            "location": "New York, NY",
            "bullets": ["Graduated with honors", "President of Coding Club"]
        },
        {
            "school": "MIT",
            "degree": "MSc",
            "subject": "Data Science",
            "start_year": 2020,
            "end_year": 2022,
            "location": "Cambridge, MA",
            "bullets": ["Thesis on NLP", "GPA: 4.0"]
        }
    ],
    "professional_experience": [
        {
            "company": "DataCorp",
            "role": "Data Engineer",
            "start_date": "2022-07",
            "end_date": None,
            "location": "New York, NY",
            "bullets": ["Built ETL pipelines", "Optimized SQL queries"],
            "tags": ["python", "sql", "aws"]
        },
        {
            "company": "AnalyticsHub",
            "role": "Junior Data Analyst",
            "start_date": "2019-08",
            "end_date": "2022-06",
            "location": "Boston, MA",
            "bullets": ["Performed exploratory data analysis", "Created dashboards in Tableau"],
            "tags": ["tableau", "excel", "python"]
        }
    ],
    "skills": [
        {"category": "Programming", "items": ["python", "java", "sql"]},
        {"category": "Data Tools", "items": ["tableau", "excel", "powerbi"]}
    ],
    "projects": [
        {
            "name": "Sales Forecast Model",
            "bullets": ["Implemented ARIMA and Prophet forecasting models"],
            "link": "https://github.com/alexjohnson/sales-forecast",
            "tags": ["python", "ml", "forecasting"]
        },
        {
            "name": "Customer Segmentation",
            "bullets": ["Applied k-means clustering to segment customer base"],
            "link": "https://github.com/alexjohnson/customer-segmentation",
            "tags": ["python", "ml", "analytics"]
        }
    ],
    "certificates": [
        {"name": "AWS Certified Data Analytics", "bullets": ["Demonstrated AWS data pipeline skills"], "link": "https://www.credly.com/badge/aws-data"},
        {"name": "Tableau Desktop Specialist", "bullets": ["Proficiency in Tableau Desktop"], "link": "https://www.credly.com/badge/tableau-desktop"}
    ],
    "interests": [
        {"items": ["hiking", "photography", "chess"]}
    ]
}

# -----------------------------
# Fixtures
# -----------------------------

@pytest.fixture
def tmp_json(tmp_path: Path):
    path = tmp_path / "resume.json"
    path.write_text(json.dumps(VALID_JSON), encoding="utf-8")
    return path

@pytest.fixture
def json_source(tmp_json):
    ds = JSONDataSource(tmp_json)
    ds.load()
    return ds

# -----------------------------
# Section DataSource Tests
# -----------------------------

def test_header_valid(json_source):
    header = HeaderDataSource(json_source).data
    assert header["first_name"] == "Alex"
    assert header["linkedin"].startswith("http")

def test_education_valid(json_source):
    edu = EducationDataSource(json_source).data
    assert isinstance(edu, list)
    assert edu[0]["school"] == "NY University"

def test_experience_valid(json_source):
    exp = ExperienceDataSource(json_source).data
    assert isinstance(exp, list)
    assert exp[0]["company"] == "DataCorp"

def test_skills_valid(json_source):
    skills = SkillsDataSource(json_source).data
    assert isinstance(skills, list)
    categories = [s["category"] for s in skills]
    assert "Programming" in categories

def test_projects_valid(json_source):
    projects = ProjectsDataSource(json_source).data
    assert isinstance(projects, list)
    assert projects[0]["name"] == "Sales Forecast Model"

def test_certificates_valid(json_source):
    certs = CertificatesDataSource(json_source).data
    assert isinstance(certs, list)
    assert certs[0]["name"] == "AWS Certified Data Analytics"

def test_interests_valid(json_source):
    interests = InterestsDataSource(json_source).data
    assert isinstance(interests, list)
    assert "hiking" in interests[0]["items"]

# -----------------------------
# Validation / Error Tests
# -----------------------------

def test_missing_section_raises(json_source):
    ds = SectionDataSource(json_source)
    ds.section_key = "nonexistent"
    with pytest.raises(KeyError):
        _ = ds.data

def test_header_missing_field(tmp_path):
    data = VALID_JSON.copy()
    del data["header"]["first_name"]
    path = tmp_path / "resume.json"
    path.write_text(json.dumps(data))
    ds = JSONDataSource(path)
    ds.load()
    header_ds = HeaderDataSource(ds)
    with pytest.raises(KeyError):
        _ = header_ds.data

def test_header_wrong_type(tmp_path):
    data = VALID_JSON.copy()
    data["header"]["first_name"] = 123
    path = tmp_path / "resume.json"
    path.write_text(json.dumps(data))
    ds = JSONDataSource(path)
    ds.load()
    header_ds = HeaderDataSource(ds)
    with pytest.raises(TypeError):
        _ = header_ds.data

def test_education_not_list(tmp_path):
    data = VALID_JSON.copy()
    data["education"] = {}
    path = tmp_path / "resume.json"
    path.write_text(json.dumps(data))
    ds = JSONDataSource(path)
    ds.load()
    edu_ds = EducationDataSource(ds)
    with pytest.raises(TypeError):
        _ = edu_ds.data

def test_experience_end_date_nullable(json_source):
    exp = ExperienceDataSource(json_source).data
    assert exp[0]["end_date"] is None

def test_skills_missing_category(tmp_path):
    data = VALID_JSON.copy()
    data["skills"][0].pop("category")
    path = tmp_path / "resume.json"
    path.write_text(json.dumps(data))
    ds = JSONDataSource(path)
    ds.load()
    skills_ds = SkillsDataSource(ds)
    with pytest.raises(KeyError):
        _ = skills_ds.data
