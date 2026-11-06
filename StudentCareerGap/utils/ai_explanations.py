def explain_recommendation(role_title, match_percentage, missing_skills):
    missing_list = ", ".join(missing_skills[:3]) if missing_skills else "core fundamentals"
    if match_percentage >= 80:
        return f"{role_title} is a strong fit because your current profile closely matches the role's expected skill profile. The main remaining work is to strengthen {missing_list}."
    if match_percentage >= 60:
        return f"{role_title} is a promising role for your profile. You already have a good foundation, and the next priorities are to improve {missing_list}."
    return f"{role_title} is still a realistic development target, but it requires a clearer focus on {missing_list} before the role can be considered a strong match."


def explain_gap(skill_name, current_level, required_level):
    gap = required_level - current_level
    if gap <= 0:
        return f"You already meet the expected level for {skill_name}."
    return f"{skill_name} has a gap of {gap} levels. You are currently at {current_level}/5, while the target level is {required_level}/5."


def explain_next_steps(skills):
    if not skills:
        return "Start by building the fundamentals in your top skill gaps before moving to role-specific tools."
    top = skills[:3]
    return f"Prioritize {', '.join(top)} first. Build a small project around these skills to move from theory to practical confidence."


def generate_ai_log_entry(student_id, input_categories, methodology, output, prompt_templates, source):
    return {
        "student_id": student_id,
        "input_categories": input_categories,
        "methodology": methodology,
        "recommendation_output": output,
        "prompt_templates": prompt_templates,
        "source": source,
    }
