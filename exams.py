# modules/exams.py
from flask import Blueprint, request, jsonify
import uuid, datetime

exams_bp = Blueprint("exams", __name__)

EXAMS = {}  # exam_id -> {id,title,date,schedule}
RESULTS = {}  # student -> [{exam_id, marks, grade}]

@exams_bp.route("/create", methods=["POST"])
def create_exam():
    data = request.json or {}
    eid = str(uuid.uuid4())
    EXAMS[eid] = {"id": eid, "title": data.get("title"), "date": data.get("date"), "created_at": datetime.datetime.utcnow().isoformat()}
    return jsonify(EXAMS[eid]), 201

@exams_bp.route("/list", methods=["GET"])
def list_exams():
    return jsonify(list(EXAMS.values()))

@exams_bp.route("/result/enter", methods=["POST"])
def enter_result():
    data = request.json or {}
    student = data.get("student")
    exam_id = data.get("exam_id")
    marks = data.get("marks", 0)
    if not student or not exam_id:
        return jsonify({"error":"student and exam_id required"}), 400
    RESULTS.setdefault(student, []).append({"exam_id": exam_id, "marks": marks})
    return jsonify({"ok": True})

@exams_bp.route("/result/<student>", methods=["GET"])
def get_results(student):
    return jsonify(RESULTS.get(student, []))
