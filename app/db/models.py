from datetime import datetime
from enum import Enum as PyEnum
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Enum, Date
from sqlalchemy.orm import relationship
from app.db.base import Base
from sqlalchemy.sql import func


# Enumok definiálása
class UserRole(PyEnum):
    USER = "user"
    ADMIN = "admin"


class WorkLocation(PyEnum):
    OFFICE = "office"
    HOME_OFFICE = "home_office"
    OTHER = "other"


class RequestStatus(PyEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False, index=True)
    email = Column(String(120), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    # Kapcsolatok
    work_sessions = relationship("AttendanceRecord", back_populates="user", foreign_keys="AttendanceRecord.user_id")
    overtime_requests = relationship("OvertimeRequest", back_populates="requester", foreign_keys="OvertimeRequest.user_id")
    reviewed_overtime_requests = relationship("OvertimeRequest", back_populates="reviewer", foreign_keys="OvertimeRequest.reviewed_by")
    modification_requests = relationship("ModificationRequest", back_populates="requester", foreign_keys="ModificationRequest.user_id")
    reviewed_modification_requests = relationship("ModificationRequest", back_populates="reviewer", foreign_keys="ModificationRequest.reviewed_by")
    audit_logs = relationship("AuditLog", back_populates="user")
    system_settings_updates = relationship("SystemSettings", back_populates="updated_by_user")

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', role='{self.role.value}')>"


class AttendanceRecord(Base):
    __tablename__ = 'work_sessions'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    check_in = Column(DateTime, nullable=False, index=True)
    check_out = Column(DateTime, nullable=True)
    work_location = Column(Enum(WorkLocation), default=WorkLocation.OFFICE, nullable=False)
    work_duration = Column(Integer, nullable=True)  # minutes
    date = Column(Date, nullable=False, index=True)
    is_overtime_generated = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    # Kapcsolatok
    user = relationship("User", back_populates="work_sessions", foreign_keys=[user_id])
    overtime_request = relationship("OvertimeRequest", back_populates="work_session", uselist=False)
    modification_requests = relationship("ModificationRequest", back_populates="work_session")

    def calculate_duration(self):
        """Kiszámolja a munkaidőt percekben."""
        if self.check_out and self.check_in:
            delta = self.check_out - self.check_in
            return int(delta.total_seconds() / 60)
        return None

    def __repr__(self):
        return f"<AttendanceRecord(id={self.id}, user_id={self.user_id}, date={self.date}, duration={self.work_duration}min)>"


class OvertimeRequest(Base):
    __tablename__ = 'overtime_requests'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    work_session_id = Column(Integer, ForeignKey('work_sessions.id'), nullable=True, index=True)
    overtime_minutes = Column(Integer, nullable=False)
    request_date = Column(DateTime, default=func.now(), nullable=False)
    status = Column(Enum(RequestStatus), default=RequestStatus.PENDING, nullable=False, index=True)
    reviewed_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    rejection_reason = Column(Text, nullable=True)
    is_auto_generated = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    # Kapcsolatok
    requester = relationship("User", back_populates="overtime_requests", foreign_keys=[user_id])
    reviewer = relationship("User", back_populates="reviewed_overtime_requests", foreign_keys=[reviewed_by])
    work_session = relationship("AttendanceRecord", back_populates="overtime_request")

    def __repr__(self):
        return f"<OvertimeRequest(id={self.id}, user_id={self.user_id}, minutes={self.overtime_minutes}, status='{self.status.value}')>"


class ModificationRequest(Base):
    __tablename__ = 'modification_requests'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    work_session_id = Column(Integer, ForeignKey('work_sessions.id'), nullable=False, index=True)
    requested_check_in = Column(DateTime, nullable=True)
    requested_check_out = Column(DateTime, nullable=True)
    requested_work_location = Column(Enum(WorkLocation), nullable=True)
    reason = Column(Text, nullable=False)
    status = Column(Enum(RequestStatus), default=RequestStatus.PENDING, nullable=False, index=True)
    reviewed_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    rejection_reason = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    # Kapcsolatok
    requester = relationship("User", back_populates="modification_requests", foreign_keys=[user_id])
    reviewer = relationship("User", back_populates="reviewed_modification_requests", foreign_keys=[reviewed_by])
    work_session = relationship("AttendanceRecord", back_populates="modification_requests")

    def __repr__(self):
        return f"<ModificationRequest(id={self.id}, user_id={self.user_id}, work_session_id={self.work_session_id}, status='{self.status.value}')>"


class AuditLog(Base):
    __tablename__ = 'audit_logs'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True, index=True)
    action = Column(String(100), nullable=False, index=True)
    entity_type = Column(String(50), nullable=True)
    entity_id = Column(Integer, nullable=True)
    description = Column(Text, nullable=True)
    ip_address = Column(String(45), nullable=True)  # IPv6 support
    created_at = Column(DateTime, default=func.now(), nullable=False, index=True)

    # Kapcsolatok
    user = relationship("User", back_populates="audit_logs")

    def __repr__(self):
        return f"<AuditLog(id={self.id}, action='{self.action}', user_id={self.user_id}, created_at={self.created_at})>"


class SystemSettings(Base):
    __tablename__ = 'system_settings'

    id = Column(Integer, primary_key=True)
    key = Column(String(100), unique=True, nullable=False, index=True)
    value = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    updated_by = Column(Integer, ForeignKey('users.id'), nullable=True)

    # Kapcsolatok
    updated_by_user = relationship("User", back_populates="system_settings_updates")

    def __repr__(self):
        return f"<SystemSettings(id={self.id}, key='{self.key}', value='{self.value}')>"