# modules/analytics.py
from flask import Blueprint, request, jsonify
import random

analytics_bp = Blueprint("analytics", __name__)

@analytics_bp.route("/overview", methods=["GET"])
def overview():
    # return dummy stats suitable for charts
    return jsonify({
        "attendance_trend": [{"day": i, "percent": 70 + random.randint(-10,10)} for i in range(1,8)],
        "marks_distribution": [{"subject":"Math","avg":75},{"subject":"CS","avg":80},{"subject":"Eng","avg":70}],
        "active_users": random.randint(50,200)
    })
