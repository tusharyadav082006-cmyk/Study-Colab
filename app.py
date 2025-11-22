# app.py
from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS

# Import blueprints for modules
# Make sure these files exist in modules/ exactly as named.
from modules.user_management import user_bp
from modules.dashboard import dashboard_bp
from modules.attendance import attendance_bp
from modules.lms_module import lms_bp
from modules.progress_report import progress_bp
from modules.notifications import notifications_bp
# realtime chat - this file should create `chat_rt_bp` and `socketio`
from modules.chat_realtime import chat_rt_bp, socketio
from modules.exams import exams_bp
from modules.calendar_module import calendar_bp
from modules.analytics import analytics_bp
from modules.course_management import course_bp
from modules.document_management import doc_bp
from modules.storage_management import storage_bp
from modules.task_management import task_bp

app = Flask(__name__, static_folder="frontend", static_url_path="/frontend")
CORS(app)  # allow cross-origin for development
app.secret_key = "dev_secret_key"

# Serve SPA (index)
@app.route("/", methods=["GET"])
def index():
    return send_from_directory("frontend", "index.html")

# Serve frontend assets (css/js/images)
@app.route("/<path:filename>")
def frontend_files(filename):
    return send_from_directory("frontend", filename)

# Simple health check
@app.route("/api/health")
def health():
    return jsonify({"status": "ok"})

# Register API blueprints (prefix them to keep endpoints tidy)
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

# If run directly, start SocketIO (wraps Flask app)
if __name__ == "__main__":
    # Initialize socketio with flask app
    socketio.init_app(app, cors_allowed_origins="*")
    # run with socketio to enable real-time features
    print("Starting app with Socket.IO on http://127.0.0.1:5000")
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
