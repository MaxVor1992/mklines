# -*- coding: utf-8 -*-
"""
Оптимизированный парсер для Yandex XML API
С поддержкой многопоточности, кэширования и обработки ошибок
"""
import time
import bs4
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from .resultobj import SingleResult, ParsingResult
from .utils import print_error
from .for_cache import timed_lru_cache
from flask_login import current_user
from . import db
import logging

logger = logging.getLogger(__name__)

# Ключи Yandex XML (для тестирования)
YANDEX_XML_USER = "igor-exist"  # test
YANDEX_XML_KEY = "03.17714018:ae35c9b26c7d4281b1e85311811a277a"  # test


def one_yandex_request(search_string: str, count, region, page=0, timeout=30):
    """Выполнение одного запроса к Yandex XML API"""
    try:
        base_link = "https://yandex.ru/search/xml"
        params = {
            "user": YANDEX_XML_USER,
            "key": YANDEX_XML_KEY,
            "query": search_string,
            "groupby": f"attr=d.mode=deep.groups-on-page={count}.docs-in-group=3",
            "filter": "none",
            "lr": region,
            "page": f"{page}"
        }
        
        response = requests.get(base_link, params=params, timeout=timeout)
        
        # Обновление лимитов пользователя
        if current_user and not current_user.is_anonymous:
            current_user.limits = max(0, current_user.limits - 1)
            db.session.commit()
        
        return response
    except requests.exceptions.Timeout:
        logger.error(f"Timeout for Yandex XML query: {search_string}")
        raise
    except Exception as e:
        logger.error(f"Error in Yandex XML request: {e}")
        raise


class YaXmlSearchParser:
    """Оптимизированный парсер для Yandex XML API"""

    def __init__(self, user_requests, count=10, repeats=1, verbose=False,
                 region="213", docache=True, max_workers=4):
        self.requests = user_requests
        self.region = region
        self.count = count
        self.repeats = repeats
        self.verbose = verbose
        self.docache = docache
        self.max_workers = max_workers
        self.delay_repeats = 0.1
        self.timeout = 30
        
        # Кэш
        self._cache = {} if docache else None
        self._cache_time = {}
        self._cache_ttl = 12 * 3600

    def __parse_yandex_response(self, response, previous_results: dict):
        """Парсинг ответа Yandex XML"""
        if response.status_code != 200:
            print_error(f"bad request: {response.status_code}")
            return
        
        soup = bs4.BeautifulSoup(response.text, 'html5lib')
        results = soup.find_all('results')
        
        if not results:
            errors = soup.find_all('error')
            if errors:
                error_msg = errors[0].contents[0] if errors[0].contents else "unknown error"
                previous_results[SingleResult(str(error_msg), "error")] = [0]
            else:
                previous_results[SingleResult("fatal", "error")] = [0]
            return

        content = results[0]
        groups = content.find_all('group')
        c = len(previous_results.keys())
        
        for group in groups:
            c += 1
            doc = group.doc
            url = doc.url.text if doc.url else ""
            title_elem = doc.title if doc.title else None
            title = ""
            
            if title_elem:
                # Удаляем теги <hlword> из заголовка
                title = title_elem.text.replace("<hlword>", "").replace('</hlword>', "")
            
            if url:
                single_result = SingleResult(url, title)
                previous_results.setdefault(single_result, []).append(c)
                
                if c >= self.count:
                    break

    def _parse_single_query(self, text):
        """Парсинг одного запроса"""
        d = {}
        
        for i in range(self.repeats):
            try:
                inx = 0
                res_func = timed_lru_cache(docache=self.docache)(one_yandex_request)
                res = res_func(text, self.count, self.region, page=inx, timeout=self.timeout)
                self.__parse_yandex_response(res, d)
                time.sleep(self.delay_repeats)
            except Exception as e:
                logger.error(f"Error parsing query '{text}': {e}")
                continue
        
        # Усреднение позиций
        for k in d:
            d[k] = sum(d[k]) / len(d[k]) if d[k] else 0
        
        return sorted(d.items(), key=lambda x: x[1])

    def run_parse(self):
        """Запуск парсинга с использованием ThreadPoolExecutor"""
        logger.info(f"Starting Yandex XML parse: {len(self.requests)} queries")
        results = ParsingResult("yandex")
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_query = {
                executor.submit(self._parse_single_query, text): text 
                for text in self.requests
            }
            
            for future in as_completed(future_to_query):
                query = future_to_query[future]
                try:
                    parsed_results = future.result()
                    results.result[query] = parsed_results
                    logger.info(f"Completed query: {query}")
                except Exception as e:
                    logger.error(f"Failed query '{query}': {e}")
                    results.result[query] = [(SingleResult("error", str(e)), 0)]
        
        logger.info(f"Yandex XML parsing completed: {len(results.result)} results")
        return results
