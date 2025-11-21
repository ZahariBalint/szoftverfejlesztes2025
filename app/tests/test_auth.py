import pytest
from unittest.mock import MagicMock, patch
from sqlalchemy.exc import SQLAlchemyError
from app.services.auth_service import AuthService
from app.db.models import User, UserRole
from app.utils.error_handler import ServiceError, ValidationError

@pytest.fixture
def db():
    return MagicMock()

@pytest.fixture
def service(db):
    return AuthService(db)

# -----------------------------
# login TESTS
# -----------------------------
def test_login_missing_credentials(service):
    with pytest.raises(ValidationError):
        service.login(username=None, password=None)
    with pytest.raises(ValidationError):
        service.login(email=None, password=None)

def test_login_user_not_found(service, db):
    db.query().filter().first.return_value = None
    with pytest.raises(ValidationError):
        service.login(username="foo", password="bar")

def test_login_wrong_password(service, db):
    user = MagicMock(password_hash="hashed_pw")
    db.query().filter().first.return_value = user
    with patch("app.services.auth_service.check_password", return_value=False):
        with pytest.raises(ValidationError):
            service.login(username="foo", password="wrong")

def test_login_success(service, db):
    user = MagicMock(id=1, username="test", role=UserRole.USER, password_hash="hashed")
    db.query().filter().first.return_value = user
    with patch("app.services.auth_service.check_password", return_value=True):
        with patch("app.services.auth_service.create_access_token", return_value="token123") as mock_token:
            u, token = service.login(username="test", password="pw")
            assert u == user
            assert token == "token123"
            mock_token.assert_called_once()

def test_login_db_error(service, db):
    db.query.side_effect = SQLAlchemyError("db fail")
    with pytest.raises(ServiceError):
        service.login(username="foo", password="bar")

# -----------------------------
# register TESTS
# -----------------------------
def test_register_missing_fields(service):
    with pytest.raises(ValidationError):
        service.register(username=None, email="a@b.com", password="123")
    with pytest.raises(ValidationError):
        service.register(username="abc", email=None, password="123")
    with pytest.raises(ValidationError):
        service.register(username="abc", email="a@b.com", password=None)

def test_register_too_short(service):
    with pytest.raises(ValidationError):
        service.register(username="ab", email="a@b.com", password="123")
    with pytest.raises(ValidationError):
        service.register(username="abc", email="a@b.com", password="12")

def test_register_existing_username_or_email(service, db):
    existing_user = MagicMock(username="abc", email="a@b.com")
    db.query().filter().first.return_value = existing_user
    with pytest.raises(ValidationError):
        service.register(username="abc", email="new@b.com", password="123")
    with pytest.raises(ValidationError):
        service.register(username="new", email="a@b.com", password="123")

def test_register_success(service, db):
    db.query().filter().first.return_value = None
    with patch("app.services.auth_service.hash_password", return_value="hashedpw") as mock_hash:
        user = service.register(username="abc", email="a@b.com", password="123")
        db.add.assert_called_once_with(user)
        db.commit.assert_called_once()
        db.refresh.assert_called_once_with(user)
        assert user.username == "abc"
        assert user.email == "a@b.com"
        assert user.password_hash == "hashedpw"
        assert user.role == UserRole.USER

def test_register_db_error_on_commit(service, db):
    db.query().filter().first.return_value = None
    db.commit.side_effect = SQLAlchemyError("fail")
    with patch("app.services.auth_service.hash_password", return_value="hashedpw"):
        with pytest.raises(ServiceError):
            service.register(username="abc", email="a@b.com", password="123")
