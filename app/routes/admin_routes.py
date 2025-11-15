from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from app.db.engine import get_db
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