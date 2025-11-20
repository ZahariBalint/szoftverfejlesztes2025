import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, date, timedelta

from sqlalchemy.exc import SQLAlchemyError

from app.services.attendance_service import AttendanceService
from app.utils.error_handler import ValidationError, NotFoundError, ForbiddenError, ServiceError
from app.db.models import AttendanceRecord, WorkLocation, ModificationRequest, RequestStatus, AuditLog
from app.utils.error_handler import ServiceError


# --- Helper: create fake AttendanceRecord ---
def make_record(user_id=1, check_in=None, check_out=None, date_value=None):
    r = AttendanceRecord(
        id=1,
        user_id=user_id,
        check_in=check_in,
        check_out=check_out,
        date=date_value or date.today()
    )
    # mock duration calc
    r.calculate_duration = lambda: 480
    return r


# --- FIXTURE: fake DB session ---
@pytest.fixture
def db():
    return MagicMock()


@pytest.fixture
def service(db):
    return AttendanceService(db=db, current_user_id=1)


# ===========================================================
# CHECK-IN TESTS
# ===========================================================

def test_check_in_success(service, db):
    db.query().filter().first.return_value = None  # No active session

    record = service.check_in()

    db.add.assert_called()
    db.commit.assert_called()
    assert isinstance(record.date, date)


def test_check_in_when_active_session_exists(service, db):
    db.query().filter().first.return_value = make_record()  # Active session

    with pytest.raises(ValidationError):
        service.check_in()


def test_check_in_database_error(service, db):
    db.query().filter().first.return_value = None
    db.commit.side_effect = SQLAlchemyError("db fail")

    with pytest.raises(ServiceError):
        service.check_in()

    db.rollback.assert_called()


# ===========================================================
# CHECK-OUT TESTS
# ===========================================================

def test_check_out_success(service, db):
    record = make_record(check_in=datetime.now() - timedelta(hours=8))
    db.query().filter().first.return_value = record

    result = service.check_out()

    db.commit.assert_called()
    assert result.check_out is not None


def test_check_out_no_active_session(service, db):
    db.query().filter().first.return_value = None

    with pytest.raises(ValidationError):
        service.check_out()


def test_check_out_overtime_generated(service, db):
    record = make_record(check_in=datetime.now() - timedelta(hours=10))
    record.calculate_duration = lambda: 600  # 10 hours → overtime
    db.query().filter().first.return_value = record

    service.check_out()

    assert record.is_overtime_generated is True
    db.add.assert_called()  # OvertimeRequest created


def test_check_out_database_error(service, db):
    record = make_record(check_in=datetime.now())
    db.query().filter().first.return_value = record
    db.commit.side_effect = SQLAlchemyError("db error")

    with pytest.raises(ServiceError):
        service.check_out()

    db.rollback.assert_called()


# ===========================================================
# REQUEST MODIFICATION
# ===========================================================

def test_request_modification_success(service, db):
    record = make_record()
    db.get.return_value = record

    service.request_modification(1)

    db.add.assert_called()
    db.commit.assert_called()


def test_request_modification_not_found(service, db):
    db.get.return_value = None

    with pytest.raises(NotFoundError):
        service.request_modification(1)


def test_request_modification_forbidden(service, db):
    db.get.return_value = make_record(user_id=2)  # other user's record

    with pytest.raises(ForbiddenError):
        service.request_modification(1)


# ===========================================================
# REVIEW MODIFICATION
# ===========================================================

def test_review_modification_approve(service, db):
    mod = MagicMock(spec=ModificationRequest)
    mod.requested_check_in = datetime.now()
    mod.requested_check_out = datetime.now()
    mod.requested_work_location = WorkLocation.OFFICE
    mod.work_session = make_record()
    db.get.return_value = mod

    service.review_modification(1, approve=True, reviewer_id=99)

    assert mod.status == RequestStatus.APPROVED
    db.commit.assert_called()


def test_review_modification_reject(service, db):
    mod = MagicMock(spec=ModificationRequest)
    mod.work_session = make_record()
    db.get.return_value = mod

    service.review_modification(1, approve=False, reviewer_id=99, rejection_reason="Nope")

    assert mod.status == RequestStatus.REJECTED
    assert mod.rejection_reason == "Nope"


def test_review_modification_not_found(service, db):
    db.get.return_value = None

    with pytest.raises(NotFoundError):
        service.review_modification(1, approve=True, reviewer_id=99)