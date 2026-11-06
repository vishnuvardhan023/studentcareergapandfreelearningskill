import json
from statistics import mean

import plotly.graph_objects as go

from database.db import get_connection
from modules.career_matching import load_job_roles
from modules.profile import get_student_profile
from utils.scoring import career_readiness_score, calculate_skill_gap, classify_gap


def analyze_role_gaps(student_id, role_title):
    conn = get_connection()
    try:
        role_row = conn.execute("SELECT * FROM job_roles WHERE title = ?", (role_title,)).fetchone()
        if not role_row:
            return {"gaps": [], "readiness_score": 0, "suggestions": []}

        req_rows = conn.execute(
            "SELECT skill_name, required_level, weight, category FROM role_required_skills WHERE role_id = ? ORDER BY weight DESC",
            (role_row["id"],),
        ).fetchall()
        student = get_student_profile(student_id)
        if not student:
            return {"gaps": [], "readiness_score": 0, "suggestions": []}

        skill_map = {}
        skill_rows = conn.execute("SELECT skill_name, skill_level FROM student_skills WHERE student_id = ?", (student_id,)).fetchall()
        for row in skill_rows:
            skill_map[row["skill_name"]] = row["skill_level"]

        gaps = []
        for req in req_rows:
            skill_name = req["skill_name"]
            current = skill_map.get(skill_name, 0)
            required_level = req["required_level"]
            gap_value = calculate_skill_gap(current, required_level)
            gaps.append({
                "skill": skill_name,
                "current_level": current,
                "required_level": required_level,
                "gap": gap_value,
                "priority": classify_gap(current, required_level),
                "weight": req["weight"],
            })

        readiness = 0
        if req_rows:
            total = sum(item["weight"] for item in req_rows)
            numerator = 0
            for req in req_rows:
                current = skill_map.get(req["skill_name"], 0)
                numerator += req["weight"] * min(current / req["required_level"], 1.0)
            readiness = (numerator / total) * 100

        priorities = sorted(gaps, key=lambda item: (item["gap"], item["weight"]), reverse=True)[:5]
        suggestions = [
            f"Strengthen {item['skill']} from {item['current_level']}/5 to {item['required_level']}/5 to close the {item['priority'].lower()} for this role."
            for item in priorities
        ]

        return {
            "role_title": role_title,
            "gaps": gaps,
            "readiness_score": round(career_readiness_score(readiness), 2),
            "suggestions": suggestions,
        }
    finally:
        conn.close()


def get_gap_summary(student_id, role_title):
    analysis = analyze_role_gaps(student_id, role_title)
    return analysis.get("gaps", [])


def plot_gap_charts(analysis, chart_type):
    skills = [item["skill"] for item in analysis.get("gaps", [])]
    current_levels = [item["current_level"] for item in analysis.get("gaps", [])]
    required_levels = [item["required_level"] for item in analysis.get("gaps", [])]

    if chart_type == "radar":
        fig = go.Figure(data=go.Scatterpolar(r=current_levels + [current_levels[0]], theta=skills + [skills[0]], fill='toself', name='Current'))
        fig.add_trace(go.Scatterpolar(r=required_levels + [required_levels[0]], theta=skills + [skills[0]], fill='toself', name='Required'))
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 5])),
            title=f"Skill radar for {analysis.get('role_title', 'Role')}"
        )
        return fig

    fig = go.Figure()
    fig.add_trace(go.Bar(x=skills, y=current_levels, name='Current level'))
    fig.add_trace(go.Bar(x=skills, y=required_levels, name='Required level'))
    fig.update_layout(title=f"Current vs required skill levels for {analysis.get('role_title', 'Role')}", barmode='group')
    return fig
