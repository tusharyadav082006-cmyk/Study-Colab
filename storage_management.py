# modules/storage_management.py
from flask import Blueprint, request, jsonify

storage_bp = Blueprint("storage", __name__)

STORAGE = {
    "total_bytes": 100 * 1024 * 1024,  # 100 MB
    "used_bytes": 0,
    "files": []
}

@storage_bp.route("/usage", methods=["GET"])
def usage():
    total = STORAGE["total_bytes"]
    used = STORAGE["used_bytes"]
    return jsonify({"total": total, "used": used, "free": total-used})

@storage_bp.route("/add_file", methods=["POST"])
def add_file():
    data = request.json or {}
    name = data.get("name")
    size = int(data.get("size",0))
    STORAGE["files"].append({"name": name, "size": size})
    STORAGE["used_bytes"] += size
    return jsonify({"ok": True, "used": STORAGE["used_bytes"]})
