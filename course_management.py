# modules/course_management.py
from flask import Blueprint, request, jsonify
import uuid

course_bp = Blueprint("course_mgmt", __name__)

COURSES = {}  # id -> {id, title, topics: []}

@course_bp.route("/add", methods=["POST"])
def add_course():
    data = request.json or {}
    cid = str(uuid.uuid4())
    COURSES[cid] = {"id": cid, "title": data.get("title"), "topics": data.get("topics", [])}
    return jsonify(COURSES[cid]), 201

@course_bp.route("/update/<cid>", methods=["PUT"])
def update_course(cid):
    data = request.json or {}
    course = COURSES.get(cid)
    if not course:
        return jsonify({"error":"not found"}), 404
    course.update(data)
    return jsonify(course)

@course_bp.route("/list", methods=["GET"])
def list_courses():
    return jsonify(list(COURSES.values()))
