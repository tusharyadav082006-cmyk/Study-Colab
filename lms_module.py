# modules/lms_module.py
from flask import Blueprint, request, jsonify
import os
from datetime import datetime

lms_bp = Blueprint("lms", __name__)

# Folder where files will be stored
UPLOAD_ROOT = "uploaded_files"

# Memory structure to track group files
GROUP_FILES = {
    # "GROUP1": [
    #     {
    #         "filename": "notes1.pdf",
    #         "filepath": "uploaded_files/GROUP1/notes1.pdf",
    #         "uploaded_by": "Amit",
    #         "uploaded_at": "2025-01-21 10:33"
    #     }
    # ]
}

# Ensure folder exists
if not os.path.exists(UPLOAD_ROOT):
    os.makedirs(UPLOAD_ROOT)

# ============================================================
# 1️⃣ Upload File to a Group
# ============================================================
@lms_bp.route("/upload", methods=["POST"])
def upload_file():
    group_id = request.form.get("group_id")
    username = request.form.get("username")

    if not group_id:
        return jsonify({"error": "Group ID required"}), 400

    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]

    # Create folder for group if not exists
    group_dir = os.path.join(UPLOAD_ROOT, group_id)
    if not os.path.exists(group_dir):
        os.makedirs(group_dir)

    # Save file
    filename = file.filename
    filepath = os.path.join(group_dir, filename)
    file.save(filepath)

    # Track file metadata
    entry = {
        "filename": filename,
        "filepath": filepath,
        "uploaded_by": username,
        "uploaded_at": datetime.now().strftime("%Y-%m-%d %H:%M")
    }

    if group_id not in GROUP_FILES:
        GROUP_FILES[group_id] = []

    GROUP_FILES[group_id].append(entry)

    return jsonify({
        "uploaded": True,
        "file": filename,
        "group": group_id
    })

# ============================================================
# 2️⃣ Fetch All Files of a Group
# ============================================================
@lms_bp.route("/files", methods=["GET"])
def get_files():
    group_id = request.args.get("group_id")

    if not group_id:
        return jsonify({"error": "Group ID required"}), 400

    if group_id not in GROUP_FILES:
        return jsonify({
            "group_id": group_id,
            "files": []
        })

    # Return metadata only (frontend can download)
    output = []
    for f in GROUP_FILES[group_id]:
        output.append({
            "filename": f["filename"],
            "url": f["filepath"],   # This path can be used for downloading
            "uploaded_by": f["uploaded_by"],
            "uploaded_at": f["uploaded_at"]
        })

    return jsonify({
        "group_id": group_id,
        "files": output
    })

# ============================================================
# 3️⃣ ADMIN — Show All Groups & Files
# ============================================================
@lms_bp.route("/all_groups", methods=["GET"])
def admin_all_groups():
    return jsonify(GROUP_FILES)
