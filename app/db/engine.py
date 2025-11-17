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

    from app.db.models import User, UserRole, AttendanceRecord, WorkLocation
    from app.utils.security import hash_password
    from datetime import datetime, date, timedelta, time as dt_time

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
    
    # John-nak néhány jelenléti rekord hozzáadása a teszthez
    john = db.session.query(User).filter(User.username == "john").first()
    if john:
        today = date.today()
        days_since_monday = today.weekday()
        monday = today - timedelta(days=days_since_monday)
        
        # Format: {
        #   'day_offset': 0-6 (0=Monday, 6=Sunday),
        #   'check_in': 'HH:MM',
        #   'check_out': 'HH:MM' or None for active session,
        #   'location': 'office' | 'home_office' | 'other',
        #   'is_active': True/False (if True, check_out should be None)
        # }
        john_attendance_data = [
            {
                'day_offset': 0,
                'check_in': '09:00',
                'check_out': '12:00',
                'location': 'office',
                'is_active': False
            },
            {
                'day_offset': 1,
                'check_in': '08:00',
                'check_out': '17:00',
                'location': 'office',
                'is_active': False
            },
            {
                'day_offset': 2,
                'check_in': '08:00',
                'check_out': '12:00',
                'location': 'office',
                'is_active': False
            },
            {
                'day_offset': 2,
                'check_in': '13:00',
                'check_out': '17:00',
                'location': 'office',
                'is_active': False
            },
            {
                'day_offset': 3,
                'check_in': '10:00',
                'check_out': '18:00',
                'location': 'home_office',
                'is_active': False
            },
            {
                'day_offset': 4,
                'check_in': '08:00',
                'check_out': '14:00',
                'location': 'office',
                'is_active': False
            },
            {
                'day_offset': 5,
                'check_in': '09:00',
                'check_out': '13:00',
                'location': 'home_office',
                'is_active': False
            },
        ]
        
        # Process the attendance data
        attendance_records = []
        for entry in john_attendance_data:
            day_date = monday + timedelta(days=entry['day_offset'])
            
            if day_date > today:
                continue
            
            check_in_hour, check_in_minute = map(int, entry['check_in'].split(':'))
            check_in_datetime = datetime.combine(day_date, dt_time(check_in_hour, check_in_minute))
            
            check_out_datetime = None
            is_active = entry.get('is_active', False)
            
            if entry.get('check_out') and not is_active:
                check_out_hour, check_out_minute = map(int, entry['check_out'].split(':'))
                check_out_datetime = datetime.combine(day_date, dt_time(check_out_hour, check_out_minute))
            
            work_duration = None
            if check_in_datetime and check_out_datetime:
                delta = check_out_datetime - check_in_datetime
                work_duration = int(delta.total_seconds() / 60)
            
            record = AttendanceRecord(
                user_id=john.id,
                check_in=check_in_datetime,
                check_out=check_out_datetime if not is_active else None,
                work_location=WorkLocation[entry['location'].upper()],
                date=day_date,
                work_duration=work_duration if not is_active else None
            )
            
            attendance_records.append(record)
        
        # Ha ma még nincs aktív session, akkor hozzunk létre egyet       
        today_offset = (today - monday).days
        if 0 <= today_offset <= 6:
            has_today_session = any(
                (monday + timedelta(days=entry['day_offset'])) == today 
                for entry in john_attendance_data
            )
            if not has_today_session and today.weekday() < 5:
                check_in_datetime = datetime.combine(today, dt_time(8, 0))
                record = AttendanceRecord(
                    user_id=john.id,
                    check_in=check_in_datetime,
                    check_out=None,
                    work_location=WorkLocation.OFFICE,
                    date=today,
                    work_duration=None
                )
                attendance_records.append(record)
        
        db.session.add_all(attendance_records)
        db.session.commit()
        print(f"Seeded {len(attendance_records)} attendance records for john")