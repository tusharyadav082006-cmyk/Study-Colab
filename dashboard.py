# modules/dashboard.py
from flask import Blueprint, request, jsonify

dashboard_bp = Blueprint("dashboard", __name__)

# -------------------------------------------
# MASTER MODULE LIST (Dashboard Item Details)
# -------------------------------------------
MODULES = {
    "user_management": {
        "id": "user_management",
        "title": "Unified Student & Faculty Management",
        "description": "Manage users, profiles, and access control.",
        "icon": "user-gear"
    },
    "attendance": {
        "id": "attendance",
        "title": "Attendance Monitoring System",
        "description": "Mark, track and check attendance records.",
        "icon": "calendar-check"
    },
    "lms": {
        "id": "lms",
        "title": "LMS Module",
        "description": "Notes, materials and assignment management.",
        "icon": "book-open"
    },
    "progress_report": {
        "id": "progress_report",
        "title": "Student Progress Report",
        "description": "Summary of marks, graphs, and attendance.",
        "icon": "chart-line"
    },
    "notifications": {
        "id": "notifications",
        "title": "Notification & Alerts",
        "description": "Real-time announcements & alerts.",
        "icon": "bell"
    },
    "chat": {
        "id": "chat",
        "title": "Group Collaboration Chat",
        "description": "Real-time group chat for students & faculty.",
        "icon": "messages"
    },
    "exams": {
        "id": "exams",
        "title": "Exam & Result Management",
        "description": "Exam schedule, marks entry, results.",
        "icon": "file-pen"
    },
    "calendar": {
        "id": "calendar",
        "title": "Academic & Event Calendar",
        "description": "Track events, lectures & exam dates.",
        "icon": "calendar-days"
    },
    "analytics": {
        "id": "analytics",
        "title": "Analytics Dashboard",
        "description": "Attendance, marks & user activity analytics.",
        "icon": "chart-bar"
    },
    "course_management": {
        "id": "course_management",
        "title": "Course / Syllabus Management",
        "description": "Update subjects, topics and units.",
        "icon": "layers"
    },
    "document_management": {
        "id": "document_management",
        "title": "Document & File Management",
        "description": "Upload / manage PDFs, notes & files.",
        "icon": "folder-open"
    },
    "storage_management": {
        "id": "storage_management",
        "title": "Storage Management",
        "description": "Cloud storage usage & admin control.",
        "icon": "database"
    },
    "task_management": {
        "id": "task_management",
        "title": "Task Management",
        "description": "Assign & track tasks for users.",
        "icon": "list-check"
    }
}

# -------------------------------------------
# ROLE → MODULE ACCESS CONFIG
# -------------------------------------------
ROLE_ACCESS = {
    "student": [
        "attendance",
        "lms",
        "progress_report",
        "notifications",
        "chat",
        "calendar",
        "document_management",
        "task_management"
    ],

    "faculty": [
        "attendance",
        "lms",
        "progress_report",
        "notifications",
        "chat",
        "calendar",
        "exams",
        "course_management",
        "document_management",
        "task_management"
    ],

    "admin": [
        "user_management",
        "attendance",
        "lms",
        "progress_report",
        "notifications",
        "chat",
        "exams",
        "calendar",
        "analytics",
        "course_management",
        "document_management",
        "storage_management",
        "task_management"
    ]
}

# -------------------------------------------
# API: RETURN MODULES BASED ON ROLE
# -------------------------------------------
@dashboard_bp.route("/modules", methods=["GET"])
def get_modules_by_role():
    role = request.args.get("role", "").lower()

    if role not in ROLE_ACCESS:
        return jsonify({"error": "Invalid role"}), 400

    allowed_module_ids = ROLE_ACCESS[role]

    # Build module details
    output = [MODULES[mid] for mid in allowed_module_ids if mid in MODULES]

    return jsonify({
        "role": role,
        "modules": output,
        "count": len(output)
    })
