from flask import Blueprint, jsonify, request
from  flask_jwt_extended import get_jwt_identity, jwt_required
from app.db.engine import get_db
from app.services.auth_service import AuthService

bp = Blueprint("auth", __name__)

@bp.post("/register")
def register():
    data = request.get_json() or {}
    db = get_db()
    service = AuthService(db)

    try:
        user = service.register(
            username=data.get("username"),
            email=data.get("email"),
            password=data.get("password"),
        )
        return jsonify({
            "msg": "User registered successfully",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role.value if hasattr(user.role, 'value') else str(user.role),
            }
        }), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@bp.post("/login")
def login():
    data = request.get_json() or {}
    db = get_db()
    service = AuthService(db)

    try:
        user, token = service.login(
            username=data.get("username"),
            email=data.get("email"),
            password=data.get("password"),
        )
        return jsonify({
            "access_token": token,
            "token_type": "Bearer",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role.value if hasattr(user.role, 'value') else str(user.role),
            }
        })
    except ValueError as e:
        return jsonify({"error": str(e)}), 401
    
@bp.get("/me")
@jwt_required()
def me():
    db = get_db()
    service = AuthService(db)
    user_id = get_jwt_identity()

    user = service.get_user_by_id(user_id)
    return jsonify({
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role.value if hasattr(user.role, 'value') else str(user.role),
    })