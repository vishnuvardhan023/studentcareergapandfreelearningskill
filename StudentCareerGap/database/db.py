import json
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "skillpath_ai.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                degree TEXT,
                department TEXT,
                academic_year TEXT,
                graduation_year INTEGER,
                preferred_role TEXT,
                study_hours_per_day INTEGER,
                preferred_weeks INTEGER,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS student_skills (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                skill_name TEXT NOT NULL,
                skill_level INTEGER NOT NULL,
                category TEXT,
                UNIQUE(student_id, skill_name)
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS job_roles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT UNIQUE,
                description TEXT,
                sample_note TEXT,
                beginner_priorities TEXT,
                responsibilities TEXT,
                is_sample INTEGER DEFAULT 1
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS role_required_skills (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role_id INTEGER NOT NULL,
                skill_name TEXT NOT NULL,
                required_level INTEGER NOT NULL,
                weight REAL NOT NULL,
                category TEXT,
                UNIQUE(role_id, skill_name)
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS learning_resources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                skill_name TEXT,
                course_title TEXT,
                provider TEXT,
                learning_url TEXT,
                learning_type TEXT,
                estimated_duration TEXT,
                difficulty TEXT,
                free_access_status TEXT,
                certificate_info TEXT,
                source_note TEXT
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS learning_plans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                role_title TEXT,
                summary TEXT,
                total_hours INTEGER,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS learning_tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                plan_id INTEGER NOT NULL,
                week_number INTEGER,
                topic TEXT,
                resource_name TEXT,
                learning_objectives TEXT,
                estimated_hours REAL,
                practical_assignment TEXT,
                completed INTEGER DEFAULT 0,
                progress_percentage INTEGER DEFAULT 0
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS progress_tracking (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                metric_name TEXT,
                metric_value REAL,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS recommendation_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                role_title TEXT,
                match_percentage REAL,
                recommendation_date TEXT DEFAULT CURRENT_TIMESTAMP,
                rationale TEXT
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS ai_usage_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER,
                input_categories TEXT,
                methodology TEXT,
                recommendation_output TEXT,
                prompt_templates TEXT,
                source TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        conn.commit()
    finally:
        conn.close()


if __name__ == "__main__":
    init_db()
    print(f"Database initialized: {DB_PATH}")
