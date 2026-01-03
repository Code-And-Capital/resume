from latex.core import LateX
from typing import Dict, List


class HeaderSection:
    """Handle header information: name, contact, and web contact."""

    def __init__(self, latex: LateX):
        self.latex = latex

    def add_name(self, firstname: str, lastname: str) -> None:
        self.latex.tex += f"\n\\name{{{firstname} {lastname}}}"

    def add_contact(self, phone: str, location: str) -> None:
        self.latex.tex += f"\n\\address{{{phone} \\\\ {location}}}"

    def add_web_contact(self, email: str, linkedin: str) -> None:
        self.latex.tex += (
            f"\n\\address{{\\href{{mailto:{email}}}{{{email}}} \\\\ "
            f"\\href{{{linkedin}}}{{{linkedin}}}}}"
            f"\n\n"
        )

    def add_full_header(
        self,
        first_name: str,
        last_name: str,
        phone: str,
        location: str,
        email: str,
        linkedin: str,
    ) -> None:
        self.add_name(first_name, last_name)
        self.add_contact(phone, location)
        self.add_web_contact(email, linkedin)


class SkillsSection:
    """Handle skills section in the resume."""

    def __init__(self, latex: LateX):
        self.latex = latex

    def skill_str(self, skill: Dict[str, List[str]]) -> None:
        category = skill["category"]
        items = skill["items"]
        return f"\n{category} & {', '.join(items)}\\\\"

    def add_skills(self, skills: List[Dict[str, List[str]]]):
        self.latex.begin_section("SKILLS", section_type="rSection")
        table = (
            "\\begin{tabular}{ @{} >{\\bfseries}l @{\\hspace{6ex}} "
            "p{0.8\\textwidth} }"
        )
        for skill in skills:
            table += self.skill_str(skill)
        table += "\n\\end{tabular}"
        self.latex.tex += table


class EducationSection:
    """Handle education section."""

    def __init__(self, latex: LateX):
        self.latex = latex

    def add_education(self, education_dict: Dict[str, Dict]) -> None:
        self.latex.begin_section("EDUCATION", section_type="rSection")
        for _, edu in education_dict.items():
            degree_subject = f"{edu['degree']} {edu['subject']}"
            year = f"{edu['year_start']} - {edu['year_end']}"
            row = (
                f"\n\\textbf{{{degree_subject}}} \\hfill {year}\\\\\n"
                f"{edu['school']} \\hfill \\textit{{{edu['location']}}}\n"
                "\\vspace{-0.5em}\n\\begin{itemize}\n\\itemsep -6pt {}"
            )
            for bullet in edu["bullet"]:
                row += f"\n\\item {bullet}"
            row += "\n\\end{itemize}"
            self.latex.tex += row
        self.latex.end_section("rSection")


class ExperienceSection:
    """Handle professional experience section."""

    def __init__(self, latex: LateX):
        self.latex = latex

    def add_experience(self, experience_dict: Dict[str, Dict]) -> None:
        self.latex.begin_section("PROFESSIONAL EXPERIENCE", section_type="rSection")
        for _, job in experience_dict.items():
            role = job["role"]
            company = job["company"]
            period = f"{job['month_start']} - {job['month_end']}"
            location = job["location"]

            row = f"\n\\textbf{{{role}}} \\hfill {period}\\\\\n{company} \\hfill \\textit{{{location}}}\n\\vspace{{-0.5em}}"
            if job.get("bullet"):
                row += "\n\\begin{itemize}\n\\itemsep -6pt {}"
                for bullet in job["bullet"]:
                    row += f"\n\\item {bullet}"
                row += "\n\\end{itemize}"
            self.latex.tex += row
        self.latex.end_section("rSection")


class ProjectsSection:
    """Handle projects section."""

    def __init__(self, latex: LateX):
        self.latex = latex

    def add_projects(self, projects_dict: Dict[str, Dict]) -> None:
        self.latex.begin_section("PROJECTS", section_type="rSection")
        self.latex.vspace(-1.75)
        for _, proj in projects_dict.items():
            row = f"\n\\item \\textbf{{{proj['name']}}} {{{proj['bullet'][0]} \\href{{{proj['link']}}}{{(See more here)}}}}"
            self.latex.tex += row
        self.latex.end_section("rSection")


class CertificatesSection:
    """Handle certificates section."""

    def __init__(self, latex: LateX):
        self.latex = latex

    def add_certificates(self, cert_dict: Dict[str, Dict]) -> None:
        self.latex.begin_section("CERTIFICATIONS", section_type="rSection")
        self.latex.vspace(-1.75)
        for _, cert in cert_dict.items():
            link = cert.get("link", "")
            row = f"\n\\item \\textbf{{{cert['name']}}} {{{cert['bullet'][0]} \\href{{{link}}}{{(See more here)}}}}"
            self.latex.tex += row
        self.latex.end_section("rSection")
