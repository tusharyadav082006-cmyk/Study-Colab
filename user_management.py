# modules/user_management.py
from flask import Blueprint, request, jsonify, abort
import uuid
from werkzeug.security import generate_password_hash, check_password_hash

user_bp = Blueprint("user_management", __name__)

# In-memory store
USERS = {
    # user_id: {id, username, password_hash, role, profile}
}
SESSIONS = {}  # simple token -> user_id

def _find_by_username(username):
    for u in USERS.values():
        if u["username"] == username:
            return u
    return None

@user_bp.route("/register", methods=["POST"])
def register():
    data = request.json or {}
    username = data.get("username")
    password = data.get("password")
    role = data.get("role", "student")  # student/faculty/admin
    profile = data.get("profile", {})

    if not username or not password:
        abort(400, "username and password required")
    if _find_by_username(username):
        abort(400, "username exists")

    uid = str(uuid.uuid4())
    USERS[uid] = {
        "id": uid,
        "username": username,
        "password_hash": generate_password_hash(password),
        "role": role,
        "profile": profile
    }
    return jsonify({"id": uid, "username": username, "role": role}), 201

@user_bp.route("/login", methods=["POST"])
def login():
    data = request.json or {}
    username = data.get("username")
    password = data.get("password")
    user = _find_by_username(username)
    if not user or not check_password_hash(user["password_hash"], password):
        return jsonify({"error": "invalid credentials"}), 401
    token = str(uuid.uuid4())
    SESSIONS[token] = user["id"]
    return jsonify({"token": token, "user": {"id": user["id"], "username": user["username"], "role": user["role"]}})

@user_bp.route("/me", methods=["GET"])
def me():
    token = request.headers.get("Authorization")
    uid = SESSIONS.get(token)
    if not uid:
        return jsonify({"error": "unauthenticated"}), 401
    user = USERS.get(uid)
    return jsonify({"id": user["id"], "username": user["username"], "role": user["role"], "profile": user["profile"]})

@user_bp.route("/profile", methods=["PUT"])
def update_profile():
    token = request.headers.get("Authorization")
    uid = SESSIONS.get(token)
    if not uid:
        return jsonify({"error": "unauthenticated"}), 401
    data = request.json or {}
    USERS[uid]["profile"].update(data)
    return jsonify({"profile": USERS[uid]["profile"]})

@user_bp.route("/list", methods=["GET"])
def list_users():
    # admin-only in real app — here return all
    out = [{"id": u["id"], "username": u["username"], "role": u["role"], "profile": u["profile"]} for u in USERS.values()]
    return jsonify(out)
