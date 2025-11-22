# modules/progress_report.py
from flask import Blueprint, request, jsonify

progress_bp = Blueprint("progress", __name__)

# ===========================================================
#   IN-MEMORY DATABASES (Replace with DB later)
# ===========================================================

# Marks stored per student:
# marks["rollno"] = [ {"subject":"Math", "marks":89}, ... ]
MARKS = {}

# Attendance imported from Attendance module:
# attendance["rollno"] = {"2025-01-12":"P", ...}
ATTENDANCE = {}

# Student registry with name/roll mapping:
STUDENTS = {
    # 101: "Tushar",
    # 102: "Aditi"
}


# ===========================================================
#   1️⃣ FACULTY / ADMIN — Upload Marks
# ===========================================================
@progress_bp.route("/upload_marks", methods=["POST"])
def upload_marks():
    data = request.json

    if data.get("role") == "student":
        return jsonify({"error": "Students cannot upload marks"}), 403

    rollno = data.get("rollno")
    subject = data.get("subject")
    marks = data.get("marks")

    if rollno is None or subject is None or marks is None:
        return jsonify({"error": "Missing fields"}), 400

    if rollno not in MARKS:
        MARKS[rollno] = []

    MARKS[rollno].append({"subject": subject, "marks": marks})

    return jsonify({
        "uploaded": True,
        "rollno": rollno,
        "subject": subject,
        "marks": marks
    })


# ===========================================================
#   2️⃣ MERGE ATTENDANCE FROM ATTENDANCE MODULE
# ===========================================================
def get_attendance_percentage(record):
    if not record:
        return 0
    total = len(record)
    present = sum(1 for x in record.values() if x == "P")
    return round((present / total) * 100, 2)


# ===========================================================
#   3️⃣ STUDENT / ADMIN / FACULTY — Get Full Report
# ===========================================================
@progress_bp.route("/report/<int:rollno>", methods=["GET"])
def get_report(rollno):
    # Name
    student_name = STUDENTS.get(rollno, f"Student-{rollno}")

    # Marks
    marks = MARKS.get(rollno, [])

    # Attendance imported from ATTENDANCE module
    attendance = ATTENDANCE.get(rollno, {})

    attendance_percent = get_attendance_percentage(attendance)

    # Compute average marks
    if marks:
        avg = sum(x["marks"] for x in marks) / len(marks)
    else:
        avg = 0

    return jsonify({
        "student": student_name,
        "rollno": rollno,
        "marks": marks,
        "average_marks": round(avg, 2),
        "attendance": attendance,
        "attendance_percentage": attendance_percent,
        "attendance_days": len(attendance),
    })


# ===========================================================
#   4️⃣ IMPORT ATTENDANCE FROM ATTENDANCE MODULE
# ===========================================================
@progress_bp.route("/import_attendance", methods=["POST"])
def import_attendance():
    """
    Attendance Module will POST:
    {
        "attendance": {
            "1": {"2025-01-15":"P", "2025-01-16":"A"},
            "2": {...}
        }
    }
    """
    data = request.json
    global ATTENDANCE
    ATTENDANCE = data.get("attendance", {})

    return jsonify({"imported": True})


# ===========================================================
#   5️⃣ REGISTER STUDENT (Faculty/Admin)
# ===========================================================
@progress_bp.route("/register_student", methods=["POST"])
def register_student():
    data = request.json
    rollno = data.get("rollno")
    name = data.get("name")

    if not rollno or not name:
        return jsonify({"error": "rollno and name required"}), 400

    STUDENTS[rollno] = name

    return jsonify({"registered": True, "rollno": rollno, "name": name})
