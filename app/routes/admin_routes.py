from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from app.db.engine import get_db
from app.db.models import AttendanceRecord
from app.services.user_service import UserService
from app.utils.decorators import admin_required

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
