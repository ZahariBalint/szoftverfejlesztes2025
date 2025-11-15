from app.db.base import Base
from flask_sqlalchemy import SQLAlchemy

# Flask-SQLAlchemy inicializálás
db = SQLAlchemy()


def init_db(app):
    """
    Adatbázis inicializálása a Flask app-pal.

    Használat:
        from app.db.engine import db, init_db

        app = Flask(__name__)
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///worktrack.db'
        init_db(app)
    """
    db.init_app(app)

    with app.app_context():
        # Importáljuk a modelleket, hogy az SQLAlchemy felismerje őket
        from app.db import models  # noqa: F401
        # Táblák létrehozása (csak dev módban! Production-ban Alembic-et használj)
        db.create_all()
        Base.metadata.create_all(bind=db.engine)

        # 2 user és 1 admin létrehozása alapból
        seed_initial_data()

        print("Database initialized successfully!")


def get_db():
    """
    Aktuális adatbázis session lekérése.
    Flask-SQLAlchemy automatikusan kezeli a session-öket.
    
    Használat route-okban:
        from app.db.engine import db
        
        @app.route('/users')
        def get_users():
            users = db.session.query(User).all()
            return jsonify(users)
    """
    return db.session


def drop_all_tables(app):
    """
    VESZÉLYES: Összes tábla törlése!
    Csak fejlesztéshez/teszteléshez használd!
    """
    with app.app_context():
        db.drop_all()
        print("All database tables dropped!")


def create_all_tables(app):
    """
    Összes tábla létrehozása.
    Figyelem: Alembic migrációk használata ajánlott!
    """
    with app.app_context():
        from app.db import models  # noqa: F401
        db.create_all()
        print("All database tables created!")

def seed_initial_data():
    """
    2 normál user + 1 admin
    Mivel In-memory SQLite eseétén üres az adatbázis minden indításkor
    """

    from app.db.models import User, UserRole
    from app.utils.security import hash_password

    exisiting = db.session.query(User).count()
    if exisiting >0:
        print("Seed skipped, some users already exist.")
        return
    
    users = [
        User(
            username="john",
            email="john@example.com",
            password_hash=hash_password("john"),
            role=UserRole.USER,
        ),
        User(
            username="jane",
            email="jane@example.com",
            password_hash=hash_password("jane"),
            role=UserRole.USER,
        ),
        User(
            username="admin",
            email="admin@example.com",
            password_hash=hash_password("admin"),
            role=UserRole.ADMIN,
        ),
    ]
    db.session.add_all(users)
    db.session.commit()
    print("Seeded initial users: john, jane, admin")