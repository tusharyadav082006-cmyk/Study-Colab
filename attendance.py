# modules/attendance.py
from flask import Blueprint, request, jsonify
from datetime import datetime

attendance_bp = Blueprint("attendance", __name__)

# ============================================================
#   IN-MEMORY DATABASE (Replace with real DB later)
# ============================================================
GROUPS = {
    # Example:
    # "CSE101": {
    #     "students": [
    #         {"rollno": 1, "name": "Ravi"},
    #         {"rollno": 2, "name": "Aditi"},
    #         {"rollno": 3, "name": "Sahil"}
    #     ],
    #     "attendance": {
    #         "2025-01-12": {1: "P", 2: "A", 3: "P"}
    #     }
    # }
}

STUDENT_ATTENDANCE = {}  
# student -> { "2025-01-12": "P" }

# ============================================================
#   1️⃣ CREATE GROUP (Faculty/Admin Only)
# ============================================================
@attendance_bp.route("/create_group", methods=["POST"])
def create_group():
    data = request.json
    group_id = data.get("group_id")
    students = data.get("students", [])

    if not group_id:
        return jsonify({"error": "Group ID required"}), 400

    GROUPS[group_id] = {
        "students": students,
        "attendance": {}
    }
    return jsonify({"created": True, "group_id": group_id})

# ============================================================
#   2️⃣ GET GROUP MEMBERS
# ============================================================
@attendance_bp.route("/group_members", methods=["GET"])
def get_group_members():
    group_id = request.args.get("group_id")

    if group_id not in GROUPS:
        return jsonify({"error": "Group not found"}), 404

    return jsonify(GROUPS[group_id]["students"])

# ============================================================
#   3️⃣ MARK ATTENDANCE (Faculty & Admin)
# ============================================================
@attendance_bp.route("/mark", methods=["POST"])
def mark_attendance():
    data = request.json

    role = data.get("role")
    if role == "student":
        return jsonify({"error": "Students cannot mark attendance"}), 403

    group_id = data.get("group_id")
    present_rolls = data.get("present", [])

    if group_id not in GROUPS:
        return jsonify({"error": "Group not found"}), 404

    today = datetime.now().strftime("%Y-%m-%d")

    if today not in GROUPS[group_id]["attendance"]:
        GROUPS[group_id]["attendance"][today] = {}

    for student in GROUPS[group_id]["students"]:
        roll = student["rollno"]
        status = "P" if roll in present_rolls else "A"

        GROUPS[group_id]["attendance"][today][roll] = status

        # store individual stats
        if roll not in STUDENT_ATTENDANCE:
            STUDENT_ATTENDANCE[roll] = {}
        STUDENT_ATTENDANCE[roll][today] = status

    return jsonify({
        "marked": True,
        "date": today,
        "details": GROUPS[group_id]["attendance"][today]
    })

# ============================================================
#   4️⃣ STUDENT: VIEW OWN ATTENDANCE
# ============================================================
@attendance_bp.route("/my", methods=["GET"])
def my_attendance():
    rollno = request.args.get("rollno")

    if not rollno:
        return jsonify({"error": "Roll number required"}), 400

    rollno = int(rollno)

    if rollno not in STUDENT_ATTENDANCE:
        return jsonify({"attendance": {}, "message": "No attendance yet"})

    return jsonify({
        "rollno": rollno,
        "attendance": STUDENT_ATTENDANCE[rollno]
    })

# ============================================================
#   5️⃣ FACULTY / ADMIN: VIEW GROUP ATTENDANCE SUMMARY
# ============================================================
@attendance_bp.route("/group_summary", methods=["GET"])
def group_summary():
    group_id = request.args.get("group_id")

    if group_id not in GROUPS:
        return jsonify({"error": "Group not found"}), 404

    return jsonify(GROUPS[group_id]["attendance"])
