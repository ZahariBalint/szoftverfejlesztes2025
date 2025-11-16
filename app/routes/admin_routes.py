from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from app.db.engine import get_db
from app.db.models import AttendanceRecord
from app.services.report_service import ReportService
from app.services.user_service import UserService
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

    return jsonify(users_list)


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
            "work_location": record.work_location.value if hasattr(record.work_location, 'value') else str(record.work_location),
            "work_duration": record.work_duration,
            "date": record.date.isoformat() if record.date else None,
            "is_overtime_generated": record.is_overtime_generated,
            "created_at": record.created_at.isoformat() if record.created_at else None,
            "updated_at": record.updated_at.isoformat() if record.updated_at else None,
        }
        for record in records
    ]

    return jsonify(records_list)

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
def get_summary():
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
