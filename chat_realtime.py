# modules/chat_realtime.py
from flask import Blueprint, request, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room
import uuid

chat_rt_bp = Blueprint("chat_realtime", __name__)

# Real-time messaging handler shared with app
socketio = SocketIO(cors_allowed_origins="*")

# In-memory storage
GROUPS = {} 
# group_id -> {id, name, members: [usernames]}

@chat_rt_bp.route("/create_group", methods=["POST"])
def create_group():
    data = request.json or {}
    group_name = data.get("name", "New Group")

    group_id = str(uuid.uuid4())[:6]  # short code like WhatsApp
    GROUPS[group_id] = {
        "id": group_id,
        "name": group_name,
        "members": []
    }
    return jsonify({"group_id": group_id, "group_name": group_name})

@chat_rt_bp.route("/groups", methods=["GET"])
def list_groups():
    return jsonify(list(GROUPS.values()))

@chat_rt_bp.route("/join_group", methods=["POST"])
def join_group():
    data = request.json or {}
    group_id = data.get("group_id")
    username = data.get("username")

    if group_id not in GROUPS:
        return jsonify({"error": "Group not found"}), 404

    if username not in GROUPS[group_id]["members"]:
        GROUPS[group_id]["members"].append(username)

    return jsonify({"joined": True, "group": GROUPS[group_id]})

# ---------------- SOCKET EVENTS (REAL-TIME) ---------------- #

@socketio.on("join_room")
def handle_join_room(data):
    username = data["username"]
    group_id = data["group_id"]

    join_room(group_id)
    emit("system_message", 
         {"msg": f"{username} joined the group."}, 
         room=group_id)

@socketio.on("send_message")
def handle_send_message(data):
    username = data["username"]
    group_id = data["group_id"]
    message = data["message"]

    # broadcast to everyone in room
    emit("receive_message", 
         {"username": username, "message": message}, 
         room=group_id)

@socketio.on("typing")
def handle_typing(data):
    emit("typing", data, room=data["group_id"])
