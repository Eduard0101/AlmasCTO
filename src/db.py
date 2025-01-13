from pony.orm import db_session
from src.models import db  # Импортируем модели

# Функция инициализации базы
def init_db():
    if not db.provider:  # Проверяем, привязана ли база
        db.bind(provider='sqlite', filename='hh_parser.db', create_db=True)
        db.generate_mapping(create_tables=True)


# Функция для очистки базы (на случай отладки)
@db_session
def clear_db():
    db.drop_all_tables(with_all_data=True)
    db.create_tables()

# Запускаем инициализацию базы при запуске файла
if __name__ == "__main__":
    init_db()
    print("База данных успешно инициализирована!")
