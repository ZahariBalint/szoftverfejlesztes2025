from datetime import datetime, date, timedelta
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from app.db.models import AttendanceRecord, OvertimeRequest, ModificationRequest, WorkLocation, RequestStatus, AuditLog
from typing import Dict, Any, Optional


class AttendanceService:
    def __init__(self, db: Session, current_user_id: int):
        self.db = db
        self.current_user_id = current_user_id

    # --- Munkaidő-nyilvántartás alapműveletek ---

    def check_in(self, work_location: WorkLocation = WorkLocation.OFFICE):
        """Felhasználó bejelentkezése"""
        existing_open = (
            self.db.query(AttendanceRecord)
            .filter(
                AttendanceRecord.user_id == self.current_user_id,
                AttendanceRecord.check_out.is_(None),
            )
            .first()
        )
        if existing_open:
            raise ValueError("Már van aktív munkamenet!")

        record = AttendanceRecord(
            user_id=self.current_user_id,
            check_in=datetime.now(),
            work_location=work_location,
            date=date.today(),
        )
        self.db.add(record)
        self.db.commit()
        self._log_action("check_in", entity_id=record.id, desc=f"{work_location.value}-ról bejelentkezett")
        return record

    def check_out(self, work_location: WorkLocation = WorkLocation.OFFICE):
        """Felhasználó kijelentkezése és munkaidő-számítás"""
        record = (
            self.db.query(AttendanceRecord)
            .filter(
                AttendanceRecord.user_id == self.current_user_id,
                AttendanceRecord.check_out.is_(None),
            )
            .first()
        )
        if not record:
            raise ValueError("Nincs aktív bejelentkezés.")

        record.check_out = datetime.now()
        record.work_location = work_location
        record.work_duration = record.calculate_duration()

        # túlóra detektálás (8 órán felül)
        if record.work_duration and record.work_duration > 480:
            overtime_minutes = record.work_duration - 480
            overtime = OvertimeRequest(
                user_id=self.current_user_id,
                work_session=record,
                overtime_minutes=overtime_minutes,
                status=RequestStatus.PENDING,
                is_auto_generated=True,
            )
            self.db.add(overtime)
            record.is_overtime_generated = True

        self.db.commit()
        self._log_action("check_out", entity_id=record.id, desc="Kijelentkezett")
        return record

    def get_weekly_attendance(self, week_start: Optional[date] = None) -> Dict[str, Any]:
        """Heti jelenléti adatok lekérése (hétfő-vasárnap)"""
        # Számítsuk ki az aktuális hét hétfő-vasárnap dátumát
        if week_start is None:
            today = date.today()
            days_since_monday = today.weekday()
            monday = today - timedelta(days=days_since_monday)
        else:
            # Ellenőrizzük, hogy a megadott dátum hétfő-e
            if week_start.weekday() != 0:
                # Ha nem hétfő, számítsuk ki a hétfőt
                days_since_monday = week_start.weekday()
                monday = week_start - timedelta(days=days_since_monday)
            else:
                monday = week_start
        sunday = monday + timedelta(days=6)
        
        # Jelenléti rekordok lekérése a hétre
        records = self.db.query(AttendanceRecord).filter(
            AttendanceRecord.user_id == self.current_user_id,
            AttendanceRecord.date >= monday,
            AttendanceRecord.date <= sunday
        ).order_by(AttendanceRecord.date, AttendanceRecord.check_in).all()
        
        # Aktív munkamenet ellenőrzése (csak ha a kért héten belül van)
        active_session = self.db.query(AttendanceRecord).filter(
            AttendanceRecord.user_id == self.current_user_id,
            AttendanceRecord.check_out.is_(None),
            AttendanceRecord.date >= monday,
            AttendanceRecord.date <= sunday
        ).first()
        
        # Rekordok napok szerint szervezése
        weekly_data = {}
        for i in range(7):  # Hétfő-vasárnap
            day_date = monday + timedelta(days=i)
            day_name = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'][i]
            weekly_data[day_name] = {
                'date': day_date.isoformat(),
                'sessions': []
            }
        
        for record in records:
            day_name = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'][record.date.weekday()]
            check_in_time = record.check_in.time() if record.check_in else None
            check_out_time = record.check_out.time() if record.check_out else None
            
            # Időtartam számítása percekben
            if record.check_out and record.check_in:
                duration = int((record.check_out - record.check_in).total_seconds() / 60)
            elif active_session and active_session.id == record.id:
                # Aktív munkamenet - aktuális időtartam számítása
                duration = int((datetime.now() - record.check_in).total_seconds() / 60)
            else:
                duration = 0
            
            weekly_data[day_name]['sessions'].append({
                'id': record.id,
                'check_in': record.check_in.isoformat() if record.check_in else None,
                'check_out': record.check_out.isoformat() if record.check_out else None,
                'check_in_time': check_in_time.strftime('%H:%M') if check_in_time else None,
                'check_out_time': check_out_time.strftime('%H:%M') if check_out_time else None,
                'duration_minutes': duration,
                'is_active': active_session and active_session.id == record.id
            })
        
        # Aktív munkamenet információk visszaadása, ha létezik
        active_info = None
        if active_session:
            current_duration = int((datetime.now() - active_session.check_in).total_seconds() / 60)
            active_info = {
                'id': active_session.id,
                'check_in': active_session.check_in.isoformat(),
                'check_in_time': active_session.check_in.time().strftime('%H:%M'),
                'duration_minutes': current_duration,
                'date': active_session.date.isoformat()
            }
        
        return {
            'week_start': monday.isoformat(),
            'week_end': sunday.isoformat(),
            'weekly_data': weekly_data,
            'active_session': active_info
        }

    # --- Módosítási kérelmek ---

    def request_modification(self, work_session_id: int, requested_check_in=None, requested_check_out=None, requested_location=None, reason=None):
        """Felhasználó kérelmezheti a munkamenet módosítását"""
        record = self.db.get(AttendanceRecord, work_session_id)
        if not record or record.user_id != self.current_user_id:
            raise ValueError("Nem található vagy nem saját rekord.")

        req = ModificationRequest(
            user_id=self.current_user_id,
            work_session_id=record.id,
            requested_check_in=requested_check_in,
            requested_check_out=requested_check_out,
            requested_work_location=requested_location,
            reason=reason or "Nincs megadva indoklás",
            status=RequestStatus.PENDING,
        )
        self.db.add(req)
        self.db.commit()
        self._log_action("request_modification", entity_id=req.id, desc="Módosítási kérelem beküldve")
        return req

    def review_modification(self, modification_id: int, approve: bool, reviewer_id: int, rejection_reason=None):
        """Admin jóváhagyja vagy elutasítja a módosítási kérelmet"""
        mod = self.db.get(ModificationRequest, modification_id)
        if not mod:
            raise ValueError("Nincs ilyen kérelem.")

        mod.reviewed_by = reviewer_id
        mod.reviewed_at = datetime.now()

        if approve:
            record = mod.work_session
            if mod.requested_check_in:
                record.check_in = mod.requested_check_in
            if mod.requested_check_out:
                record.check_out = mod.requested_check_out
                record.work_duration = record.calculate_duration()
            if mod.requested_work_location:
                record.work_location = mod.requested_work_location
            mod.status = RequestStatus.APPROVED
            desc = "Kérelem jóváhagyva"
        else:
            mod.status = RequestStatus.REJECTED
            mod.rejection_reason = rejection_reason or "Elutasítva indoklás nélkül"
            desc = "Kérelem elutasítva"

        self.db.commit()
        self._log_action("review_modification", entity_id=mod.id, desc=desc)
        return mod

    # --- Audit log segédfüggvény ---
    def _log_action(self, action: str, entity_id=None, desc=None):
        log = AuditLog(
            user_id=self.current_user_id,
            action=action,
            entity_type="attendance",
            entity_id=entity_id,
            description=desc,
        )
        self.db.add(log)
        self.db.commit()
