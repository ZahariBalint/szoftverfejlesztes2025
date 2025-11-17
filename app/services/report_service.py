from datetime import date

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.models import AttendanceRecord, WorkLocation
from app.utils.error_handler import ServiceError, NotFoundError, ValidationError

class ReportService:
    def __init__(self, db: Session):
        self.db = db

    def get_summary(self, user_id=None, start_date=None, end_date=None):
        """Riport lekérdezése időszakra és felhasználóra"""
        try:
            q = self.db.query(AttendanceRecord)

            if user_id:
                q = q.filter(AttendanceRecord.user_id == user_id)
            if start_date:
                q = q.filter(AttendanceRecord.date >= start_date)
            if end_date:
                q = q.filter(AttendanceRecord.date <= end_date)

            records = q.all()
            if user_id and not records:
                raise NotFoundError(f"Nem található rekord a user_id={user_id}-hez")

            total_minutes = sum(r.work_duration or 0 for r in records)
            total_hours = round(total_minutes / 60, 2)
            home_office_days = len([r for r in records if r.work_location == WorkLocation.HOME_OFFICE])
            office_days = len([r for r in records if r.work_location == WorkLocation.OFFICE])

            return {
                "total_records": len(records),
                "total_hours": total_hours,
                "home_office_days": home_office_days,
                "office_days": office_days,
                "home_office_ratio": f"{(home_office_days / len(records) * 100):.1f}%" if records else "0%",
            }
        except SQLAlchemyError:
            raise ServiceError("Adatbázis hiba a riport lekérdezés során")

    def get_user_overtime(self, user_id, start_date=None, end_date=None):
        """Felhasználó túlóráinak lekérdezése"""
        try:
            if not user_id:
                raise ValidationError("user_id megadása kötelező")

            q = self.db.query(AttendanceRecord).filter(
                AttendanceRecord.user_id == user_id,
                AttendanceRecord.is_overtime_generated == True)
            if start_date:
                q = q.filter(AttendanceRecord.date >= start_date)
            if end_date:
                q = q.filter(AttendanceRecord.date <= end_date)
            records = q.all()
            if not records:
                raise NotFoundError(f"Nincs túlóra rekord a user_id={user_id}-hez")

            return records

        except SQLAlchemyError:
            raise ServiceError("Adatbázis hiba a túlóra lekérdezés során")

    def get_location_stats(self):
        """Home office vs office napok arány statisztika"""
        try:
            total_days = self.db.query(func.count(AttendanceRecord.id)).scalar()
            office_days = self.db.query(func.count(AttendanceRecord.id)).filter(AttendanceRecord.work_location == WorkLocation.OFFICE).scalar()
            home_days = self.db.query(func.count(AttendanceRecord.id)).filter(AttendanceRecord.work_location == WorkLocation.HOME_OFFICE).scalar()

            return {
                "total_days": total_days or 0,
                "office_days": office_days or 0,
                "home_office_days": home_days or 0,
                "home_office_ratio": f"{(home_days / total_days * 100):.1f}%" if total_days else "0%",
            }
        except SQLAlchemyError:
            raise ServiceError("Adatbázis hiba a statisztika lekérdezés során")
