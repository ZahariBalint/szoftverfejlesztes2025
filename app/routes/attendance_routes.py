from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from app.db.engine import get_db
from app.services.attendance_service import AttendanceService
from app.db.models import WorkLocation
from datetime import date

bp = Blueprint("attendance", __name__)

@bp.post("/checkin")
@jwt_required()
def check_in():
    db = get_db()
    user_id = get_jwt_identity()
    location = WorkLocation(request.json.get("location", "office"))
    service = AttendanceService(db, user_id)
    record = service.check_in(location)
    return jsonify({"id": record.id, "status": "checked_in"})


@bp.post("/checkout")
@jwt_required()
def check_out():
    db = get_db()
    user_id = get_jwt_identity()
    service = AttendanceService(db, user_id)
    record = service.check_out()
    return jsonify({"id": record.id, "status": "checked_out"})


@bp.get("/weekly")
@jwt_required()
def get_weekly_attendance():
    """A heti jelenléti adatok lekérése a hétre, a dashboardhoz kell"""
    db = get_db()
    user_id = get_jwt_identity()
    service = AttendanceService(db, user_id)
    
    week_start = None
    week_start_str = request.args.get('week_start')
    if week_start_str:
        try:
            week_start = date.fromisoformat(week_start_str)
        except ValueError:
            # Invalid date format, use current week
            pass
    
    weekly_data = service.get_weekly_attendance(week_start=week_start)
    return jsonify(weekly_data)