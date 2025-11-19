from typing import Optional

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.db.crud import get_attendance_records_by_user
from app.db.engine import get_db
from app.db.models import AttendanceRecord, User, ModificationRequest, RequestStatus, OvertimeRequest
from app.services.report_service import ReportService
from app.services.user_service import UserService
from app.services.attendance_service import AttendanceService
from app.utils.decorators import admin_required
from app.utils.timecalc import parse_dt

bp = Blueprint("admin", __name__)


@bp.get("/users")
@jwt_required()
@admin_required()
def get_all_users():
    db = get_db()
    service = UserService(db)
    users = service.get_all_users()

    users_list = [
        {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "password_hash": user.password_hash,
            "role": user.role.value if hasattr(user.role, 'value') else str(user.role),
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat(),
            "updated_at": user.updated_at.isoformat(),
        } for user in users
    ]

    return jsonify(users_list), 200


@bp.get("/attendancerecords")
@jwt_required()
@admin_required()
def get_all_attendance_records():
    """List all attendance records from the database (admin only)."""
    db = get_db()
    records = db.query(AttendanceRecord).all()

    records_list = [
        {
            "id": record.id,
            "user_id": record.user_id,
            "check_in": record.check_in.isoformat() if record.check_in else None,
            "check_out": record.check_out.isoformat() if record.check_out else None,
            "work_location": record.work_location.value if hasattr(record.work_location, 'value') else str(
                record.work_location),
            "work_duration": record.work_duration,
            "date": record.date.isoformat() if record.date else None,
            "is_overtime_generated": record.is_overtime_generated,
            "created_at": record.created_at.isoformat() if record.created_at else None,
            "updated_at": record.updated_at.isoformat() if record.updated_at else None,
        }
        for record in records
    ]

    return jsonify(records_list), 200


@bp.get("/location-stats")
@jwt_required()
@admin_required()
def get_user_location_stats():
    """
    Home office vs office napok arány statisztika.
    Nem igényel paramétert.
    """
    db = get_db()
    service = ReportService(db)
    stats = service.get_location_stats()
    return jsonify(stats), 200


@bp.get("/overtime")
@admin_required()
def get_user_overtime():
    """
    Egy felhasználó túlóráinak lekérdezése.
    Query paraméterek:
      - start_date: opcionális (YYYY-MM-DD)
      - end_date: opcionális (YYYY-MM-DD)
    """
    db = get_db()
    service = ReportService(db)
    user_id = int(request.args.get("user_id"))

    try:
        start_date = parse_dt(request.args.get("start_date"))
        end_date = parse_dt(request.args.get("end_date"))
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    records = service.get_user_overtime(
        user_id=user_id,
        start_date=start_date,
        end_date=end_date,
    )

    result = []
    for r in records:
        result.append(
            {
                "id": r.id,
                "user_id": r.user_id,
                "date": r.date.isoformat() if r.date else None,
                "check_in": r.check_in.isoformat() if r.check_in else None,
                "check_out": r.check_out.isoformat() if r.check_out else None,
                "work_duration_minutes": r.work_duration,
                "work_location": r.work_location.value if getattr(r, "work_location", None) else None,
            }
        )

    return jsonify(result), 200


@bp.get("/summary")
@admin_required()
def get_user_summary():
    """
    Összefoglaló riport.
    Query paraméterek:
      - user_id: kötelező
      - start_date: opcionális (YYYY-MM-DD)
      - end_date: opcionális (YYYY-MM-DD)
    """
    db = get_db()
    service = ReportService(db)
    user_id = int(request.args.get("user_id"))

    try:
        start_date = parse_dt(request.args.get("start_date"))
        end_date = parse_dt(request.args.get("end_date"))
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    stats = service.get_summary(user_id, start_date, end_date)
    return jsonify(stats), 200


@bp.get("/user/<username>")
@admin_required()
def get_user_by_username(username: str):
    """
    Felhasználót keres a megadott név alapján.
    """
    db = get_db()
    service = UserService(db)
    user = service.get_user_by_username(username)
    if user is None:
        return jsonify({"error": f"User with username '{username}' not found"}), 404

    user_json = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role.value if hasattr(user.role, 'value') else str(user.role),
        "is_active": user.is_active,
        "created_at": user.created_at.isoformat(),
        "updated_at": user.updated_at.isoformat(),
    }
    return jsonify(user_json), 200


@bp.get("/user/<id>")
@admin_required()
def get_user_by_id(id: int):
    """
    Felhasználót keres az azonosító alapján.
    """
    db = get_db()
    service = UserService(db)
    user = service.get_user_by_id(id)
    if user is None:
        return jsonify({"error": f"User with id '{id}' not found"}), 404

    user_json = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role.value if hasattr(user.role, 'value') else str(user.role),
        "is_active": user.is_active,
        "created_at": user.created_at.isoformat(),
        "updated_at": user.updated_at.isoformat(),
    }

    return jsonify(user_json), 200


# --- Módosítási kérelmek – útvonalak JS-hez igazítva ---


