from utils.scoring import calculate_skill_gap, classify_gap, normalize_proficiency, weighted_match


def test_normalize_proficiency_caps_at_one():
    assert normalize_proficiency(5, 3) == 1.0
    assert normalize_proficiency(2, 3) == 2 / 3


def test_skill_gap_calculation():
    assert calculate_skill_gap(2, 3) == 1
    assert calculate_skill_gap(4, 3) == 0


def test_classify_gap_types():
    assert classify_gap(0, 3) == "Critical gap"
    assert classify_gap(2, 3) == "Moderate gap"
    assert classify_gap(4, 5) == "Minor gap"
    assert classify_gap(3, 3) == "No gap"


def test_weighted_match_formula():
    student_skills = {"Python": 3, "SQL": 1}
    required_skills = [
        {"skill_name": "Python", "required_level": 3, "weight": 10},
        {"skill_name": "SQL", "required_level": 3, "weight": 10},
    ]
    result = weighted_match(student_skills, required_skills)
    assert abs(result - 66.66666666666666) < 1e-9
