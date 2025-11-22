# modules/task_management.py
from flask import Blueprint, request, jsonify
import uuid, datetime

task_bp = Blueprint("tasks", __name__)

TASKS = []  # {id,title,desc,assigned_to,status,created_at}

@task_bp.route("/create", methods=["POST"])
def create_task():
    data = request.json or {}
    tid = str(uuid.uuid4())
    t = {"id": tid, "title": data.get("title"), "desc": data.get("desc"), "assigned_to": data.get("assigned_to"), "status": "open", "created_at": datetime.datetime.utcnow().isoformat()}
    TASKS.append(t)
    return jsonify(t), 201

@task_bp.route("/list", methods=["GET"])
def list_tasks():
    user = request.args.get("user")
    if user:
        return jsonify([t for t in TASKS if t.get("assigned_to")==user])
    return jsonify(TASKS)

@task_bp.route("/update/<tid>", methods=["PUT"])
def update_task(tid):
    data = request.json or {}
    for t in TASKS:
        if t["id"] == tid:
            t.update(data)
            return jsonify(t)
    return jsonify({"error":"not found"}), 404
