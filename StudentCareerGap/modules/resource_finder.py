from database.db import get_connection
from modules.career_matching import get_top_role_matches


def get_all_resources():
    conn = get_connection()
    try:
        rows = conn.execute("SELECT * FROM learning_resources ORDER BY skill_name, provider").fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def get_recommended_resources(student_id):
    conn = get_connection()
    try:
        top_roles = get_top_role_matches(student_id, 1)
        if not top_roles:
            return []
        role = top_roles[0]
        priority_skills = set(role["missing_skills"]) | set(role["weak_skills"]) | set(role["priority_skills"])
        if not priority_skills:
            priority_skills = {"Python", "SQL", "Excel", "Communication"}

        placeholders = ', '.join(['?'] * len(priority_skills))
        query = f"SELECT * FROM learning_resources WHERE skill_name IN ({placeholders}) ORDER BY skill_name, provider"
        rows = conn.execute(query, tuple(priority_skills)).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()
