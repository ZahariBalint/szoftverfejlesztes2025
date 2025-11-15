from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from app.db.engine import get_db
from app.services.attendance_service import AttendanceService
from app.db.models import WorkLocation

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
