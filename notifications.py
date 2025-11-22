# modules/notifications.py
from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta

notifications_bp = Blueprint("notifications", __name__)

# ===============================================================
# In-memory notification storage
# ===============================================================
USER_NOTIFS = {}  
# USER_NOTIFS["tushar"] = [ {msg, date} ]

GROUP_NOTIFS = {}  
# GROUP_NOTIFS["CSE101"] = [ {msg, date} ]

# Calendar exam data will be imported from academic calendar
EXAM_SCHEDULE = []  
# Example: [ {"title":"Mid Sem", "date":"2025-01-15", "group_id":"CSE101"} ]

# Attendance imported from progress module
STUDENT_ATTENDANCE = {}  
# STUDENT_ATTENDANCE[roll] = { "2025-01-12":"P", ... }

# Roll → username mapping
ROLL_USER = {}
# Example: 101 → "tushar"

# Group structure
GROUP_MEMBERS = {}
# GROUP_MEMBERS["CSE101"] = ["tushar", "aditi"]


# ==================================================================
# 1️⃣ Send Notification to Group (Faculty/Admin Only)
# ==================================================================
@notifications_bp.route("/send_group", methods=["POST"])
def send_group():
    data = request.json

    role = data.get("role")
    if role == "student":
        return jsonify({"error": "Students cannot send notifications"}), 403

    group_id = data.get("group_id")
    msg = data.get("msg")

    if not group_id or not msg:
        return jsonify({"error": "Missing fields"}), 400

    entry = {
        "message": msg,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M")
    }

    if group_id not in GROUP_NOTIFS:
        GROUP_NOTIFS[group_id] = []

    GROUP_NOTIFS[group_id].append(entry)

    # Push to each member's inbox
    if group_id in GROUP_MEMBERS:
        for user in GROUP_MEMBERS[group_id]:
            if user not in USER_NOTIFS:
                USER_NOTIFS[user] = []
            USER_NOTIFS[user].append(entry)

    return jsonify({"sent": True, "group_id": group_id, "message": msg})


# ==================================================================
# 2️⃣ Send Notification to Single User
# ==================================================================
@notifications_bp.route("/send_user", methods=["POST"])
def send_user():

    data = request.json

    role = data.get("role")
    if role == "student":
        return jsonify({"error": "Students cannot send notifications"}), 403

    username = data.get("username")
    msg = data.get("msg")

    if not username or not msg:
        return jsonify({"error": "Missing fields"}), 400

    entry = {
        "message": msg,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M")
    }

    if username not in USER_NOTIFS:
        USER_NOTIFS[username] = []

    USER_NOTIFS[username].append(entry)

    return jsonify({"sent": True, "username": username})


# ==================================================================
# 3️⃣ AUTO-ATTENDANCE ALERT (< 75%)
# ==================================================================
def check_attendance_alerts():
    alerts = []

    for roll, records in STUDENT_ATTENDANCE.items():
        total = len(records)
        present = sum(1 for v in records.values() if v == "P")

        percent = (present / total) * 100 if total > 0 else 0

        if percent < 75:
            username = ROLL_USER.get(roll)
            if not username:
                continue

            msg = f"Alert: Your attendance is below 75% ({percent:.2f}%)."

            entry = {
                "message": msg,
                "date": datetime.now().strftime("%Y-%m-%d %H:%M")
            }

            if username not in USER_NOTIFS:
                USER_NOTIFS[username] = []

            USER_NOTIFS[username].append(entry)
            alerts.append({"user": username, "message": msg})

    return alerts


# ==================================================================
# 4️⃣ AUTO-EXAM REMINDER (Exam within 7 days)
# ==================================================================

def check_exam_alerts():
    alerts = []
    today = datetime.now().date()

    for exam in EXAM_SCHEDULE:
        ex_date = datetime.strptime(exam["date"], "%Y-%m-%d").date()
        diff = (ex_date - today).days

        if 0 <= diff <= 7:  # exam coming within a week
            msg = f"Reminder: Upcoming exam '{exam['title']}' on {exam['date']}."

            group_id = exam.get("group_id")
            if not group_id:
                continue

            # Notify whole group
            entry = {
                "message": msg,
                "date": datetime.now().strftime("%Y-%m-%d %H:%M")
            }

            if group_id not in GROUP_NOTIFS:
                GROUP_NOTIFS[group_id] = []
            GROUP_NOTIFS[group_id].append(entry)

            # Notify members
            if group_id in GROUP_MEMBERS:
                for user in GROUP_MEMBERS[group_id]:
                    if user not in USER_NOTIFS:
                        USER_NOTIFS[user] = []
                    USER_NOTIFS[user].append(entry)
                    alerts.append({"user": user, "message": msg})

    return alerts