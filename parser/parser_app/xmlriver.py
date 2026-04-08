import requests
import time
import os
import logging
from datetime import datetime

# Настройка логирования
logging.basicConfig(
    filename='parser.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# БЕЗОПАСНОСТЬ: Чтение ключа из переменных окружения
KEY = os.environ.get('XMLRIVER_KEY')
USER_ID = os.environ.get('XMLRIVER_USER_ID')

if not KEY or not USER_ID:
    logger.warning("API ключи не найдены в переменных окружения! Проверьте .env файл.")
    # Для локального теста можно раскомментировать строку ниже, но НЕ в продакшене!
    # KEY = "ВАШ_КЛЮЧ" 

class XMLRiverParser:
    def __init__(self):
        self.base_url = "https://xmlriver.com/api/"
        self.delay_repeats = 0.5  # Увеличено до 0.5 сек для безопасности
        self.timeout = 30  # Таймаут запроса (секунды)

    def get_limits(self):
        """Проверка лимитов с обработкой ошибок"""
        if not KEY:
            return 0
        
        params = {
            'user': USER_ID,
            'key': KEY,
            'action': 'limits'
        }
        
        try:
            # ДОБАВЛЕНО: timeout и обработка исключений
            response = requests.get(self.base_url, params=params, timeout=self.timeout)
            response.raise_for_status()
            
            if response.status_code == 200:
                data = response.json()
                if 'limits' in data:
                    return int(data['limits'])
            logger.error(f"Ошибка получения лимитов: {response.status_code}")
            return 0
            
        except requests.exceptions.Timeout:
            logger.error("Таймаут при запросе лимитов")
            return 0
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка запроса лимитов: {e}")
            return 0

    def parse_query(self, query, region, depth, engine='yandex'):
        """Основной метод парсинга с защитой от сбоев"""
        if not KEY:
            raise Exception("API ключ не настроен")

        params = {
            'user': USER_ID,
            'key': KEY,
            'action': 'parse',
            'query': query,
            'region': region,
            'depth': depth,
            'engine': engine
        }

        retries = 3
        for attempt in range(retries):
            try:
                # ДОБАВЛЕНО: timeout
                response = requests.get(self.base_url, params=params, timeout=self.timeout)
                
                if response.status_code == 429:
                    wait_time = (attempt + 1) * 5
                    logger.warning(f"Превышение лимитов (429). Ждем {wait_time} сек...")
                    time.sleep(wait_time)
                    continue
                
                if response.status_code >= 500:
                    logger.error(f"Ошибка сервера XMLRiver: {response.status_code}")
                    time.sleep(2)
                    continue

                response.raise_for_status()
                data = response.json()
                
                if data.get('error'):
                    raise Exception(f"API Error: {data['error']}")
                    
                return data

            except requests.exceptions.Timeout:
                logger.warning(f"Таймаут запроса (попытка {attempt+1})")
                if attempt == retries - 1:
                    raise Exception("Превышено время ожидания ответа от XMLRiver")
                time.sleep(2)
            except Exception as e:
                logger.error(f"Критическая ошибка парсинга: {e}")
                if attempt == retries - 1:
                    raise e
                time.sleep(2)
        
        raise Exception("Не удалось выполнить запрос после нескольких попыток")