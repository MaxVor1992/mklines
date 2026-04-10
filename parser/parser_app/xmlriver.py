# -*- coding: utf-8 -*-
"""
Оптимизированный XMLRiver парсер с поддержкой асинхронности и таймаутами
"""
import requests
import time
import os
import logging
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from .resultobj import ParsingResult, SingleResult

# Настройка логирования
logging.basicConfig(
    filename='parser.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Чтение ключей из переменных окружения
KEY = os.environ.get('XMLRIVER_KEY', '9305a49e48a27d38f87261f26a6346f4d6508b6d')
USER_ID = os.environ.get('XMLRIVER_USER_ID', '3089')


class SearchParser:
    """Оптимизированный парсер для XMLRiver с поддержкой многопоточности"""
    
    YA = "http://xmlriver.com/search_yandex/xml"
    GOO = "http://xmlriver.com/search/xml"
    
    def __init__(self, user_requests, engine="yandex", count=10, repeats=1,
                 verbose=False, region="213", docache=True, max_workers=None):
        self.requests = user_requests
        self.system = engine
        self.region = region
        self.count = count
        self.repeats = repeats
        self.verbose = verbose
        self.docache = docache
        # ПРОБЛЕМА 2: Автоматический max_workers = min(кол-во запросов, 10)
        self.max_workers = min(len(user_requests), 10) if max_workers is None else max_workers
        self.delay_repeats = 0.1
        # ПРОБЛЕМА 1: Таймаут увеличен до 70 сек (с запасом на 60 сек max XMLRiver)
        self.timeout = 70

        # Кэш для результатов
        self._cache = {} if docache else None
        self._cache_time = {}
        self._cache_ttl = 12 * 3600  # 12 часов

    def _one_request(self, search_string: str, page=0):
        """Выполнение одного запроса к API с обработкой ошибок"""
        cache_key = f"{search_string}_{self.region}_{page}"
        
        # Проверка кэша
        if self._cache and cache_key in self._cache:
            cache_age = time.time() - self._cache_time.get(cache_key, 0)
            if cache_age < self._cache_ttl:
                logger.debug(f"Cache hit for: {search_string}")
                return self._cache[cache_key]
        
        base_link = self.YA if "yandex" in self.system else self.GOO
        
        if "yandex" in self.system:
            params = {
                "user": USER_ID,
                "key": KEY,
                "query": search_string,
                "groupby": f"attr=d.mode=deep.groups-on-page={self.count}.docs-in-group=3",
                "lr": self.region,
                "page": str(page)
            }
        else:
            params = {
                "user": USER_ID,
                "key": KEY,
                "query": search_string,
                "groupby": str(self.count),
                "lr": 143,
                "country": 2643,
                "page": str(page),
                "domain": 143
            }
        
        # ПРОБЛЕМА 3: Retry при таймауте — 3 попытки с нарастающей задержкой
        max_retries = 3
        last_error = None

        for retry in range(max_retries):
            try:
                response = requests.get(base_link, params=params, timeout=self.timeout)
                response.raise_for_status()

                # Сохранение в кэш
                if self._cache:
                    self._cache[cache_key] = response
                    self._cache_time[cache_key] = time.time()

                return response

            except requests.exceptions.Timeout:
                last_error = f"Таймаут запроса для: {search_string}"
                if retry < max_retries - 1:
                    wait = 5 * (retry + 1)  # 5с, 10с
                    logger.warning(f"Timeout for {search_string}, retry {retry+1}/{max_retries}, waiting {wait}s")
                    time.sleep(wait)
                else:
                    logger.error(f"Timeout for query after {max_retries} retries: {search_string}")
                    raise Exception(last_error)

            except requests.exceptions.RequestException as e:
                last_error = f"Request error for {search_string}: {e}"
                if retry < max_retries - 1:
                    wait = 3 * (retry + 1)
                    logger.warning(f"Request error for {search_string}, retry {retry+1}/{max_retries}, waiting {wait}s")
                    time.sleep(wait)
                else:
                    logger.error(f"Request error after {max_retries} retries: {search_string}")
                    raise Exception(last_error)

    def _parse_response(self, response, previous_results: dict):
        """Парсинг XML ответа"""
        if response.status_code != 200:
            logger.error(f"Bad status code: {response.status_code}")
            return
        
        from bs4 import BeautifulSoup
        # ПРОБЛЕМА 4: lxml вместо html5lib — в 3-5 раз быстрее, меньше памяти
        soup = BeautifulSoup(response.text, 'lxml')
        results = soup.find_all('results')
        
        if not results:
            errors = soup.find_all('error')
            if errors:
                error_msg = errors[0].contents[0] if errors[0].contents else "unknown error"
                previous_results[SingleResult(str(error_msg), "error")] = [0]
            else:
                previous_results[SingleResult("no results", "error")] = [0]
            return
        
        content = results[0]
        groups = content.find_all('group')
        c = len(previous_results.keys())
        
        for group in groups:
            c += 1
            doc = group.doc
            url = doc.url.text if doc.url else ""
            title = doc.title.text if doc.title else ""
            
            if url and url != "error":
                single_result = SingleResult(url, title)
                previous_results.setdefault(single_result, []).append(c)
                
                if c >= self.count:
                    break

    def _parse_single_query(self, text):
        """Парсинг одного запроса с повторами"""
        d = {}
        
        for i in range(self.repeats):
            try:
                response = self._one_request(text, page=0)
                self._parse_response(response, d)
                time.sleep(self.delay_repeats)
            except Exception as e:
                logger.error(f"Error parsing query '{text}': {e}")
                continue
        
        # Усреднение позиций
        for k in d:
            d[k] = sum(d[k]) / len(d[k])
        
        return sorted(d.items(), key=lambda x: x[1])

    def run_parse(self):
        """Запуск парсинга с использованием ThreadPoolExecutor"""
        logger.info(f"Starting parse: {len(self.requests)} queries, engine={self.system}")
        results = ParsingResult(self.system)
        
        # Ограничение количества одновременных запросов
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Отправляем все задачи на выполнение
            future_to_query = {
                executor.submit(self._parse_single_query, text): text 
                for text in self.requests
            }
            
            # Получаем результаты по мере завершения
            for future in as_completed(future_to_query):
                query = future_to_query[future]
                try:
                    parsed_results = future.result()
                    results.result[query] = parsed_results
                    logger.info(f"Completed query: {query}")
                except Exception as e:
                    logger.error(f"Failed query '{query}': {e}")
                    results.result[query] = [(SingleResult("error", str(e)), 0)]
        
        logger.info(f"Parsing completed: {len(results.result)} results")
        return results
