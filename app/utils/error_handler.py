from flask import jsonify
from werkzeug.exceptions import HTTPException


# --- Alap saját kivételek ---

class ServiceError(Exception):
    """Általános szolgáltatás réteg hiba."""
    status_code = 400

    def __init__(self, message="Service error occurred", status_code=None):
        super().__init__(message)
        if status_code:
            self.status_code = status_code
        self.message = message


class NotFoundError(ServiceError):
    """Erőforrás nem található."""
    status_code = 404


class ForbiddenError(ServiceError):
    """A felhasználónak nincs jogosultsága hozzáférni."""
    status_code = 403


class UnauthorizedError(ServiceError):
    """Nincs hitelesítve vagy lejárt token."""
    status_code = 401


# --- Globális hibakezelő regisztrálása ---

def register_error_handlers(app):

    @app.errorhandler(ServiceError)
    def handle_service_error(e):
        response = {
            "error": e.message,
            "status": e.status_code
        }
        return jsonify(response), e.status_code

    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        response = {
            "error": e.description,
            "status": e.code
        }
        return jsonify(response), e.code

    @app.errorhandler(Exception)
    def handle_generic_exception(e):
        print("Unhandled exception:", e)

        response = {
            "error": "Unexpected server error",
            "status": 500
        }
        return jsonify(response), 500
