from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from app.db.engine import get_db
from app.services.report_service import ReportService
from app.services.user_service import UserService
from app.utils.timecalc import parse_dt

bp = Blueprint("users", __name__)

@bp.get("/me")
@jwt_required()
def me():
    db = get_db()
    user_id = get_jwt_identity()
    service = UserService(db)

    user = service.get_user_by_id(user_id)
        
    return jsonify({
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role.value if hasattr(user.role, 'value') else str(user.role),
    })

@bp.get("/summary")
@jwt_required()
def get_summary():
    """
        Összefoglaló riport.
        Query paraméterek:
          - user_id: opcionális, ha nincs megadva, az aktuális user kerül felhasználásra
          - start_date: opcionális (YYYY-MM-DD)
          - end_date: opcionális (YYYY-MM-DD)
        """
    db = get_db()
    user_id = get_jwt_identity()
    service = ReportService(db)

    try:
        start_date = parse_dt(request.args.get("start_date"))
        end_date = parse_dt(request.args.get("end_date"))
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    summary = service.get_summary(
        user_id=user_id,
        start_date=start_date,
        end_date=end_date,
    )
    return jsonify(summary), 200

@bp.get("/overtime")
@jwt_required()
def get_user_overtime():
    """
    Egy felhasználó túlóráinak lekérdezése.
    Query paraméterek:
      - start_date: opcionális (YYYY-MM-DD)
      - end_date: opcionális (YYYY-MM-DD)
    """
    db = get_db()
    user_id = get_jwt_identity()
    service = ReportService(db)
    try:
        start_date = parse_dt(request.args.get("start_date"))
        end_date = parse_dt(request.args.get("end_date"))
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    records = service.get_user_overtime(
        user_id=user_id,
        start_date=start_date,
        end_date=end_date,
    )

    result = []
    for r in records:
        result.append(
            {
                "id": r.id,
                "user_id": r.user_id,
                "date": r.date.isoformat() if r.date else None,
                "check_in": r.check_in.isoformat() if r.check_in else None,
                "check_out": r.check_out.isoformat() if r.check_out else None,
                "work_duration_minutes": r.work_duration,
                "work_location": r.work_location.value if getattr(r, "work_location", None) else None,
            }
        )

    return jsonify(result), 200