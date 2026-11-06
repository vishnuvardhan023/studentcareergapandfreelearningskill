# SkillPath AI

SkillPath AI is a local-first career-readiness platform built for students preparing for placements. It helps students evaluate their current technical and soft-skill levels, compare them to role requirements, identify skill gaps, discover free learning resources, create learning plans, and track progress.

## Problem addressed

Students often do not know which skills are required for a preferred role, how far they are from those requirements, or where to learn for free. SkillPath AI fills that gap by using a transparent rule-based recommendation engine with explanation templates, without relying on external paid LLM APIs.

## Highlights

- Student profile and skill assessment forms
- Role-matching engine for 10 sample job roles
- Skill gap analysis with gap classification
- Free learning resource finder with direct links
- Personalized weekly schedule generator
- Progress tracker and report export
- Demo mode with a ready-made sample student
- SQLite persistence and modular design

## Tech stack

- Python
- Streamlit
- SQLite
- Plotly
- Pandas
- ReportLab

## Project structure

- `app.py` – main Streamlit application
- `database/` – SQLite database setup and seed logic
- `modules/` – skill, career, gap, resource, planner, report, and tracker modules
- `data/` – role and resource seed data
- `utils/` – utility scoring and explanation helpers
- `tests/` – unit tests for matching, scoring, and learning plan logic
- `docs/` – hackathon supporting documents

## Quick start

1. Create a virtual environment.
2. Install dependencies: `pip install -r requirements.txt`
3. Run the app: `streamlit run app.py`
4. Open the local Streamlit URL in the browser.

## Demo mode

Use the sidebar button `Load Demo Student` to instantly populate the profile with a sample student.

## Deployment

This app is prepared for Render using the included `render.yaml` configuration. It binds to `0.0.0.0` and reads the `$PORT` environment variable.

## Responsible AI note

The application does not use a paid or external AI API. Recommendations are generated from transparent role-matching rules and explanation templates to keep the app functional and reproducible.

## License

This project is for educational and hackathon use.
