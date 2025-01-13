# src/parser/hh_parser.py
import aiohttp
import asyncio
from bs4 import BeautifulSoup
from datetime import datetime
from ..config import HEADERS, REQUEST_DELAY, MAX_RETRIES, BASE_URL

class HHParser:
    def __init__(self):
        self.base_url = BASE_URL

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()

    async def fetch_page(self, url):
        """Делает запрос к странице. Повторяет, если ошибка."""
        for attempt in range(MAX_RETRIES):
            try:
                async with self.session.get(url, headers=HEADERS) as response:
                    text = await response.text()
                    # Задержка между запросами
                    await asyncio.sleep(REQUEST_DELAY)
                    return text
            except Exception as e:
                if attempt < MAX_RETRIES - 1:
                    await asyncio.sleep(1)
                else:
                    raise e

    async def parse_vacancies(self, query, region, page=0):
        """
        Парсит одну страницу результатов поиска вакансий
        (query — например, "python",
         region — номер региона, page — номер страницы).
        """
        url = f"{self.base_url}/search/vacancy?text={query}&area={region}&page={page}"
        page_content = await self.fetch_page(url)
        soup = BeautifulSoup(page_content, 'html.parser')

        vacancy_blocks = soup.find_all('div', class_='vacancy-serp-item')
        results = []
        for block in vacancy_blocks:
            vac_data = self.parse_vacancy_block(block)
            if vac_data:
                results.append(vac_data)
        return results

    def parse_vacancy_block(self, block):
        """Разбирает один блок вакансии, достаёт название, ссылку, зарплату, компанию и т.д."""
        title_element = block.find('a', {'data-qa': 'serp-item__title'})
        if not title_element:
            return None

        title = title_element.get_text(strip=True)
        url = title_element['href']

        # Пример: ищем блок зарплаты
        salary_element = block.find('span', {'data-qa': 'vacancy-serp__vacancy-compensation'})
        salary_text = salary_element.get_text(strip=True) if salary_element else None

        # Пример: ищем компанию
        company_element = block.find('a', {'data-qa': 'vacancy-serp__vacancy-employer'})
        company_name = company_element.get_text(strip=True) if company_element else "Не указано"
        company_url = company_element.get('href') if company_element else None

        # Опыт
        experience_element = block.find('div', {'data-qa': 'vacancy-serp__vacancy-experience'})
        experience_name = experience_element.get_text(strip=True) if experience_element else "Не указано"

        # Дата публикации (иногда hh.kz имеет разные форматы)
        published_at = datetime.now()  # упрощённо

        # Здесь же можно распарсить зарплату ( salary_min, salary_max, salary_currency ) — отдельной логикой.

        return {
            'title': title,
            'url': url,
            'salary_text': salary_text,
            'company_name': company_name,
            'company_url': company_url,
            'experience_name': experience_name,
            'published_at': published_at,
            # и т.д. (позже сохраним в БД)
        }

    async def gather_all_vacancies(self, query="python", region=160, max_pages=2):
        """
        Обходит несколько страниц (от 0 до max_pages-1), собирает все вакансии в один список.
        """
        all_vacancies = []
        for page in range(max_pages):
            page_data = await self.parse_vacancies(query, region, page)
            if not page_data:
                break
            all_vacancies.extend(page_data)
        return all_vacancies


from pony.orm import db_session
from datetime import datetime
from ..models import Vacancy, Company, Experience, EmploymentType


@db_session
def save_vacancy(v_data):
    """
    Сохраняет одну вакансию в базу (или обновляет, если уже есть).
    """
    # Сначала создаём/находим компанию
    company = Company.get(name=v_data['company_name'])
    if not company:
        company = Company(name=v_data['company_name'], url=v_data['company_url'])

    # Аналогично для Experience:
    experience = Experience.get(name=v_data['experience_name'])
    if not experience:
        experience = Experience(name=v_data['experience_name'])

    # Для EmploymentType (в примере не извлекали — можно захардкодить "Полная занятость" или парсить)
    employment_type = EmploymentType.get(name="Полная занятость")
    if not employment_type:
        employment_type = EmploymentType(name="Полная занятость")

    # Используем ссылку (url) в качестве external_id (или, если есть ID вакансии в HTML, достаём его)
    external_id = v_data['url']

    vacancy = Vacancy.get(external_id=external_id)
    if not vacancy:
        # Создаём новую
        vacancy = Vacancy(
            external_id=external_id,
            title=v_data['title'],
            company=company,
            salary_min=None,  # Тут можно распарсить salary_text и присвоить
            salary_max=None,
            salary_currency=None,
            experience=experience,
            employment_type=employment_type,
            description="",
            requirements="",
            published_at=v_data['published_at'],
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
    else:
        # Обновляем существующую
        vacancy.title = v_data['title']
        vacancy.updated_at = datetime.now()

    return vacancy