@bp.get("/modification-requests")
@jwt_required()
@admin_required()
def get_modification_requests():
    db = get_db()
    status_filter = request.args.get("status")
    
    query = db.query(ModificationRequest)
    if status_filter:
        try:
            status_enum = RequestStatus(status_filter)
            query = query.filter(ModificationRequest.status == status_enum)
        except ValueError:
            pass # Ignore invalid status
            
    requests = query.all()
    
    result = []
    for req in requests:
        result.append({
            "id": req.id,
            "user_id": req.user_id,
            "username": req.requester.username if req.requester else None,
            "work_session_id": req.work_session_id,
            "date": req.work_session.date.isoformat() if req.work_session and req.work_session.date else None,
            "requested_check_in": req.requested_check_in.isoformat() if req.requested_check_in else None,
            "requested_check_out": req.requested_check_out.isoformat() if req.requested_check_out else None,
            "requested_work_location": req.requested_work_location.value if req.requested_work_location else None,
            "reason": req.reason,
            "status": req.status.value,
            "created_at": req.created_at.isoformat(),
        })
        
    return jsonify(result), 200


@bp.post("/modification-requests/<int:request_id>/review")
@jwt_required()
@admin_required()
def review_modification_request(request_id: int):
    db = get_db()
    data = request.get_json() or {}
    approve = data.get("approve")
    reason = data.get("reason")
    
    if approve is None:
        return jsonify({"error": "Missing 'approve' field"}), 400
        
    reviewer_id = int(get_jwt_identity())
    service = AttendanceService(db, reviewer_id)
    
    try:
        mod = service.review_modification(
            modification_id=request_id,
            approve=approve,
            reviewer_id=reviewer_id,
            rejection_reason=reason
        )
        return jsonify({
            "id": mod.id,
            "status": mod.status.value
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400


# --- Túlóra kérelmek – útvonalak JS-hez igazítva ---


@bp.get("/overtime-requests")
@jwt_required()
@admin_required()
def list_overtime_requests():
    db = get_db()
    status_param = request.args.get("status", type=str)
    query = db.query(OvertimeRequest)

    if status_param:
        try:
            status_enum = RequestStatus(status_param.lower())
            query = query.filter(OvertimeRequest.status == status_enum)
        except ValueError:
            return jsonify({"error": "Érvénytelen státusz paraméter."}), 400

    requests_qs = query.order_by(OvertimeRequest.request_date.desc()).all()

    result = []
    for req in requests_qs:
        result.append(
            {
                "id": req.id,
                "user_id": req.user_id,
                "username": getattr(req.requester, "username", None),
                "work_session_id": getattr(req, "attendance_id", None)
                or getattr(req, "work_session_id", None),
                "overtime_minutes": req.overtime_minutes,
                "request_date": req.request_date.isoformat()
                if getattr(req, "created_at", None)
                else None,
                "status": req.status.value if hasattr(req.status, "value") else str(req.status),
            }
        )

    return jsonify(result), 200


@bp.post("/overtime-requests/<int:request_id>/review")
@jwt_required()
@admin_required()
def review_overtime_request(request_id: int):
    db = get_db()
    data = request.get_json(silent=True) or {}
    approve = data.get("approve")
    reason = data.get("reason")

    if approve is None:
        return jsonify({"error": "A 'approve' mező kötelező (true/false)."}), 400

    req_obj: OvertimeRequest = (
        db.query(OvertimeRequest).filter_by(id=request_id).first()
    )
    if not req_obj:
        return jsonify({"error": "A megadott túlóra kérelem nem található."}), 404

    if approve:
        req_obj.status = RequestStatus.APPROVED
    else:
        req_obj.status = RequestStatus.REJECTED
        if hasattr(req_obj, "rejection_reason"):
            req_obj.rejection_reason = reason

    db.commit()

    return jsonify({"message": "Túlóra kérelem elbírálva.", "status": req_obj.status.value}), 200


# --- Felhasználó jelenlétek – admin.js által hívott endpoint ---


@bp.get("/users/<identifier>/attendance")
@jwt_required()
@admin_required()
def user_attendance(identifier: str):
    """
    identifier: lehet numerikus user_id vagy felhasználónév.
    """
    db = get_db()
    start_str = request.args.get("from")
    end_str = request.args.get("to")

    try:
        start_date = parse_dt(start_str) if start_str else None
        end_date = parse_dt(end_str) if end_str else None
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    # Felhasználó keresése ID vagy username alapján
    user: Optional[User] = None
    if identifier.isdigit():
        user = db.query(User).filter_by(id=int(identifier)).first()
    else:
        user = db.query(User).filter_by(username=identifier).first()

    if not user:
        return jsonify({"error": "Felhasználó nem található."}), 404

    records = get_attendance_records_by_user(user.id, start_date=start_date, end_date=end_date)

    result = []
    for rec in records:
        # Munkaidő percben – ha van check_in és check_out
        work_minutes = None
        if rec.check_in and rec.check_out:
            delta = rec.check_out - rec.check_in
            work_minutes = int(delta.total_seconds() // 60)

        result.append(
            {
                "date": rec.date.isoformat() if rec.date else None,
                "check_in": rec.check_in.isoformat() if rec.check_in else None,
                "check_out": rec.check_out.isoformat() if rec.check_out else None,
                "work_location": rec.work_location.value,
                "work_duration": work_minutes,
            }
        )

    return jsonify(result), 200