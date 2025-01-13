from pony.orm import Database
from .models import db  # Должен быть импорт моделей

def init_db():
    db.bind(provider='sqlite', filename='hh_parser.db', create_db=True)
    db.generate_mapping(create_tables=True)