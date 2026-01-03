from __future__ import annotations
from typing import Any, Dict, Mapping, Tuple, Type
from data_loader.json_loader import JSONDataSource


# -----------------------------
# Validation Helpers
# -----------------------------


def _require_mapping(obj: Any, *, context: str) -> Mapping[str, Any]:
    if not isinstance(obj, Mapping):
        raise TypeError(f"{context} must be an object")
    return obj


def _require_list(obj: Any, *, context: str) -> list:
    if not isinstance(obj, list):
        raise TypeError(f"{context} must be a list")
    return obj


def _validate_required_fields(
    obj: Mapping[str, Any],
    required_fields: Dict[str, Type | Tuple[Type, ...]],
    *,
    context: str,
) -> None:
    for field, expected_type in required_fields.items():
        if field not in obj:
            raise KeyError(f"{context} missing required field '{field}'")
        if not isinstance(obj[field], expected_type):
            raise TypeError(
                f"{context} field '{field}' must be of type {expected_type}"
            )


# -----------------------------
# Base Section Data Source
# -----------------------------


class SectionDataSource:
    """
    Abstract base class for accessing and validating a top-level JSON section.

    Responsibilities
    ----------------
    - Retrieve a named top-level section from a loaded JSONDataSource
    - Enforce presence of the section
    - Delegate schema validation to subclasses

    Non-Responsibilities
    --------------------
    - No business logic
    - No transformations
    - No rendering decisions
    """

    #: Key of the top-level JSON section (must be overridden)
    section_key: str

    def __init__(self, json_source: JSONDataSource) -> None:
        """
        Initialize a section data source.

        Parameters
        ----------
        json_source : JSONDataSource
            Loaded JSON data source providing the raw document.
        """
        self._json_source = json_source

    @property
    def data(self) -> Any:
        """
        Return the validated section data.

        Raises
        ------
        KeyError
            If the section is missing.
        TypeError
            If the section structure is invalid.
        """
        root = self._json_source.data

        if self.section_key not in root:
            raise KeyError(f"Missing required section '{self.section_key}'")

        section = root[self.section_key]
        self.validate(section)
        return section

    def validate(self, section: Any) -> None:
        """
        Validate the section structure.

        Subclasses must override this method to enforce
        section-specific structural rules.

        Parameters
        ----------
        section : Any
            Raw section value extracted from the JSON document.
        """
        raise NotImplementedError


# -----------------------------
# Section Implementations
# -----------------------------


class HeaderDataSource(SectionDataSource):
    """Data source for the resume header section."""

    section_key = "header"

    REQUIRED_FIELDS = {
        "first_name": str,
        "last_name": str,
        "email": str,
        "phone": str,
        "location": str,
    }

    def validate(self, section: Any) -> None:
        header = _require_mapping(section, context="Header")
        _validate_required_fields(header, self.REQUIRED_FIELDS, context="Header")


class EducationDataSource(SectionDataSource):
    """Data source for education history."""

    section_key = "education"

    REQUIRED_FIELDS = {
        "school": str,
        "degree": str,
        "subject": str,
        "start_year": int,
        "end_year": int,
        "location": str,
        "bullets": list,
    }

    def validate(self, section: Any) -> None:
        entries = _require_list(section, context="Education")
        for entry in entries:
            edu = _require_mapping(entry, context="Education entry")
            _validate_required_fields(
                edu, self.REQUIRED_FIELDS, context="Education entry"
            )


class ExperienceDataSource(SectionDataSource):
    """Data source for professional experience."""

    section_key = "professional_experience"

    REQUIRED_FIELDS = {
        "company": str,
        "role": str,
        "start_date": str,
        "end_date": (str, type(None)),
        "location": str,
        "bullets": list,
    }

    def validate(self, section: Any) -> None:
        entries = _require_list(section, context="Professional experience")
        for entry in entries:
            exp = _require_mapping(entry, context="Experience entry")
            _validate_required_fields(
                exp, self.REQUIRED_FIELDS, context="Experience entry"
            )


class SkillsDataSource(SectionDataSource):
    """Data source for categorized skill listings."""

    section_key = "skills"

    def validate(self, section: Any) -> None:
        entries = _require_list(section, context="Skills")
        for entry in entries:
            skill = _require_mapping(entry, context="Skills entry")
            if "category" not in skill or not isinstance(skill["category"], str):
                raise KeyError("Skills entry missing valid 'category'")
            if "items" not in skill or not isinstance(skill["items"], list):
                raise KeyError("Skills entry missing valid 'items'")


class ProjectsDataSource(SectionDataSource):
    """Data source for project portfolio entries."""

    section_key = "projects"

    REQUIRED_FIELDS = {
        "name": str,
        "bullets": list,
        "link": str,
    }

    def validate(self, section: Any) -> None:
        entries = _require_list(section, context="Projects")
        for entry in entries:
            proj = _require_mapping(entry, context="Project entry")
            _validate_required_fields(
                proj, self.REQUIRED_FIELDS, context="Project entry"
            )


class CertificatesDataSource(SectionDataSource):
    """Data source for certifications and credentials."""

    section_key = "certificates"

    REQUIRED_FIELDS = {
        "name": str,
        "bullets": list,
        "link": str,
    }

    def validate(self, section: Any) -> None:
        entries = _require_list(section, context="Certificates")
        for entry in entries:
            cert = _require_mapping(entry, context="Certificate entry")
            _validate_required_fields(
                cert, self.REQUIRED_FIELDS, context="Certificate entry"
            )


class InterestsDataSource(SectionDataSource):
    """Data source for personal interests."""

    section_key = "interests"

    def validate(self, section: Any) -> None:
        entries = _require_list(section, context="Interests")
        for entry in entries:
            interest = _require_mapping(entry, context="Interest entry")
            if "items" not in interest or not isinstance(interest["items"], list):
                raise KeyError("Interest entry missing valid 'items'")
