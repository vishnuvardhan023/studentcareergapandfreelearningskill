import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from database.db import init_db
from database.seed_data import ensure_seed_data
from modules.assessment import get_skill_categories, get_student_skill_summary
from modules.career_matching import get_all_role_matches, get_top_role_matches, load_job_roles
from modules.gap_analysis import analyze_role_gaps, get_gap_summary, plot_gap_charts
from modules.learning_planner import generate_learning_plan, get_learning_plan_for_student
from modules.profile import get_student_profile, save_profile, upsert_student_skills, load_student_profile_by_id
from modules.progress_tracker import get_progress_summary, update_task_completion
from modules.report_generator import build_student_report, download_report_csv, download_report_pdf
from modules.resource_finder import get_recommended_resources
from utils.ai_explanations import explain_recommendation, explain_gap, explain_next_steps
from utils.validation import validate_student_profile

st.set_page_config(page_title="SkillPath AI", page_icon="📘", layout="wide")


@st.cache_data
def get_skill_catalog():
    from modules.assessment import SKILL_CATALOG
    return SKILL_CATALOG


def init_app():
    init_db()
    ensure_seed_data()


init_app()


def sidebar_navigation():
    pages = [
        "Home Dashboard",
        "Student Profile",
        "Skill Assessment",
        "Career Recommendations",
        "Skill Gap Analysis",
        "Free Learning Finder",
        "Personalized Learning Plan",
        "Progress Tracker",
        "Download Reports",
        "About Project",
    ]
    return st.sidebar.radio("Navigation", pages, index=0)


def load_demo_student():
    from database.seed_data import seed_demo_student
    student_id = seed_demo_student()
    st.session_state["selected_student_id"] = student_id
    st.session_state["student_loaded"] = True
    st.success("Demo student loaded successfully.")
    st.rerun()


def get_selected_student_id():
    if "selected_student_id" not in st.session_state:
        profile = get_student_profile()
        if profile:
            st.session_state["selected_student_id"] = profile["id"]
        else:
            st.session_state["selected_student_id"] = None
    return st.session_state["selected_student_id"]


def render_home_dashboard():
    st.title("SkillPath AI")
    st.caption("Discover Your Skill Gaps. Learn for Free. Become Career Ready.")

    student = get_student_profile(get_selected_student_id())
    if not student:
        st.info("No student profile found yet. Add a profile or load the demo student.")
        return

    skill_summary = get_student_skill_summary(student["id"])
    top_roles = get_top_role_matches(student["id"], 3)
    readiness = top_roles[0]["match_percentage"] if top_roles else 0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Career Readiness", f"{readiness:.0f}%")
    col2.metric("Skills Assessed", len(skill_summary))
    col3.metric("Top Role", top_roles[0]["title"] if top_roles else "N/A")
    col4.metric("Study Hours/Day", student.get("study_hours_per_day", 0))

    st.subheader("Profile snapshot")
    left, right = st.columns(2)
    left.write(f"**Student:** {student['name']}")
    left.write(f"**Degree:** {student['degree']} / {student['department']}")
    left.write(f"**Academic Year:** {student['academic_year']}")
    left.write(f"**Preferred Role:** {student.get('preferred_role', 'Not set')}")
    right.write(f"**Preferred Learning Weeks:** {student.get('preferred_weeks', 0)}")
    right.write(f"**Graduation Year:** {student.get('graduation_year', 'N/A')}")
    right.write(f"**Available Study Hours:** {student.get('study_hours_per_day', 0)} hours/day")

    if top_roles:
        st.subheader("Top role matches")
        for role in top_roles[:3]:
            with st.container():
                st.markdown(f"### {role['title']} — {role['match_percentage']:.0f}%")
                st.write(explain_recommendation(role['title'], role['match_percentage'], role['missing_skills']))

    st.subheader("Skill strength overview")
    skills_df = pd.DataFrame(
        [{"skill": k, "level": v} for k, v in skill_summary.items() if isinstance(v, (int, float))]
    )
    if not skills_df.empty:
        fig = px.bar(skills_df.sort_values("level", ascending=False), x="skill", y="level", color="level", title="Skill strengths")
        st.plotly_chart(fig, use_container_width=True)


