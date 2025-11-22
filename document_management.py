# modules/document_management.py
from flask import Blueprint, request, jsonify
import uuid, datetime

doc_bp = Blueprint("docs", __name__)

DOCS = {}  # id -> {id,name,url,version,uploaded_at}

@doc_bp.route("/upload", methods=["POST"])
def upload():
    data = request.json or {}
    did = str(uuid.uuid4())
    DOCS[did] = {"id": did, "name": data.get("name"), "url": data.get("url"), "version": 1, "uploaded_at": datetime.datetime.utcnow().isoformat()}
    return jsonify(DOCS[did]), 201

@doc_bp.route("/list", methods=["GET"])
def list_docs():
    return jsonify(list(DOCS.values()))

@doc_bp.route("/update/<doc_id>", methods=["POST"])
def update_doc(doc_id):
    doc = DOCS.get(doc_id)
    if not doc:
        return jsonify({"error":"not found"}), 404
    doc["version"] += 1
    doc["url"] = request.json.get("url", doc["url"])
    return jsonify(doc)
