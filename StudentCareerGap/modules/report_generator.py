import io
import csv

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from modules.career_matching import get_top_role_matches
from modules.gap_analysis import analyze_role_gaps
from modules.learning_planner import get_learning_plan_for_student
from modules.profile import get_student_profile
from modules.resource_finder import get_recommended_resources


def build_student_report(student_id):
    student = get_student_profile(student_id)
    if not student:
        return None

    roles = get_top_role_matches(student_id, 3)
    role_title = roles[0]["title"] if roles else student.get("preferred_role", "Career Goal")
    analysis = analyze_role_gaps(student_id, role_title)
    resources = get_recommended_resources(student_id)
    plan = get_learning_plan_for_student(student_id)

    summary = (
        f"{student['name']} is pursuing {student['degree']} in {student['department']} and aiming for {role_title}. "
        f"Career readiness is estimated at {analysis.get('readiness_score', 0):.0f}% based on the current skill profile."
    )

    return {
        "student": student,
        "top_roles": roles,
        "role_title": role_title,
        "analysis": analysis,
        "resources": resources,
        "plan": plan,
        "summary": summary,
    }


def download_report_csv(student_id):
    report = build_student_report(student_id)
    if not report:
        return b""

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Student Name", report["student"]["name"]])
    writer.writerow(["Degree", report["student"]["degree"]])
    writer.writerow(["Preferred Role", report["role_title"]])
    writer.writerow(["Career Readiness (%)", report["analysis"].get("readiness_score", 0)])
    writer.writerow([])
    writer.writerow(["Top Recommendation", "Match %"])
    for role in report["top_roles"]:
        writer.writerow([role["title"], role["match_percentage"]])
    return output.getvalue().encode("utf-8")


def download_report_pdf(student_id):
    report = build_student_report(student_id)
    if not report:
        return b""

    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    pdf.setTitle("SkillPath AI Report")
    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(50, 760, "SkillPath AI - Career Report")
    pdf.setFont("Helvetica", 11)
    lines = [
        f"Student: {report['student']['name']}",
        f"Degree: {report['student']['degree']} / {report['student']['department']}",
        f"Preferred Role: {report['role_title']}",
        f"Career Readiness: {report['analysis'].get('readiness_score', 0):.0f}%",
        "",
        "Top role recommendations:",
    ]
    for role in report["top_roles"][:3]:
        lines.append(f"- {role['title']}: {role['match_percentage']:.0f}%")

    y = 730
    for line in lines:
        pdf.drawString(50, y, line)
        y -= 18

    pdf.save()
    return buffer.getvalue()
