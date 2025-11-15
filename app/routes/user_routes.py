from flask import Blueprint, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
from app.db.engine import get_db
from app.services.user_service import UserService

bp = Blueprint("users", __name__)

@bp.get("/me")
@jwt_required()
def me():
    db = get_db()
    user_id = get_jwt_identity()
    service = UserService(db)

    user = service.get_user_by_id(user_id)
        
    return jsonify({
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role.value if hasattr(user.role, 'value') else str(user.role),
    })