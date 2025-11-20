import pytest
from unittest.mock import MagicMock
from datetime import date
from app.services.report_service import ReportService
from app.utils.error_handler import ServiceError, NotFoundError, ValidationError
from app.db.models import WorkLocation
from sqlalchemy.exc import SQLAlchemyError


@pytest.fixture
def db():
    return MagicMock()

@pytest.fixture
def service(db):
    return ReportService(db)


# -----------------------------
# get_summary TESTS
# -----------------------------
def test_get_summary_success(service, db):
    record1 = MagicMock(work_duration=120, work_location=WorkLocation.OFFICE)
    record2 = MagicMock(work_duration=240, work_location=WorkLocation.HOME_OFFICE)

    query = MagicMock()
    query.filter.return_value = query
    query.all.return_value = [record1, record2]

    db.query.return_value = query

    result = service.get_summary(user_id=1)

    assert result["total_records"] == 2
    assert result["total_hours"] == 6.0
    assert result["home_office_days"] == 1
    assert result["office_days"] == 1
    assert result["home_office_ratio"] == "50.0%"


def test_get_summary_user_not_found(service, db):
    # mockolt query objektum
    query = MagicMock()
    query.filter.return_value = query
    query.all.return_value = []

    db.query.return_value = query

    with pytest.raises(NotFoundError):
        service.get_summary(user_id=999)


def test_get_summary_db_error(service, db):
    db.query.side_effect = SQLAlchemyError("db error")
    with pytest.raises(ServiceError):
        service.get_summary()

# -----------------------------
# get_user_overtime TESTS
# -----------------------------
def test_get_user_overtime_success(service, db):
    r1 = MagicMock()
    r2 = MagicMock()

    query = MagicMock()
    query.filter.return_value = query
    query.all.return_value = [r1, r2]
    db.query.return_value = query

    result = service.get_user_overtime(user_id=1)

    assert len(result) == 2


def test_get_user_overtime_missing_user_id(service):
    with pytest.raises(ValidationError):
        service.get_user_overtime(user_id=None)


def test_get_user_overtime_not_found(service, db):
    query = MagicMock()
    query.filter.return_value = query
    query.all.return_value = []
    db.query.return_value = query

    with pytest.raises(NotFoundError):
        service.get_user_overtime(user_id=1)



def test_get_user_overtime_db_error(service, db):
    db.query.side_effect = SQLAlchemyError("db fail")

    with pytest.raises(ServiceError):
        service.get_user_overtime(user_id=1)


# -----------------------------
# get_location_stats TESTS
# -----------------------------
def test_location_stats_success(service, db):
    # három külön query mock
    total_mock = MagicMock()
    total_mock.scalar.return_value = 10

    office_mock = MagicMock()
    office_mock.filter.return_value.scalar.return_value = 4

    home_mock = MagicMock()
    home_mock.filter.return_value.scalar.return_value = 6

    # db.query() return_value függvény szerint
    db.query.side_effect = [total_mock, office_mock, home_mock]

    result = service.get_location_stats()

    assert result["total_days"] == 10
    assert result["office_days"] == 4
    assert result["home_office_days"] == 6
    assert result["home_office_ratio"] == "60.0%"

def test_location_stats_zero_days(service, db):
    db.query().scalar.return_value = 0

    result = service.get_location_stats()

    assert result["total_days"] == 0
    assert result["home_office_ratio"] == "0%"

def test_location_stats_db_error(service, db):
    db.query().scalar.side_effect = SQLAlchemyError("fail")

    with pytest.raises(ServiceError):
        service.get_location_stats()