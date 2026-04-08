# -*- coding: utf-8 -*-
"""
Оптимизированный парсер для нативных запросов к Яндекс и Google
С поддержкой многопоточности, кэширования и обработки ошибок
"""
import time
import bs4
import fake_headers
import fake_useragent
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from .for_cache import timed_lru_cache
from .resultobj import ParsingResult, SingleResult
from .utils import print_error
from flask_login import current_user
from . import db
import logging

logger = logging.getLogger(__name__)


def one_google_request(search_string: str, search_parameter, links_on_page, url, timeout=30):
    """Выполнение одного запроса к Google с таймаутом"""
    try:
        header = fake_headers.Headers().generate()
        data = {search_parameter: search_string, links_on_page: 50}
        response = requests.get(url, params=data, headers=header, timeout=timeout)
        response.encoding = 'utf-8'
        
        # Обновление лимитов пользователя
        if current_user and not current_user.is_anonymous:
            current_user.limits = max(0, current_user.limits - 1)
            db.session.commit()
        
        return response
    except requests.exceptions.Timeout:
        logger.error(f"Timeout for Google query: {search_string}")
        raise
    except Exception as e:
        logger.error(f"Error in Google request: {e}")
        raise


def one_yandex_request(search_string: str, region, url, links_on_page, page=0, timeout=30):
    """Выполнение одного запроса к Яндексу с таймаутом"""
    try:
        headers = fake_headers.Headers().generate()
        params = {
            "text": search_string,
            "lr": region,
            links_on_page: 30,
            "p": page
        }
        response = requests.get(url, params=params, headers=headers, timeout=timeout)
        
        # Обновление лимитов пользователя
        if current_user and not current_user.is_anonymous:
            current_user.limits = max(0, current_user.limits - 1)
            db.session.commit()
        
        return response
    except requests.exceptions.Timeout:
        logger.error(f"Timeout for Yandex query: {search_string}")
        raise
    except Exception as e:
        logger.error(f"Error in Yandex request: {e}")
        raise


class SearchParser:
    """Оптимизированный парсер с поддержкой многопоточности"""
    
    YA = "http://yandex.ru/search"
    GOO = "http://google.com/search"
    YA_CLASS = "path organic__path organic__path organic__path_rated"
    YA_CLASS_DIV = "path organic__path"
    GOO_CLASS = "yuRUbf"
    CAPTCHA_YA_CLASS = ["captcha i-bem", "CheckboxCaptcha", "CheckboxCaptcha-Button", 
                        "CheckboxCaptcha-Checkbox", "CheckboxCaptcha-Form"]

    def __init__(self, user_requests, system="yandex", count=10, repeats=1, 
                 output_file="urls", verbose=False, region="213", docache=True, 
                 max_workers=4):
        self.requests = user_requests
        self.system = system
        self.region = region
        
        if "yandex" in system:
            self.BASE_URL = SearchParser.YA
            self.a_class = SearchParser.YA_CLASS_DIV
            self.__search_parameter = "text"
            self.__links_on_page = "numdoc"
        else:
            self.BASE_URL = SearchParser.GOO
            self.a_class = SearchParser.GOO_CLASS
            self.__search_parameter = "q"
            self.__links_on_page = "num"
        
        self.count = count
        self.repeats = repeats
        self.ua = fake_useragent.FakeUserAgent()
        self.fake_head = fake_headers.Headers()
        self.output_file = output_file
        self.verbose = verbose
        self.docache = docache
        self.max_workers = max_workers
        self.delay_repeats = 0.5
        self.delay_requests = 0.5
        self.timeout = 30
        
        # Кэш
        self._cache = {} if docache else None
        self._cache_time = {}
        self._cache_ttl = 12 * 3600

    def __parse_yandex_response(self, response, previous_results: dict):
        """Парсинг ответа Яндекса"""
        if response.status_code == 200:
            soup = bs4.BeautifulSoup(response.text, 'html5lib')
            
            if not self.__check_captcha(soup):
                previous_results[SingleResult("обнаружена captcha", "error")] = [0]
                return "captcha"

            results = soup.find('ul', id="search-result")
            if not results:
                return
            
            lis = results.find_all('li', class_="serp-item")
            c = len(previous_results.keys())
            
            for li in lis:
                div = li.find("div")
                if not div or not div.h2:
                    continue
                    
                h2 = div.h2
                a = h2.a
                if not a:
                    continue
                    
                url = a.get('href', '')
                div_title = a.find("div", class_="OrganicTitle-LinkText organic__url-text")
                title = div_title.text if div_title else "no title"
                
                single_result = SingleResult(url, title)
                c += 1
                previous_results.setdefault(single_result, []).append(c)
                
                if c >= self.count:
                    break
        else:
            print_error(f"bad request: {response.status_code}")

    def __check_captcha(self, soup: bs4.BeautifulSoup):
        """Проверка на капчу"""
        if soup.find_all("div", {"class": self.CAPTCHA_YA_CLASS}):
            print_error("yandex captcha detected...")
            return False
        return True

    def __parse_google_response(self, response, previous_results: dict):
        """Парсинг ответа Google"""
        if response.status_code == 200:
            soup = bs4.BeautifulSoup(response.text, features="html.parser")
            
            if not self.__check_captcha(soup):
                previous_results[SingleResult("обнаружена captcha", "error")] = [0]
                return "captcha"
                
            c = 0
            for div in soup.find_all('div', {"class": self.a_class}):
                a = div.findChildren("a", recursive=False)[0] if div.findChildren("a", recursive=False) else None
                if not a:
                    continue
                    
                url = a.get('href', '')
                h3 = a.h3
                
                if "yabs.yandex" in url:
                    continue
                    
                c += 1
                title = h3.text if h3 else "title not parsed"
                single_result = SingleResult(url, title)
                previous_results.setdefault(single_result, []).append(c)
                
                if c >= self.count:
                    break
        else:
            print_error(f"bad request: {response.status_code}")

    def _parse_single_query(self, text):
        """Парсинг одного запроса"""
        d = {}
        
        for i in range(self.repeats):
            try:
                if "yandex" not in self.system:
                    # Google
                    res_func = timed_lru_cache(docache=self.docache)(one_google_request)
                    res = res_func(text, self.__search_parameter, self.__links_on_page, 
                                   self.BASE_URL, self.timeout)
                    code = self.__parse_google_response(res, d)
                else:
                    # Yandex
                    inx = 0
                    while len(d.keys()) < self.count and inx < 16:
                        time.sleep(self.delay_requests)
                        res_func = timed_lru_cache(docache=self.docache)(one_yandex_request)
                        res = res_func(text, self.region, self.BASE_URL, 
                                       self.__links_on_page, page=inx, timeout=self.timeout)
                        code = self.__parse_yandex_response(res, d)
                        inx += 1
                        
                        if code == "captcha":
                            break
                        
                        time.sleep(self.delay_requests)
                        
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
        logger.info(f"Starting native parse: {len(self.requests)} queries, system={self.system}")
        results = ParsingResult(self.system)
        
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
        
        logger.info(f"Native parsing completed: {len(results.result)} results")
        return results
