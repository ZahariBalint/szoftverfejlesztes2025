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