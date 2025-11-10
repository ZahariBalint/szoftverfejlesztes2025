from sqlalchemy import and_
from datetime import datetime, date
from typing import List, Optional, Dict, Any
from app.db.engine import db
from app.db.models import (
    User, AttendanceRecord, OvertimeRequest, ModificationRequest,
    AuditLog, SystemSettings, UserRole, WorkLocation, RequestStatus
)

# ==================== USER CRUD ====================

def create_user(username: str, email: str, password_hash: str,
                role: UserRole = UserRole.USER) -> User:
    """Új felhasználó létrehozása."""
    user = User(
        username=username,
        email=email,
        password_hash=password_hash,
        role=role
    )
    db.session.add(user)
    db.session.commit()
    return user


def get_user_by_id(user_id: int) -> Optional[User]:
    """Felhasználó lekérése ID alapján."""
    return db.session.query(User).filter(User.id == user_id).first()


def get_user_by_username(username: str) -> Optional[User]:
    """Felhasználó lekérése felhasználónév alapján."""
    return db.session.query(User).filter(User.username == username).first()


def get_user_by_email(email: str) -> Optional[User]:
    """Felhasználó lekérése email alapján."""
    return db.session.query(User).filter(User.email == email).first()


def get_all_users(skip: int = 0, limit: int = 100, active_only: bool = True) -> List[User]:
    """Összes felhasználó lekérése."""
    query = db.session.query(User)
    if active_only:
        query = query.filter(User.is_active == True)
    return query.offset(skip).limit(limit).all()


def update_user(user_id: int, **kwargs) -> Optional[User]:
    """Felhasználó adatainak frissítése."""
    user = get_user_by_id(user_id)
    if user:
        for key, value in kwargs.items():
            if hasattr(user, key):
                setattr(user, key, value)
        db.session.commit()
    return user


def delete_user(user_id: int, soft_delete: bool = True) -> bool:
    """Felhasználó törlése (soft delete vagy hard delete)."""
    user = get_user_by_id(user_id)
    if user:
        if soft_delete:
            user.is_active = False
            db.session.commit()
        else:
            db.session.delete(user)
            db.session.commit()
        return True
    return False


# ==================== ATTENDANCE RECORD CRUD ====================

def create_attendance_record(user_id: int, check_in: datetime,
                             work_location: WorkLocation = WorkLocation.OFFICE) -> AttendanceRecord:
    """Új jelenlét rekord létrehozása (bejelentkezés)."""
    record = AttendanceRecord(
        user_id=user_id,
        check_in=check_in,
        work_location=work_location,
        date=check_in.date()
    )
    db.session.add(record)
    db.session.commit()
    return record


def check_in_user(user_id: int, work_location: WorkLocation = WorkLocation.OFFICE) -> AttendanceRecord:
    """Felhasználó bejelentkezése (check-in)."""
    return create_attendance_record(user_id, datetime.now(), work_location)


def check_out_user(record_id: int, check_out: Optional[datetime] = None) -> Optional[AttendanceRecord]:
    """Felhasználó kijelentkezése (check-out)."""
    record = db.session.query(AttendanceRecord).filter(AttendanceRecord.id == record_id).first()
    if record and not record.check_out:
        record.check_out = check_out or datetime.now()
        record.work_duration = record.calculate_duration()
        db.session.commit()
    return record


def get_active_attendance(user_id: int) -> Optional[AttendanceRecord]:
    """Aktív jelenlét rekord lekérése (még nincs check_out)."""
    return db.session.query(AttendanceRecord).filter(
        and_(
            AttendanceRecord.user_id == user_id,
            AttendanceRecord.check_out.is_(None)
        )
    ).first()


def get_attendance_records_by_user(user_id: int,
                                   start_date: Optional[date] = None,
                                   end_date: Optional[date] = None) -> List[AttendanceRecord]:
    """Felhasználó jelenlét rekordjai dátum tartomány szerint."""
    query = db.session.query(AttendanceRecord).filter(AttendanceRecord.user_id == user_id)

    if start_date:
        query = query.filter(AttendanceRecord.date >= start_date)
    if end_date:
        query = query.filter(AttendanceRecord.date <= end_date)

    return query.order_by(AttendanceRecord.check_in.desc()).all()


def get_attendance_records_by_date(target_date: date) -> List[AttendanceRecord]:
    """Adott napi jelenlét rekordok lekérése."""
    return db.session.query(AttendanceRecord).filter(AttendanceRecord.date == target_date).all()


def get_attendance_record_by_id(record_id: int) -> Optional[AttendanceRecord]:
    """Jelenlét rekord lekérése ID alapján."""
    return db.session.query(AttendanceRecord).filter(AttendanceRecord.id == record_id).first()


