def normalize_proficiency(student_level, required_level):
    if required_level <= 0:
        return 0.0
    return min(float(student_level) / float(required_level), 1.0)


def weighted_match(student_skills, required_skills):
    total_weight = sum(item["weight"] for item in required_skills)
    if total_weight == 0:
        return 0.0
    weighted_total = 0.0
    for item in required_skills:
        skill_name = item["skill_name"]
        current = student_skills.get(skill_name, 0)
        weighted_total += item["weight"] * normalize_proficiency(current, item["required_level"])
    return (weighted_total / total_weight) * 100.0


def calculate_skill_gap(current_level, required_level):
    gap = required_level - current_level
    return max(0, gap)


def classify_gap(current_level, required_level):
    gap = required_level - current_level
    if gap <= 0:
        return "No gap"
    if current_level <= 1:
        return "Critical gap"
    if 2 <= current_level <= 3:
        return "Moderate gap"
    return "Minor gap"


def career_readiness_score(match_percentage):
    return max(0.0, min(100.0, float(match_percentage)))