def render_student_profile():
    st.title("Student Profile")
    st.caption("Personalize the platform to your current graduation track and preferred job target.")

    student = get_student_profile(get_selected_student_id())
    selected_id = get_selected_student_id()

    with st.form("profile_form"):
        st.subheader("Academic details")
        col1, col2 = st.columns(2)
        student_name = col1.text_input("Student name or nickname", value=student["name"] if student else "")
        degree = col1.text_input("Degree", value=student["degree"] if student else "")
        department = col1.text_input("Department", value=student["department"] if student else "")
        academic_year = col1.selectbox("Current academic year", ["First year", "Second year", "Third year", "Fourth year", "Graduate"], index=0 if not student else ["First year", "Second year", "Third year", "Fourth year", "Graduate"].index(student.get("academic_year", "First year")))
        graduation_year = col2.number_input("Graduation year", min_value=2025, max_value=2035, value=int(student["graduation_year"]) if student and student.get("graduation_year") else 2028)
        preferred_role = col2.text_input("Preferred job role", value=student.get("preferred_role", "") if student else "")
        study_hours = col2.number_input("Available study hours per day", min_value=0, max_value=12, value=int(student["study_hours_per_day"]) if student else 2)
        preferred_weeks = col2.number_input("Preferred learning duration (weeks)", min_value=1, max_value=40, value=int(student["preferred_weeks"]) if student else 8)

        st.subheader("Technical skills")
        skills = get_skill_catalog()
        skill_values = {}
        for category in skills:
            st.write(f"**{category['category']}**")
            for skill in category["skills"]:
                skill_values[skill] = st.slider(skill, 0, 5, value=int(student.get(skill, 0)) if student and student.get(skill) is not None else 0, key=f"profile_{skill}")

        submitted = st.form_submit_button("Save profile")

    if submitted:
        profile_data = {
            "id": selected_id,
            "name": student_name,
            "degree": degree,
            "department": department,
            "academic_year": academic_year,
            "graduation_year": graduation_year,
            "preferred_role": preferred_role,
            "study_hours_per_day": int(study_hours),
            "preferred_weeks": int(preferred_weeks),
            "skills": skill_values,
        }
        result = validate_student_profile(profile_data)
        if result["valid"]:
            student_id = save_profile(profile_data)
            upsert_student_skills(student_id, skill_values)
            st.session_state["selected_student_id"] = student_id
            st.success("Profile saved successfully.")
        else:
            for err in result["errors"]:
                st.warning(err)

    st.button("Load Demo Student", on_click=load_demo_student)


def render_skill_assessment():
    st.title("Skill Assessment")
    student = get_student_profile(get_selected_student_id())
    if not student:
        st.info("Create or load a student profile to begin the assessment.")
        return

    skills_by_category = get_skill_categories(student["id"])
    for category, skill_map in skills_by_category.items():
        st.subheader(category)
        data = [{"Skill": name, "Level": level} for name, level in skill_map.items()]
        if data:
            st.dataframe(pd.DataFrame(data), hide_index=True, use_container_width=True)

    st.subheader("Overall summary")
    summary = get_student_skill_summary(student["id"])
    if summary:
        fig = px.bar(pd.DataFrame({"Skill": list(summary.keys()), "Level": list(summary.values())}), x="Skill", y="Level", color="Level", title="Current skill snapshot")
        st.plotly_chart(fig, use_container_width=True)


