def validate_student_profile(profile):
    errors = []
    if not profile.get("name", "").strip():
        errors.append("Student name is required.")
    if not profile.get("degree", "").strip():
        errors.append("Degree is required.")
    if not profile.get("department", "").strip():
        errors.append("Department is required.")
    if profile.get("graduation_year") is None:
        errors.append("Graduation year is required.")
    if profile.get("study_hours_per_day", 0) < 0:
        errors.append("Study hours cannot be negative.")
    if profile.get("preferred_weeks", 0) <= 0:
        errors.append("Preferred learning duration must be greater than zero.")

    skill_values = profile.get("skills", {})
    if not isinstance(skill_values, dict) or not skill_values:
        errors.append("At least one skill rating is required.")
    else:
        for skill, value in skill_values.items():
            try:
                numeric = int(value)
            except (TypeError, ValueError):
                errors.append(f"Skill score for {skill} must be numeric.")
                continue
            if numeric < 0 or numeric > 5:
                errors.append(f"Skill score for {skill} must be between 0 and 5.")

    return {"valid": not errors, "errors": errors}


def clean_skill_level(value):
    try:
        number = int(value)
    except (TypeError, ValueError):
        return 0
    return max(0, min(5, number))
