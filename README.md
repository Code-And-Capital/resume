# Resume Generator

A configurable, code-driven resume generator built with **Python** and **LaTeX**.  
This project allows you to define resume content in structured **JSON**, then render a clean, professional PDF using LaTeX with fine-grained control over section selection and ordering.

The core goal is reproducibility, customization, and separation of content from presentation.

## Features

- Define resume content entirely in JSON
- Programmatic selection of:
  - Professional experience
  - Education
  - Projects
  - Certificates
- LaTeX-quality typography via `pdflatex`
- Python API designed for scripting and automation
- Deterministic output (same input → same PDF)

---

## Project Structure (High-Level)

```

.
├── data_loader/
│   ├── json_loader.py      # Loader for JSON files
│   ├── section_loader.py   # Resume section loader
├── latex/
│   ├── core.py             # Core LaTeX class
│   ├── resume.py           # Core Resume class
│   ├── resume_sections.py  # Section renderers
├── templates/
│   └── resume.cls          # Resume LaTeX formatting
├── inputs/
│   └── dummy.json          # Example resume configuration
├── notebooks/
│   └── create_resume.ipynb # Example usage
├── output/
│   ├── resume.tex          # Generated LaTeX source
│   └── resume.pdf          # Final compiled resume
├── setup.sh                # Environment setup script
├── run_tests.sh            # Test runner
├── tests/
│   └── ...                 # Unit tests
└── README.md

````

The `output/` directory is created automatically if it does not exist.  
All generated artifacts are written there to keep inputs, templates, and outputs cleanly separated.

---

## Requirements

### System Dependencies

You **must** have a LaTeX distribution installed with `pdflatex` available on your PATH.

- **macOS**: MacTeX
- **Linux**: TeX Live (`texlive-full` or a minimal install that includes `pdflatex`)
- **Windows**: MiKTeX

Verify installation:

```bash
pdflatex --version
````

If this command fails, LaTeX is not installed correctly.

---

### Python

* Python **3.10+** recommended
* Virtual environment strongly encouraged

---

## Environment Setup

This project uses a shell script to create and validate the environment.

```bash
. ./setup.sh
```

**Important:**
The leading dot (`.`) is intentional. It ensures environment variables and virtual
environment activation persist in your current shell session.

The script typically:

* Creates or activates a virtual environment
* Installs required Python packages

If this script fails, fix the errors before proceeding.

---

## Resume Configuration (JSON Input)

All resume content is defined in a single JSON file.

A full example lives in `inputs/dummy.json`. Below is a minimal illustration:

```json
{
  "header": {
    "first_name": "Alice",
    "last_name": "Doe",
    "email": "alice.doe@example.com",
    "location": "Test City, TC"
  },
  "skills": [
    {
      "category": "Programming",
      "items": ["Python", "Java", "C++"]
    }
  ]
}
```

### JSON Design Principles

* **Explicit over implicit** — no hidden inference
* **Order matters** — bullets render in the order provided
* **Content-only** — no layout or formatting logic in JSON

If you feel tempted to add formatting rules to the JSON, that logic belongs in LaTeX, not here.

---

## Basic Usage

### Python API Example

```python
import os
from latex.resume import Resume

configs = os.path.join(
    os.path.abspath(
        os.path.join(os.path.dirname(os.path.realpath("__file__")), "..")
    ),
    "inputs",
    "dummy.json",
)

r = Resume(file_path=configs)

r.create_resume(
    select_experiences=3,
    select_education=2,
    select_projects=1,
    select_certificates=2,
)
```

### What This Does

* Loads resume content from the JSON file
* Selects the top *N* entries from each section
* Generates a LaTeX source file (`resume.tex`)
* Compiles a PDF using `pdflatex`

Both `resume.tex` and the final `resume.pdf` are written to the `output/` directory.

Selection is deterministic and preserves input order.

---

## LaTeX Integration (`pdflatex`)

This project relies on **external LaTeX compilation**, not Python-native PDF rendering.

### Compilation Pipeline

1. Python generates `output/resume.tex`
2. `pdflatex` is invoked as a subprocess
3. `output/resume.pdf` is produced
4. Intermediate LaTeX files may be cleaned up

### Why `pdflatex`?

* Industry standard
* Predictable output
* Excellent typography
* Easy to debug and version control

### Common Failure Modes

| Error                | Likely Cause                                |
| -------------------- | ------------------------------------------- |
| `pdflatex not found` | LaTeX not installed or not on PATH          |
| Compilation errors   | Invalid LaTeX syntax in templates           |
| Unicode errors       | Missing LaTeX packages (fonts or encodings) |

If LaTeX compilation fails, **inspect the `.log` file**. That is the authoritative source of truth.

---

## Testing

Tests validate:

* JSON schema handling
* Section selection logic
* LaTeX rendering safety
* Error handling

Run tests manually:

```bash
. ./run_tests.sh
```

If tests pass but LaTeX fails, the issue is almost certainly system-level rather than Python-level.

---

## Non-Goals

This project intentionally does **not**:

* Provide a GUI
* Automatically optimize resume content
* Perform NLP rewriting
* Abstract away LaTeX entirely

It is a **tool**, not a resume writer.

---

## Extending the Project

Reasonable extensions:

* Multiple LaTeX themes
* CI pipeline that builds PDFs

Anti-patterns:

* Silent error handling
* “Smart” inference that hides decisions

---

## Philosophy

Your resume is code:

* Versioned
* Tested
* Reproducible
* Explicit

If that framing feels uncomfortable, this project may not be the right tool.
