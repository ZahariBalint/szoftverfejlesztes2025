from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from app.db.engine import get_db
from app.services.attendance_service import AttendanceService
from app.db.models import WorkLocation
from datetime import date
from app.utils.timecalc import parse_dt

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
  
@bp.post("/modifications")
@jwt_required()
def request_modification():
    """
    Módosítási kérelem létrehozása a saját munkamenetre.
    Várható body (JSON):
    {
        "work_session_id": 123,              # kötelező
        "requested_check_in": "2025-11-15T08:00:00",   # opcionális, ISO 8601
        "requested_check_out": "2025-11-15T16:30:00",  # opcionális, ISO 8601
        "requested_location": "office" | "home_office" | ...,
        "reason": "Indoklás szövege"
    }
    """

    data = request.get_json() or {}
    work_session_id = data.get("work_session_id")

    try:
        requested_check_in = parse_dt(data.get("requested_check_in"))
        requested_check_out = parse_dt(data.get("requested_check_out"))
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    requested_location = WorkLocation(data["requested_location"])
    reason = data.get("reason")

    db = get_db()
    user_id = get_jwt_identity()
    service = AttendanceService(db, user_id)

    try:
        req = service.request_modification(
            work_session_id=work_session_id,
            requested_check_in=requested_check_in,
            requested_check_out=requested_check_out,
            requested_location=requested_location,
            reason=reason,
        )
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    return jsonify(
        {
            "id": req.id,
            "work_session_id": req.work_session_id,
            "status": req.status.value,
            "reason": req.reason,
        }
    ), 201

@bp.post("/modifications/<int:modification_id>/review")
@jwt_required()
def review_modification(modification_id: int):
    """
    Módosítási kérelem elbírálása (admin funkció).
    Várható body (JSON):
    {
        "approve": true/false, # kötelező
        "rejection_reason": "Indoklás elutasítás esetén"   # opcionális
    }
    """
    data = request.get_json() or {}

    approve = bool(data.get("approve"))
    rejection_reason = data.get("rejection_reason")

    db = get_db()
    reviewer_id = get_jwt_identity()
    service = AttendanceService(db, reviewer_id)

    try:
        mod = service.review_modification(
            modification_id=modification_id,
            approve=approve,
            reviewer_id=reviewer_id,
            rejection_reason=rejection_reason,
        )
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    return jsonify(
        {
            "id": mod.id,
            "work_session_id": mod.work_session_id,
            "status": mod.status.value,
            "rejection_reason": getattr(mod, "rejection_reason", None),
            "reviewed_by": mod.reviewed_by,
        }
    ), 200
