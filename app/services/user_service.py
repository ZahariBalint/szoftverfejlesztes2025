from sqlalchemy.orm import Session

from app.db.models import User

class UserService:
    def __init__(self, db: Session):
        self.db = db

    def get_user_by_id(self, user_id: int) -> User | None:
        """Fetches a user by their ID."""
        return self.db.query(User).get(user_id)

    def get_all_users(self) -> list[type[User]]:
        """Fetches all users."""
        return self.db.query(User).all()

    def get_user_by_username(self, username: str) -> User | None:
        """Fetches a user by their username."""
        return self.db.query(User).filter(User.username == username).first()