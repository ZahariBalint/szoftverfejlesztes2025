from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from .config.settings import Config
from .db.engine import init_db
from .routes import auth_routes, user_routes, attendance_routes, admin_routes


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # CORS és JWT beállítások
    CORS(app)
    JWTManager(app)

    # Adatbázis inicializálás
    with app.app_context():
        init_db(app)


    # Blueprintek regisztrálása
    app.register_blueprint(auth_routes.bp, url_prefix="/api/auth")
    app.register_blueprint(user_routes.bp, url_prefix="/api/users")
    app.register_blueprint(attendance_routes.bp, url_prefix="/api/attendance")
    app.register_blueprint(admin_routes.bp, url_prefix="/api/admin")

    return app