# src/models.py
from pony.orm import Database, Required, Optional, PrimaryKey, Set
from datetime import datetime

db = Database()

class Company(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str)
    url = Optional(str)
    vacancies = Set('Vacancy')

class Experience(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str)
    vacancies = Set('Vacancy')

class EmploymentType(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str)
    vacancies = Set('Vacancy')

class Vacancy(db.Entity):
    id = PrimaryKey(int, auto=True)
    external_id = Required(str, unique=True)
    title = Required(str)
    company = Required(Company)
    salary_min = Optional(int)
    salary_max = Optional(int)
    salary_currency = Optional(str)
    experience = Required(Experience)
    employment_type = Required(EmploymentType)
    description = Optional(str)
    requirements = Optional(str)
    published_at = Required(datetime)
    url = Required(str)
    created_at = Required(datetime, default=datetime.now)
    updated_at = Required(datetime, default=datetime.now)
