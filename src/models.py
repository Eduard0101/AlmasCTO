from pony.orm import Database, Required, Optional, PrimaryKey, Set
from datetime import datetime

# Создаём объект базы данных
db = Database()

# Модель компании
class Company(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str)
    url = Optional(str)
    vacancies = Set('Vacancy')

# Модель опыта работы
class Experience(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str)
    vacancies = Set('Vacancy')

# Модель типа занятости (полная, частичная и т. д.)
class EmploymentType(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str)
    vacancies = Set('Vacancy')

# Модель вакансии
class Vacancy(db.Entity):
    id = PrimaryKey(int, auto=True)
    title = Required(str)
    company = Required(Company)
    salary = Optional(str)
    experience = Required(Experience)
    employment_type = Required(EmploymentType)
    description = Optional(str)
    requirements = Optional(str)
    published_at = Required(datetime)
    url = Required(str)

# Связываем базу с SQLite (файл hh_parser.db создастся автоматически)
db.bind(provider='sqlite', filename='hh_parser.db', create_db=True)
db.generate_mapping(create_tables=True)
