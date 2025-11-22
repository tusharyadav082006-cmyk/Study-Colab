# modules/calendar_module.py
from flask import Blueprint, request, jsonify
from datetime import datetime
import uuid

calendar_bp = Blueprint("calendar", __name__)

# ==================================================================
# In-Memory Calendar Events Storage
# ==================================================================
EVENTS = []
"""
EVENT STRUCTURE:
{
    "id": "uuid",
    "title": "Exam",
    "start": "2025-02-12",
    "end": "2025-02-12",
    "group_id": "CSE101",
    "type": "exam" | "holiday" | "festival" | "event",
    "created_by": "faculty_username"
}
"""

# ==================================================================
# Helper: Find event
# ==================================================================
def find_event(event_id):
    for e in EVENTS:
        if e["id"] == event_id:
            return e
    return None


# ==================================================================
# 1️⃣ Get All Events (Everyone)
# ==================================================================
@calendar_bp.route("/list", methods=["GET"])
def list_events():
    return jsonify(EVENTS)


# ==================================================================
# 2️⃣ Add Event (Faculty & Admin)
# ==================================================================
@calendar_bp.route("/add", methods=["POST"])
def add_event():
    data = request.json

    role = data.get("role")
    if role == "student":
        return jsonify({"error": "Students cannot add events"}), 403

    title = data.get("title")
    start = data.get("start")
    end = data.get("end")
    event_type = data.get("type", "event")
    group_id = data.get("group_id", "all")
    created_by = data.get("created_by", "unknown")

    if not title or not start:
        return jsonify({"error": "Missing fields"}), 400

    event = {
        "id": str(uuid.uuid4())[:8],
        "title": title,
        "start": start,
        "end": end if end else start,
        "type": event_type,
        "group_id": group_id,
        "created_by": created_by
    }

    EVENTS.append(event)

    return jsonify({"added": True, "event": event})


# ==================================================================
# 3️⃣ Edit Event (Faculty & Admin)
# ==================================================================
@calendar_bp.route("/edit", methods=["PUT"])
def edit_event():
    data = request.json
    role = data.get("role")

    if role == "student":
        return jsonify({"error": "Students cannot edit events"}), 403

    event_id = data.get("id")
    event = find_event(event_id)
    if not event:
        return jsonify({"error": "Event not found"}), 404

    event["title"] = data.get("title", event["title"])
    event["start"] = data.get("start", event["start"])
    event["end"] = data.get("end", event["end"])
    event["type"] = data.get("type", event["type"])
    event["group_id"] = data.get("group_id", event["group_id"])

    return jsonify({"updated": True, "event": event})


# ==================================================================
# 4️⃣ Delete Event (Faculty & Admin)
# ==================================================================
@calendar_bp.route("/delete", methods=["DELETE"])
def delete_event():
    data = request.json
    role = data.get("role")

    if role == "student":
        return jsonify({"error": "Students cannot delete events"}), 403

    event_id = data.get("id")
    event = find_event(event_id)

    if not event:
        return jsonify({"error": "Event not found"}), 404

    EVENTS.remove(event)
    return jsonify({"deleted": True, "id": event_id})