def render_career_recommendations():
    st.title("Career Recommendations")
    student = get_student_profile(get_selected_student_id())
    if not student:
        st.info("Load a student profile to get role recommendations.")
        return

    roles = get_all_role_matches(student["id"])
    if not roles:
        st.warning("No role data available yet.")
        return

    for role in roles[:3]:
        st.subheader(f"{role['title']} — {role['match_percentage']:.0f}% match")
        st.write(role["summary"])
        st.write("**Already matching:** " + ", ".join(role["matching_skills"]) if role["matching_skills"] else "None")
        st.write("**Missing skills:** " + ", ".join(role["missing_skills"]) if role["missing_skills"] else "No major gaps")
        st.write("**Weak skills:** " + ", ".join(role["weak_skills"]) if role["weak_skills"] else "No weak gaps")
        st.write("**Priority skills:** " + ", ".join(role["priority_skills"]))

    st.subheader("Role comparison")
    compare_df = pd.DataFrame(
        [{"Role": item["title"], "Match %": round(item["match_percentage"], 1), "Estimated Readiness": round(item["match_percentage"], 1)} for item in roles]
    )
    fig = px.bar(compare_df, x="Role", y="Match %", color="Match %", title="Role matching comparison")
    st.plotly_chart(fig, use_container_width=True)


def render_skill_gap_analysis():
    st.title("Skill Gap Analysis")
    student = get_student_profile(get_selected_student_id())
    if not student:
        st.info("Add a profile first.")
        return

    roles = load_job_roles()
    role_titles = [role["title"] for role in roles]
    selected_role = st.selectbox("Select a role to analyze", role_titles)
    analysis = analyze_role_gaps(student["id"], selected_role)

    if analysis.get("gaps"):
        st.subheader(f"Gap analysis for {selected_role}")
        st.dataframe(pd.DataFrame(analysis["gaps"]), hide_index=True, use_container_width=True)
        st.metric("Career Readiness Score", f"{analysis['readiness_score']:.0f}%")
        st.write("**Actionable suggestions:**")
        for item in analysis["suggestions"]:
            st.write(f"- {item}")
        chart1, chart2 = st.columns(2)
        with chart1:
            st.plotly_chart(plot_gap_charts(analysis, "radar"), use_container_width=True)
        with chart2:
            st.plotly_chart(plot_gap_charts(analysis, "bar"), use_container_width=True)


def render_learning_finder():
    st.title("Free Learning Finder")
    student = get_student_profile(get_selected_student_id())
    if not student:
        st.info("Create a profile to discover learning resources.")
        return

    resources = get_recommended_resources(student["id"])
    if not resources:
        st.warning("No learning resources available yet for your current gaps.")
        return

    skill_filter = st.selectbox("Filter by skill", ["All"] + sorted({item["skill_name"] for item in resources}))
    difficulty_filter = st.selectbox("Filter by difficulty", ["All", "Beginner", "Intermediate", "Advanced"])

    filtered = []
    for item in resources:
        if skill_filter != "All" and item["skill_name"] != skill_filter:
            continue
        if difficulty_filter != "All" and item["difficulty"] != difficulty_filter:
            continue
        filtered.append(item)

    for item in filtered:
        st.markdown(f"### {item['course_title']}")
        st.write(f"**Skill:** {item['skill_name']} | **Provider:** {item['provider']} | **Type:** {item['learning_type']}")
        st.write(f"**Difficulty:** {item['difficulty']} | **Duration:** {item['estimated_duration']} | **Free access:** {item['free_access_status']}")
        st.write(f"**Certificate availability:** {item['certificate_info']}")
        st.markdown(f"[Open Course]({item['learning_url']})")
        st.markdown("---")


