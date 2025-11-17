from flask import Flask, send_from_directory, redirect
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from .config.settings import Config
from .db.engine import init_db
from .routes import auth_routes, user_routes, attendance_routes, admin_routes


def create_app():
    app = Flask(__name__, static_folder='../static', static_url_path='/static')
    app.config.from_object(Config)

    # CORS és JWT beállítások
    CORS(app)
    JWTManager(app)

    # Adatbázis inicializálás
    with app.app_context():
        init_db(app)

    # Főoldal átirányítása a bejelentkezési oldalra
    @app.route('/')
    def index():
        return redirect('/login')

    # Login oldal kiszolgálása
    @app.route('/login')
    def login_page():
        return send_from_directory(app.static_folder, 'login.html')

    # Register oldal kiszolgálása
    @app.route('/register')
    def register_page():
        return send_from_directory(app.static_folder, 'register.html')

    # Dashboard oldal kiszolgálása
    @app.route('/dashboard')
    def dashboard_page():
        return send_from_directory(app.static_folder, 'dashboard.html')

    # Blueprintek regisztrálása
    app.register_blueprint(auth_routes.bp, url_prefix="/api/auth")
    app.register_blueprint(user_routes.bp, url_prefix="/api/users")
    app.register_blueprint(attendance_routes.bp, url_prefix="/api/attendance")
    app.register_blueprint(admin_routes.bp, url_prefix="/api/admin")

    # 404 hibakezelő
    @app.errorhandler(404)
    def page_not_found(e):
        return send_from_directory(app.static_folder, '404.html'), 404

    return app