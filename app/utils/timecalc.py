from datetime import datetime

def parse_dt(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        raise ValueError(f"Érvénytelen dátum formátum: {value}. ISO 8601 szükséges.")
