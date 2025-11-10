from flask_sqlalchemy import SQLAlchemy
from .base import Base
from .models import * # Modellek betöltése

# Flask-SQLAlchemy inicializálás
db = SQLAlchemy()

def init_db():
    db.create_all()