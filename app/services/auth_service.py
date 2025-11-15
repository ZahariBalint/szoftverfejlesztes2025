from sqlalchemy.orm import Session
from flask_jwt_extended import create_access_token
from app.db.models import User, UserRole
from app.utils.security import check_password, hash_password

class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def login(self, username: str = None, email: str = None, password: str = None):
        if not password or not (username or email):
            raise ValueError("Hiányzó felhasználónév vagy jelszó")
        
        query = self.db.query(User)
        user = query.filter(User.username == username).first() if username else query.filter(User.email == email).first()

        if not user or not check_password(password, user.password_hash):
            raise ValueError("Érvénytelen hitelesítési adatok")
        
        token = create_access_token(
            identity=str(user.id),
            additional_claims={
                "role": user.role.value if hasattr(user.role, 'value') else str(user.role),
                "username": user.username
            },
        )
        return user, token
    
    def register(self, username: str, email: str, password: str):
        if not username or not email or not password:
            raise ValueError("Felhasználónév, email és jelszó megadása kötelező")
        
        if len(username) < 3 or len(password) < 3:
            raise ValueError("A felhasználónévnek és jelszónak legalább 3 karakter hosszúnak kell lennie")

        existing_user = self.db.query(User).filter(
            (User.username == username) | (User.email == email)
        ).first()

        if existing_user:
            if existing_user.username == username:
                raise ValueError("A felhasználónév már foglalt")
            if existing_user.email == email:
                raise ValueError("Az email cím már foglalt")
            
        user = User(
            username=username,
            email=email,
            password_hash=hash_password(password),
            role=UserRole.USER,
        )

        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        return user

    def get_user_by_id(self, user_id: int):
        return self.db.query(User).get(user_id)