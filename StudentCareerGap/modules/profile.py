import sqlite3

from database.db import get_connection
from utils.validation import clean_skill_level


def get_student_profile(student_id=None):
    conn = get_connection()
    try:
        if student_id is None:
            row = conn.execute("SELECT * FROM students ORDER BY id DESC LIMIT 1").fetchone()
        else:
            row = conn.execute("SELECT * FROM students WHERE id = ?", (student_id,)).fetchone()
        if not row:
            return None
        profile = dict(row)
        skill_rows = conn.execute(
            "SELECT skill_name, skill_level FROM student_skills WHERE student_id = ?",
            (profile["id"],),
        ).fetchall()
        for skill_row in skill_rows:
            profile[skill_row["skill_name"]] = skill_row["skill_level"]
        return profile
    finally:
        conn.close()


def load_student_profile_by_id(student_id):
    return get_student_profile(student_id)


def save_profile(profile):
    conn = get_connection()
    try:
        student_id = profile.get("id")
        if student_id:
            conn.execute(
                """
                UPDATE students
                SET name = ?, degree = ?, department = ?, academic_year = ?, graduation_year = ?,
                    preferred_role = ?, study_hours_per_day = ?, preferred_weeks = ?
                WHERE id = ?
                """,
                (
                    profile["name"],
                    profile["degree"],
                    profile["department"],
                    profile["academic_year"],
                    profile["graduation_year"],
                    profile["preferred_role"],
                    int(profile["study_hours_per_day"]),
                    int(profile["preferred_weeks"]),
                    student_id,
                ),
            )
            conn.commit()
            return student_id

        conn.execute(
            """
            INSERT INTO students (name, degree, department, academic_year, graduation_year, preferred_role, study_hours_per_day, preferred_weeks)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                profile["name"],
                profile["degree"],
                profile["department"],
                profile["academic_year"],
                int(profile["graduation_year"]),
                profile["preferred_role"],
                int(profile["study_hours_per_day"]),
                int(profile["preferred_weeks"]),
            ),
        )
        conn.commit()
        return conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    finally:
        conn.close()


def upsert_student_skills(student_id, skill_values):
    conn = get_connection()
    try:
        for skill_name, value in skill_values.items():
            level = clean_skill_level(value)
            conn.execute(
                """
                INSERT INTO student_skills (student_id, skill_name, skill_level, category)
                VALUES (?, ?, ?, 'General')
                ON CONFLICT(student_id, skill_name)
                DO UPDATE SET skill_level = excluded.skill_level, category = excluded.category
                """,
                (student_id, skill_name, level),
            )
        conn.commit()
    finally:
        conn.close()
