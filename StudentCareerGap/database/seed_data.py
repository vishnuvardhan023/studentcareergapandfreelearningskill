import json
from pathlib import Path

from database.db import get_connection

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"


def load_json_file(filename):
    with open(DATA_DIR / filename, "r", encoding="utf-8") as f:
        return json.load(f)


def ensure_seed_data():
    conn = get_connection()
    try:
        role_count = conn.execute("SELECT COUNT(*) FROM job_roles").fetchone()[0]
        resource_count = conn.execute("SELECT COUNT(*) FROM learning_resources").fetchone()[0]
        if role_count == 0:
            seed_roles()
        if resource_count == 0:
            seed_resources()
    finally:
        conn.close()


def seed_roles():
    roles_data = load_json_file("job_roles.json")
    conn = get_connection()
    try:
        for role in roles_data["roles"]:
            conn.execute(
                """
                INSERT INTO job_roles (title, description, sample_note, beginner_priorities, responsibilities, is_sample)
                VALUES (?, ?, ?, ?, ?, 1)
                """,
                (
                    role["title"],
                    role["description"],
                    role.get("sample_note", "Illustrative sample role profile."),
                    json.dumps(role.get("beginner_priorities", [])),
                    json.dumps(role.get("responsibilities", [])),
                ),
            )
            role_id = conn.execute("SELECT id FROM job_roles WHERE title = ?", (role["title"],)).fetchone()[0]
            for skill in role["required_skills"]:
                conn.execute(
                    """
                    INSERT INTO role_required_skills (role_id, skill_name, required_level, weight, category)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        role_id,
                        skill["skill"],
                        skill["required_level"],
                        skill["weight"],
                        skill.get("category", "General"),
                    ),
                )
        conn.commit()
    finally:
        conn.close()


def seed_resources():
    resources_data = load_json_file("learning_resources.json")
    conn = get_connection()
    try:
        for item in resources_data["resources"]:
            conn.execute(
                """
                INSERT INTO learning_resources (
                    skill_name, course_title, provider, learning_url, learning_type,
                    estimated_duration, difficulty, free_access_status, certificate_info, source_note
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    item["skill_name"],
                    item["course_title"],
                    item["provider"],
                    item["learning_url"],
                    item["learning_type"],
                    item["estimated_duration"],
                    item["difficulty"],
                    item["free_access_status"],
                    item["certificate_info"],
                    item.get("source_note", "Curated free resource"),
                ),
            )
        conn.commit()
    finally:
        conn.close()


def seed_demo_student():
    conn = get_connection()
    try:
        existing = conn.execute("SELECT id FROM students WHERE name = ?", ("Demo Student",)).fetchone()
        if existing:
            return existing[0]

        conn.execute(
            """
            INSERT INTO students (name, degree, department, academic_year, graduation_year, preferred_role, study_hours_per_day, preferred_weeks)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            ("Demo Student", "B.Sc. Computer Science", "Computer Science", "Third year", 2027, "Data Analyst", 2, 8),
        )
        student_id = conn.execute("SELECT id FROM students WHERE name = ?", ("Demo Student",)).fetchone()[0]
        sample_skills = {
            "Python": 2,
            "SQL": 1,
            "Excel": 3,
            "Statistics": 1,
            "Power BI": 0,
            "Data Analysis": 2,
            "Communication": 3,
            "Problem Solving": 3,
            "Git": 0,
        }
        for skill_name, level in sample_skills.items():
            conn.execute(
                "INSERT INTO student_skills (student_id, skill_name, skill_level, category) VALUES (?, ?, ?, ?)",
                (student_id, skill_name, level, "General"),
            )
        conn.commit()
        return student_id
    finally:
        conn.close()