def update_attendance_record(record_id: int, **kwargs) -> Optional[AttendanceRecord]:
    """Jelenlét rekord módosítása."""
    record = get_attendance_record_by_id(record_id)
    if record:
        for key, value in kwargs.items():
            if hasattr(record, key):
                setattr(record, key, value)

        # Időtartam újraszámítása, ha szükséges
        if 'check_in' in kwargs or 'check_out' in kwargs:
            record.work_duration = record.calculate_duration()

        db.session.commit()
    return record


# ==================== OVERTIME REQUEST CRUD ====================

def create_overtime_request(user_id: int, overtime_minutes: int,
                            work_session_id: Optional[int] = None,
                            is_auto_generated: bool = False) -> OvertimeRequest:
    """Túlóra kérelem létrehozása."""
    request = OvertimeRequest(
        user_id=user_id,
        overtime_minutes=overtime_minutes,
        work_session_id=work_session_id,
        is_auto_generated=is_auto_generated
    )
    db.session.add(request)
    db.session.commit()
    return request


def get_overtime_request_by_id(request_id: int) -> Optional[OvertimeRequest]:
    """Túlóra kérelem lekérése ID alapján."""
    return db.session.query(OvertimeRequest).filter(OvertimeRequest.id == request_id).first()


def get_pending_overtime_requests(user_id: Optional[int] = None) -> List[OvertimeRequest]:
    """Függőben lévő túlóra kérelmek."""
    query = db.session.query(OvertimeRequest).filter(OvertimeRequest.status == RequestStatus.PENDING)
    if user_id:
        query = query.filter(OvertimeRequest.user_id == user_id)
    return query.order_by(OvertimeRequest.request_date.desc()).all()


def get_overtime_requests_by_user(user_id: int, status: Optional[RequestStatus] = None) -> List[OvertimeRequest]:
    """Felhasználó túlóra kérelmei."""
    query = db.session.query(OvertimeRequest).filter(OvertimeRequest.user_id == user_id)
    if status:
        query = query.filter(OvertimeRequest.status == status)
    return query.order_by(OvertimeRequest.request_date.desc()).all()


def approve_overtime_request(request_id: int, reviewer_id: int) -> Optional[OvertimeRequest]:
    """Túlóra kérelem jóváhagyása."""
    request = get_overtime_request_by_id(request_id)
    if request and request.status == RequestStatus.PENDING:
        request.status = RequestStatus.APPROVED
        request.reviewed_by = reviewer_id
        request.reviewed_at = datetime.now()
        db.session.commit()
    return request


def reject_overtime_request(request_id: int, reviewer_id: int, reason: str) -> Optional[OvertimeRequest]:
    """Túlóra kérelem elutasítása."""
    request = get_overtime_request_by_id(request_id)
    if request and request.status == RequestStatus.PENDING:
        request.status = RequestStatus.REJECTED
        request.reviewed_by = reviewer_id
        request.reviewed_at = datetime.now()
        request.rejection_reason = reason
        db.session.commit()
    return request


# ==================== MODIFICATION REQUEST CRUD ====================

def create_modification_request(user_id: int, work_session_id: int,
                                reason: str, **changes) -> ModificationRequest:
    """Jelenlét rekord módosítási kérelem létrehozása."""
    request = ModificationRequest(
        user_id=user_id,
        work_session_id=work_session_id,
        reason=reason,
        requested_check_in=changes.get('check_in'),
        requested_check_out=changes.get('check_out'),
        requested_work_location=changes.get('work_location')
    )
    db.session.add(request)
    db.session.commit()
    return request


def get_modification_request_by_id(request_id: int) -> Optional[ModificationRequest]:
    """Módosítási kérelem lekérése ID alapján."""
    return db.session.query(ModificationRequest).filter(ModificationRequest.id == request_id).first()


def get_pending_modification_requests(user_id: Optional[int] = None) -> List[ModificationRequest]:
    """Függőben lévő módosítási kérelmek."""
    query = db.session.query(ModificationRequest).filter(ModificationRequest.status == RequestStatus.PENDING)
    if user_id:
        query = query.filter(ModificationRequest.user_id == user_id)
    return query.order_by(ModificationRequest.created_at.desc()).all()


def get_modification_requests_by_user(user_id: int, status: Optional[RequestStatus] = None) -> List[
    ModificationRequest]:
    """Felhasználó módosítási kérelmei."""
    query = db.session.query(ModificationRequest).filter(ModificationRequest.user_id == user_id)
    if status:
        query = query.filter(ModificationRequest.status == status)
    return query.order_by(ModificationRequest.created_at.desc()).all()


