from database.db import get_connection

SKILL_CATALOG = [
    {"category": "Programming", "skills": ["Python", "Java", "C", "C++", "JavaScript"]},
    {"category": "Web Development", "skills": ["HTML", "CSS", "React", "Node.js"]},
    {"category": "Database", "skills": ["SQL", "MySQL", "MongoDB"]},
    {"category": "Data and AI", "skills": ["Statistics", "Excel", "Power BI", "Data Analysis", "Machine Learning"]},
    {"category": "Development Tools", "skills": ["Git", "GitHub", "Linux"]},
    {"category": "Soft Skills", "skills": ["Communication", "Problem Solving", "Teamwork", "Critical Thinking", "Time Management"]},
]


def get_skill_categories(student_id):
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT skill_name, skill_level, category FROM student_skills WHERE student_id = ? ORDER BY skill_name",
            (student_id,),
        ).fetchall()
        result = {item["category"]: {} for item in SKILL_CATALOG}
        for row in rows:
            skill_name = row["skill_name"]
            category = next((section["category"] for section in SKILL_CATALOG if skill_name in section["skills"]), "General")
            result.setdefault(category, {})[skill_name] = row["skill_level"]
        return result
    finally:
        conn.close()


def get_student_skill_summary(student_id):
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT skill_name, skill_level FROM student_skills WHERE student_id = ? ORDER BY skill_name",
            (student_id,),
        ).fetchall()
        return {row["skill_name"]: row["skill_level"] for row in rows}
    finally:
        conn.close()
