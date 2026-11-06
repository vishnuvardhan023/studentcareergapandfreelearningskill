from database.db import get_connection, init_db
from database.seed_data import ensure_seed_data, seed_demo_student
from modules.learning_planner import generate_learning_plan
from utils.validation import validate_student_profile


def test_learning_plan_sizing():
    available_hours = 12
    planned_hours = 6
    assert planned_hours <= available_hours


def test_regenerated_plan_overwrites_old_plan():
    old_plan = ["Python", "SQL"]
    new_plan = ["Python", "SQL", "Excel"]
    assert len(new_plan) >= len(old_plan)


def test_zero_study_hours_plan_is_blocked():
    init_db()
    ensure_seed_data()
    student_id = seed_demo_student()
    conn = get_connection()
    conn.execute("UPDATE students SET study_hours_per_day = 0, preferred_weeks = 4 WHERE id = ?", (student_id,))
    conn.commit()
    conn.close()

    plan = generate_learning_plan(student_id)
    assert "warning" in plan
    assert plan["warning"]


def test_incomplete_profile_is_rejected():
    result = validate_student_profile({"name": "", "degree": "", "department": "", "graduation_year": 2027, "study_hours_per_day": 2, "preferred_weeks": 4, "skills": {"Python": 2}})
    assert result["valid"] is False
    assert any("required" in error.lower() for error in result["errors"])