def render_learning_plan():
    st.title("Personalized Learning Plan")
    student = get_student_profile(get_selected_student_id())
    if not student:
        st.info("Load a profile before generating a schedule.")
        return

    plan = get_learning_plan_for_student(student["id"])
    if plan:
        st.success("Existing plan found. You can regenerate it below.")

    if st.button("Generate / Regenerate Learning Plan"):
        generated_plan = generate_learning_plan(student["id"])
        if generated_plan.get("warning"):
            st.warning(generated_plan["warning"])
        else:
            st.success("Learning plan generated successfully.")
        st.rerun()

    plan = get_learning_plan_for_student(student["id"])
    if not plan or not plan.get("tasks"):
        st.info("No plan available yet. Generate one based on your selected role and job gaps.")
        return

    for task in plan["tasks"]:
        with st.container():
            st.markdown(f"### Week {task['week']} — {task['topic']}")
            st.write(f"**Learning resource:** {task['resource_name']}")
            st.write(f"**Objectives:** {task['learning_objectives']}")
            st.write(f"**Estimated hours:** {task['estimated_hours']} | **Progress:** {task['progress_percentage']}%")
            completed = st.checkbox("Mark completed", value=bool(task["completed"]), key=f"task_{task['id']}")
            if completed != bool(task["completed"]):
                update_task_completion(task["id"], completed)
                st.rerun()
            st.write(f"**Practical assignment:** {task['practical_assignment']}")
            st.markdown("---")


def render_progress_tracker():
    st.title("Progress Tracker")
    student = get_student_profile(get_selected_student_id())
    if not student:
        st.info("No student selected.")
        return

    summary = get_progress_summary(student["id"])
    if not summary:
        st.info("Track your progress after generating a learning plan.")
        return

    col1, col2, col3 = st.columns(3)
    col1.metric("Completed Tasks", summary["completed_tasks"])
    col2.metric("Total Tasks", summary["total_tasks"])
    col3.metric("Overall Progress", f"{summary['overall_progress']:.0f}%")

    st.subheader("Weekly progress")
    week_df = pd.DataFrame(summary["weekly_progress"])
    if not week_df.empty:
        fig = px.line(week_df, x="week", y="progress", title="Weekly completion trend")
        st.plotly_chart(fig, use_container_width=True)


def render_download_reports():
    st.title("Download Reports")
    student = get_student_profile(get_selected_student_id())
    if not student:
        st.info("Create a profile before generating reports.")
        return

    report = build_student_report(student["id"])
    if not report:
        st.warning("No report data is available yet.")
        return

    st.write(report["summary"])
    st.download_button("Download CSV report", data=download_report_csv(student["id"]), file_name="skillpath_report.csv", mime="text/csv")
    st.download_button("Download PDF report", data=download_report_pdf(student["id"]), file_name="skillpath_report.pdf", mime="application/pdf")


def render_about_project():
    st.title("About Project")
    st.markdown("""
    SkillPath AI is a transparent, local-first placement-readiness dashboard for students.

    It helps students:
    - understand where they stand relative to a role
    - identify missing skills and weak areas
    - find free educational resources
    - build a weekly learning path
    - monitor progress and export a summary report

    This app uses a rule-based recommendation engine and explanation templates because no external paid AI service is required. All data is stored locally using SQLite.
    """)


def main():
    st.sidebar.markdown("## SkillPath AI")
    st.sidebar.caption("Discover Your Skill Gaps. Learn for Free. Become Career Ready.")
    if st.sidebar.button("Load Demo Student"):
        load_demo_student()

    page = sidebar_navigation()

    if page == "Home Dashboard":
        render_home_dashboard()
    elif page == "Student Profile":
        render_student_profile()
    elif page == "Skill Assessment":
        render_skill_assessment()
    elif page == "Career Recommendations":
        render_career_recommendations()
    elif page == "Skill Gap Analysis":
        render_skill_gap_analysis()
    elif page == "Free Learning Finder":
        render_learning_finder()
    elif page == "Personalized Learning Plan":
        render_learning_plan()
    elif page == "Progress Tracker":
        render_progress_tracker()
    elif page == "Download Reports":
        render_download_reports()
    elif page == "About Project":
        render_about_project()


if __name__ == "__main__":
    main()