def approve_modification_request(request_id: int, reviewer_id: int) -> Optional[ModificationRequest]:
    """Módosítási kérelem jóváhagyása és alkalmazása."""
    request = get_modification_request_by_id(request_id)
    if request and request.status == RequestStatus.PENDING:
        # Jelenlét rekord módosítása
        record = request.work_session
        if request.requested_check_in:
            record.check_in = request.requested_check_in
        if request.requested_check_out:
            record.check_out = request.requested_check_out
        if request.requested_work_location:
            record.work_location = request.requested_work_location

        # Időtartam újraszámítása
        record.work_duration = record.calculate_duration()

        # Kérelem jóváhagyása
        request.status = RequestStatus.APPROVED
        request.reviewed_by = reviewer_id
        request.reviewed_at = datetime.now()

        db.session.commit()
    return request


def reject_modification_request(request_id: int, reviewer_id: int, reason: str) -> Optional[ModificationRequest]:
    """Módosítási kérelem elutasítása."""
    request = get_modification_request_by_id(request_id)
    if request and request.status == RequestStatus.PENDING:
        request.status = RequestStatus.REJECTED
        request.reviewed_by = reviewer_id
        request.reviewed_at = datetime.now()
        request.rejection_reason = reason
        db.session.commit()
    return request


# ==================== AUDIT LOG CRUD ====================

def create_audit_log(action: str, user_id: Optional[int] = None,
                     entity_type: Optional[str] = None, entity_id: Optional[int] = None,
                     description: Optional[str] = None, ip_address: Optional[str] = None) -> AuditLog:
    """Audit log bejegyzés létrehozása."""
    log = AuditLog(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        description=description,
        ip_address=ip_address
    )
    db.session.add(log)
    db.session.commit()
    return log


def get_audit_logs(user_id: Optional[int] = None,
                   action: Optional[str] = None,
                   start_date: Optional[datetime] = None,
                   limit: int = 100) -> List[AuditLog]:
    """Audit logok lekérése szűrési feltételekkel."""
    query = db.session.query(AuditLog)

    if user_id:
        query = query.filter(AuditLog.user_id == user_id)
    if action:
        query = query.filter(AuditLog.action == action)
    if start_date:
        query = query.filter(AuditLog.created_at >= start_date)

    return query.order_by(AuditLog.created_at.desc()).limit(limit).all()


# ==================== SYSTEM SETTINGS CRUD ====================

def get_setting(key: str) -> Optional[str]:
    """Rendszerbeállítás lekérése."""
    setting = db.session.query(SystemSettings).filter(SystemSettings.key == key).first()
    return setting.value if setting else None


def set_setting(key: str, value: str, updated_by: int, description: Optional[str] = None) -> SystemSettings:
    """Rendszerbeállítás mentése vagy módosítása."""
    setting = db.session.query(SystemSettings).filter(SystemSettings.key == key).first()

    if setting:
        setting.value = value
        setting.updated_by = updated_by
        if description:
            setting.description = description
    else:
        setting = SystemSettings(
            key=key,
            value=value,
            description=description,
            updated_by=updated_by
        )
        db.session.add(setting)

    db.session.commit()
    return setting


def get_all_settings() -> List[SystemSettings]:
    """Összes rendszerbeállítás lekérése."""
    return db.session.query(SystemSettings).all()


# ==================== STATISTICS / REPORTS ====================

def get_user_work_hours_summary(user_id: int, start_date: date, end_date: date) -> Dict[str, Any]:
    """Felhasználó munkaidő összesítés egy időszakra."""
    records = get_attendance_records_by_user(user_id, start_date, end_date)

    total_minutes = sum(r.work_duration or 0 for r in records)
    office_days = sum(1 for r in records if r.work_location == WorkLocation.OFFICE)
    home_office_days = sum(1 for r in records if r.work_location == WorkLocation.HOME_OFFICE)

    return {
        "user_id": user_id,
        "period": {"start": start_date.isoformat(), "end": end_date.isoformat()},
        "total_hours": round(total_minutes / 60, 2),
        "total_days": len(records),
        "office_days": office_days,
        "home_office_days": home_office_days,
        "other_days": len(records) - office_days - home_office_days
    }


def get_daily_summary(target_date: date) -> Dict[str, Any]:
    """Napi összesítés - hány user dolgozott, összesen hány óra."""
    records = get_attendance_records_by_date(target_date)

    total_minutes = sum(r.work_duration or 0 for r in records if r.work_duration)
    unique_users = len(set(r.user_id for r in records))

    return {
        "date": target_date.isoformat(),
        "total_users": unique_users,
        "total_hours": round(total_minutes / 60, 2),
        "total_records": len(records)
    }