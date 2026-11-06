from database.db import get_connection
from modules.career_matching import get_top_role_matches
from modules.profile import get_student_profile
from modules.resource_finder import get_recommended_resources


def generate_learning_plan(student_id):
    conn = get_connection()
    try:
        top_roles = get_top_role_matches(student_id, 1)
        if not top_roles:
            return {"id": None, "role_title": "N/A", "summary": "No role available for planning.", "tasks": [], "warning": "No role information available."}

        student = get_student_profile(student_id)
        role_title = top_roles[0]["title"]
        resources = get_recommended_resources(student_id)
        priority_skills = top_roles[0]["priority_skills"][:6]

        daily_hours = int(student.get("study_hours_per_day", 0) if student else 0)
        preferred_weeks = int(student.get("preferred_weeks", 1) if student else 1)
        max_total_hours = daily_hours * preferred_weeks

        conn.execute("DELETE FROM learning_tasks WHERE plan_id IN (SELECT id FROM learning_plans WHERE student_id = ?)", (student_id,))
        conn.execute("DELETE FROM learning_plans WHERE student_id = ?", (student_id,))

        plan_id = conn.execute(
            "INSERT INTO learning_plans (student_id, role_title, summary, total_hours) VALUES (?, ?, ?, ?)",
            (student_id, role_title, f"Personalized plan for {role_title}.", 0),
        ).lastrowid

        tasks = []
        if max_total_hours <= 0:
            conn.commit()
            return {
                "id": plan_id,
                "role_title": role_title,
                "summary": f"Personalized plan for {role_title}. Study time is zero, so a plan needs your availability input.",
                "tasks": tasks,
                "warning": "Study hours are zero. Please update the profile before generating a schedule.",
            }

        task_count = max(1, len(priority_skills))
        per_task_budget = max_total_hours / task_count

        for week_num, skill_name in enumerate(priority_skills, start=1):
            resource = next((item for item in resources if item["skill_name"] == skill_name), None)
            resource_name = resource["course_title"] if resource else "Core practice exercises"
            objectives = f"Master {skill_name} fundamentals and practice with real exercises."
            practical_assignment = f"Build a short project using {skill_name} and document the outcome."
            estimated_hours = round(min(3.0, per_task_budget), 1)
            task_id = conn.execute(
                """
                INSERT INTO learning_tasks (plan_id, week_number, topic, resource_name, learning_objectives, estimated_hours, practical_assignment, completed, progress_percentage)
                VALUES (?, ?, ?, ?, ?, ?, ?, 0, 0)
                """,
                (plan_id, week_num, skill_name, resource_name, objectives, estimated_hours, practical_assignment),
            ).lastrowid
            tasks.append({
                "id": task_id,
                "week": week_num,
                "topic": skill_name,
                "resource_name": resource_name,
                "learning_objectives": objectives,
                "estimated_hours": estimated_hours,
                "practical_assignment": practical_assignment,
                "completed": False,
                "progress_percentage": 0,
            })

        total_hours = sum(task["estimated_hours"] for task in tasks)
        conn.execute("UPDATE learning_plans SET total_hours = ? WHERE id = ?", (total_hours, plan_id))
        conn.commit()
        return {
            "id": plan_id,
            "role_title": role_title,
            "summary": f"Personalized plan for {role_title}. Total planned hours stay within your declared availability.",
            "tasks": tasks,
            "warning": "Planned hours are capped to your profile's available study time.",
        }
    finally:
        conn.close()


def get_learning_plan_for_student(student_id):
    conn = get_connection()
    try:
        plan_row = conn.execute(
            "SELECT * FROM learning_plans WHERE student_id = ? ORDER BY id DESC LIMIT 1",
            (student_id,),
        ).fetchone()
        if not plan_row:
            return None
        tasks = conn.execute(
            "SELECT * FROM learning_tasks WHERE plan_id = ? ORDER BY week_number",
            (plan_row["id"],),
        ).fetchall()
        return {
            "id": plan_row["id"],
            "role_title": plan_row["role_title"],
            "summary": plan_row["summary"],
            "total_hours": plan_row["total_hours"],
            "tasks": [dict(task) for task in tasks],
        }
    finally:
        conn.close()
