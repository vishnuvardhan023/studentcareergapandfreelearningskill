from utils.scoring import weighted_match


def test_role_match_for_beginner_student():
    student_skills = {"Python": 2, "SQL": 1, "Excel": 3, "Statistics": 1}
    required_skills = [
        {"skill_name": "Python", "required_level": 3, "weight": 3},
        {"skill_name": "SQL", "required_level": 3, "weight": 3},
        {"skill_name": "Excel", "required_level": 3, "weight": 2},
        {"skill_name": "Statistics", "required_level": 3, "weight": 2},
    ]
    result = weighted_match(student_skills, required_skills)
    assert 0 < result < 100


def test_role_match_with_no_skills_is_zero():
    student_skills = {}
    required_skills = [{"skill_name": "Python", "required_level": 3, "weight": 5}]
    result = weighted_match(student_skills, required_skills)
    assert result == 0.0
