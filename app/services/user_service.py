from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.db.models import User
from app.utils.error_handler import ServiceError, ValidationError,NotFoundError


class UserService:
    def __init__(self, db: Session):
        self.db = db

    def get_user_by_id(self, user_id: int) -> User | None:
        """Fetches a user by their ID."""
        if not user_id:
            raise ValidationError("user_id megadása kötelező")

        try:
            user=self.db.query(User).get(user_id)
            if not user:
                raise NotFoundError(f"Nincs felhasználó a megadott ID-vel: {user_id}")
            return user
        except SQLAlchemyError as e:
            raise ServiceError(f"Adatbázis hiba a felhasználó lekérdezésénél: {e}")

    def get_all_users(self) -> list[type[User]]:
        """Fetches all users."""
        try:
            users=self.db.query(User).all()
            if not users:
                raise NotFoundError("Nicsenek felhasználók az adatbázisban")
            return users
        except SQLAlchemyError as e:
            raise ServiceError(f"Adatbázis hiba a felhasználók lekérdezésénél: {e}")

    def get_user_by_username(self, username: str) -> User | None:
        """Fetches a user by their username."""
        if not username:
            raise ValidationError("username megadása kötelező")

        try:
            user = self.db.query(User).filter(User.username == username).first()
            if not user:
                raise NotFoundError(f"Nincs felhasználó a megadott felhasználónévvel: {username}")
            return user
        except SQLAlchemyError as e:
            raise ServiceError(f"Adatbázis hiba a felhasználó lekérdezésénél: {e}")