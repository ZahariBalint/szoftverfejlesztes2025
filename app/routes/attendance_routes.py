from flask import Blueprint, jsonify, request
from app.db.engine import get_db
from app.services.attendance_service import AttendanceService
from app.db.models import WorkLocation

bp = Blueprint("attendance", __name__)

@bp.route("/checkin", methods=["POST"])
def check_in():
    db = get_db()
    user_id = request.json.get("user_id")
    #user_id = request.json.get("")
    location = WorkLocation(request.json.get("location", "office"))
    service = AttendanceService(db, user_id)
    record = service.check_in(location)
    #return jsonify({"id": record.id, "status": "checked_in"})
    return jsonify({"status": "checked_in"})
