# app.py - Adjusted for Flat File Structure
from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
import os

# Import modules directly (since they are in the same folder now)
from user_management import user_bp
from dashboard import dashboard_bp
from attendance import attendance_bp
from lms_module import lms_bp
from progress_report import progress_bp
from notifications import notifications_bp
from chat_realtime import chat_rt_bp, socketio
from exams import exams_bp
from calendar_module import calendar_bp
from analytics import analytics_bp
from course_management import course_bp
from document_management import doc_bp
from storage_management import storage_bp
from task_management import task_bp

# Setup Flask to serve static files from the current directory (.)
app = Flask(__name__, static_folder=".")
CORS(app)
app.secret_key = "dev_secret_key"

# Serve SPA (index.html)
@app.route("/", methods=["GET"])
def index():
    # Look for index.html in the current directory
    return send_from_directory(".", "index.html")

# Serve other frontend assets (css/js/images)
@app.route("/<path:filename>")
def frontend_files(filename):
    # Look for files in the current directory
    return send_from_directory(".", filename)

# Simple health check
@app.route("/api/health")
def health():
    return jsonify({"status": "ok"})

# Register API blueprints
app.register_blueprint(user_bp, url_prefix="/api/user")
app.register_blueprint(dashboard_bp, url_prefix="/api/dashboard")
app.register_blueprint(attendance_bp, url_prefix="/api/attendance")
app.register_blueprint(lms_bp, url_prefix="/api/lms")
app.register_blueprint(progress_bp, url_prefix="/api/progress")
app.register_blueprint(notifications_bp, url_prefix="/api/notifications")
app.register_blueprint(chat_rt_bp, url_prefix="/api/chat")
app.register_blueprint(exams_bp, url_prefix="/api/exams")
app.register_blueprint(calendar_bp, url_prefix="/api/calendar")
app.register_blueprint(analytics_bp, url_prefix="/api/analytics")
app.register_blueprint(course_bp, url_prefix="/api/course")
app.register_blueprint(doc_bp, url_prefix="/api/docs")
app.register_blueprint(storage_bp, url_prefix="/api/storage")
app.register_blueprint(task_bp, url_prefix="/api/tasks")

if __name__ == "__main__":
    socketio.init_app(app, cors_allowed_origins="*")
    print("Starting app with Socket.IO...")
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
