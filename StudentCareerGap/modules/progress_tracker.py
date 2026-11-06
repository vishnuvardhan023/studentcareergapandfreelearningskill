from database.db import get_connection


def get_progress_summary(student_id):
    conn = get_connection()
    try:
        latest_plan = conn.execute(
            "SELECT * FROM learning_plans WHERE student_id = ? ORDER BY id DESC LIMIT 1",
            (student_id,),
        ).fetchone()
        if not latest_plan:
            return None

        tasks = conn.execute(
            "SELECT * FROM learning_tasks WHERE plan_id = ? ORDER BY week_number",
            (latest_plan["id"],),
        ).fetchall()
        if not tasks:
            return None

        completed = sum(1 for task in tasks if task["completed"])
        total = len(tasks)
        overall = round((completed / total) * 100, 2) if total else 0
        weekly_progress = []
        for task in tasks:
            weekly_progress.append({
                "week": task["week_number"],
                "progress": task["progress_percentage"],
            })

        return {
            "completed_tasks": completed,
            "total_tasks": total,
            "overall_progress": overall,
            "weekly_progress": weekly_progress,
        }
    finally:
        conn.close()


def update_task_completion(task_id, completed):
    conn = get_connection()
    try:
        progress = 100 if completed else 0
        conn.execute(
            "UPDATE learning_tasks SET completed = ?, progress_percentage = ? WHERE id = ?",
            (1 if completed else 0, progress, task_id),
        )
        conn.commit()
    finally:
        conn.close()
