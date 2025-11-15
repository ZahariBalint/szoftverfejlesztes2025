from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt

def admin_required():
    """
    Decorator to ensure the user has an 'admin' role.
    Must be used after @jwt_required().
    """
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            claims = get_jwt()
            if claims.get("role") != "admin":
                return jsonify({"error": "Administration rights are required for this action."}), 403
            return fn(*args, **kwargs)
        return decorator
    return wrapper