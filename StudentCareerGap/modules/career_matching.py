import json

from database.db import get_connection
from utils.scoring import weighted_match


def load_job_roles():
    conn = get_connection()
    try:
        rows = conn.execute("SELECT * FROM job_roles ORDER BY id").fetchall()
        roles = []
        for row in rows:
            req_rows = conn.execute(
                "SELECT skill_name, required_level, weight, category FROM role_required_skills WHERE role_id = ? ORDER BY weight DESC",
                (row["id"],),
            ).fetchall()
            roles.append({
                "id": row["id"],
                "title": row["title"],
                "description": row["description"],
                "sample_note": row["sample_note"],
                "beginner_priorities": row["beginner_priorities"],
                "responsibilities": row["responsibilities"],
                "required_skills": [
                    {
                        "skill_name": item["skill_name"],
                        "required_level": item["required_level"],
                        "weight": item["weight"],
                        "category": item["category"],
                    }
                    for item in req_rows
                ],
            })
        return roles
    finally:
        conn.close()


def get_student_skill_map(student_id):
    conn = get_connection()
    try:
        rows = conn.execute("SELECT skill_name, skill_level FROM student_skills WHERE student_id = ?", (student_id,)).fetchall()
        return {row["skill_name"]: row["skill_level"] for row in rows}
    finally:
        conn.close()


def get_role_match_for_student(student_id, role):
    student_skills = get_student_skill_map(student_id)
    required_skills = role["required_skills"]
    match_percentage = weighted_match(student_skills, required_skills)

    matching_skills = []
    missing_skills = []
    weak_skills = []
    priority_skills = []

    for item in required_skills:
        skill_name = item["skill_name"]
        current = student_skills.get(skill_name, 0)
        required_level = item["required_level"]
        gap = required_level - current
        if gap <= 0:
            matching_skills.append(skill_name)
        else:
            missing_skills.append(skill_name)
            priority_skills.append(skill_name)
            if current <= 1:
                weak_skills.append(skill_name)

    priority_skills = sorted(priority_skills, key=lambda skill: -(next((item["weight"] for item in required_skills if item["skill_name"] == skill), 0)))
    summary = f"This role matches your current profile at {match_percentage:.0f}% and expects stronger performance in {', '.join(priority_skills[:3]) if priority_skills else 'core fundamentals'}."

    return {
        "title": role["title"],
        "description": role["description"],
        "match_percentage": round(match_percentage, 2),
        "matching_skills": matching_skills,
        "missing_skills": missing_skills,
        "weak_skills": weak_skills,
        "priority_skills": priority_skills,
        "summary": summary,
    }


def get_all_role_matches(student_id):
    roles = load_job_roles()
    matches = [get_role_match_for_student(student_id, role) for role in roles]
    ordered = sorted(matches, key=lambda item: item["match_percentage"], reverse=True)

    conn = get_connection()
    try:
        conn.execute("INSERT INTO ai_usage_logs (student_id, input_categories, methodology, recommendation_output, prompt_templates, source) VALUES (?, ?, ?, ?, ?, ?)", (
            student_id,
            "student_profile,job_requirements,skill_levels",
            "Weighted role matching with normalized proficiency capped at 1",
            json.dumps([{"role": role["title"], "match": role["match_percentage"]} for role in ordered]),
            "Why this role is recommended: role-matching explanation template; why this skill is important: skill-gap template",
            "rules",
        ))
        for role in ordered:
            conn.execute(
                "INSERT INTO recommendation_history (student_id, role_title, match_percentage, rationale) VALUES (?, ?, ?, ?)",
                (student_id, role["title"], role["match_percentage"], role["summary"]),
            )
        conn.commit()
    finally:
        conn.close()

    return ordered


def get_top_role_matches(student_id, limit=3):
    return get_all_role_matches(student_id)[:limit]
