# src/config.py

BASE_URL = "https://hh.kz"
HEADERS = {
    "User-Agent": "MySuperParserBot/1.0"
}
REQUEST_DELAY = 2  # задержка между запросами, чтобы не слишком спамить
MAX_RETRIES = 3    # сколько раз повторим запрос при ошибке