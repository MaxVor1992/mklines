import time
import bs4
import fake_headers
import fake_useragent
import requests
from .for_cache import timed_lru_cache
from .resultobj import ParsingResult, SingleResult
from .utils import print_error
from flask_login import current_user
from . import db


def one_google_request(search_string: str, search_parameter, links_on_page, url):
    header = fake_headers.Headers().generate()
    data = {search_parameter: search_string, links_on_page: 50}
    response = requests.get(url, params=data, headers=header)
    response.encoding = 'utf-8'
    # print(f"request for {search_string}")
    current_user.limits = current_user.limits - 1
    print("request limits:", current_user.user_limit)
    db.session.commit()

    return response



def one_yandex_request(search_string: str, region, url, links_on_page, page=0):
    headers = fake_headers.Headers().generate()
    params = {
        "text": search_string,
        "lr": region,
        links_on_page: 30,
        "p": page
    }
    current_user.limits = current_user.limits - 1
    print("request limits:", current_user.limits)
    db.session.commit()

    return requests.get(url, params=params, headers=headers)


class SearchParser:
    """make search requests and parse results"""
    # YA = "http://yandex.ru/search?text={}&numdoc={}"
    YA = "http://yandex.ru/search"
    GOO = "http://google.com/search"
    "link link_theme_outer path__item i-bem link_js_inited"
    YA_CLASS = "path organic__path organic__path organic__path_rated"
    YA_CLASS_DIV = "path organic__path"
    GOO_CLASS = "yuRUbf"
    CAPTCHA_YA_CLASS = ["captcha i-bem", "CheckboxCaptcha", "CheckboxCaptcha-Button", "CheckboxCaptcha-Checkbox",
                        "CheckboxCaptcha-Form"]

    def __init__(self, user_requests, system="yandex", count=10, repeats=1, output_file="urls", verbose=False,
                 region="213", docache=True):
        self.requests = user_requests
        self.system = system
        self.region = region
        if "yandex" in system:
            self.BASE_URL = SearchParser.YA
            self.a_class = SearchParser.YA_CLASS_DIV
            self.__search_parameter = "text"
            self.__links_on_page = "numdoc"
            self.delay_repeats = 1
            self.delay_requests = 1

        else:
            self.BASE_URL = SearchParser.GOO
            self.a_class = SearchParser.GOO_CLASS
            self.__search_parameter = "q"
            self.__links_on_page = "num"
            self.delay_repeats = 1
            self.delay_requests = 1

        self.session = requests.Session()
        self.cookies = None
        self.count = count
        self.repeats = repeats
        self.ua = fake_useragent.FakeUserAgent()
        self.fake_head = fake_headers.Headers()
        self.output_file = output_file
        self.verbose = verbose
        self.docache = docache

    def __parse_yandex_response(self, response: requests.Response, previous_results: dict):
        # print(response.status_code)

        if response.status_code == 200:
            page = response.text
            # print("page")
            # print(page)
            soup = bs4.BeautifulSoup(page, 'html5lib')
            if not SearchParser.__check_captcha(soup):
                previous_results[SingleResult("обнаружена captcha", "error")] = [0]
                return "captcha"

            results = soup.find('ul', id="search-result")
            # print("debug results yandex raw parse", results)
            lis = results.find_all('li', class_="serp-item")

            c = len(previous_results.keys())
            for li in lis:
                div = li.find("div")
                h2 = div.h2
                a = h2.a
                url = a['href']
                div = a.find("div", class_="OrganicTitle-LinkText organic__url-text")
                title = div.text
                single_result = SingleResult(url, title)
                c += 1
                print(url.contents[0])
                previous_results.setdefault(single_result, []).append(c)
                if c > self.count:
                    break
        else:
            print_error(f"bad request: {response.status_code}")

    @staticmethod
    def __check_captcha(soup: bs4.BeautifulSoup):
        if soup.find_all("div", {"class": SearchParser.CAPTCHA_YA_CLASS}):
            print_error("yandex captcha detected...")
            return False
        return True

    def get_favicon(self, div):
        pass

    def __parse_google_response(self, response: requests.Response, previous_results: dict):
        # print(response.status_code)
        if response.status_code == 200:
            page = response.text
            soup = bs4.BeautifulSoup(page, features="html.parser")
            if not SearchParser.__check_captcha(soup):
                previous_results[SingleResult("обнаружена captcha", "error")] = [0]
                return "captcha"
            c = 0
            for div in soup.find_all('div', {"class": self.a_class}):
                a = div.findChildren("a", recursive=False)[0]
                url = a['href']
                h3 = a.h3
                if "yabs.yandex" in url:
                    continue
                c += 1
                if not h3:
                    title = "title not parsed"
                else:
                    title = h3.text
                single_result = SingleResult(url, title)
                previous_results.setdefault(single_result, []).append(c)
                if c >= self.count:
                    break
            # print(f"found {c} urls")
        else:
            print_error(f"bad request: {response.status_code}")

    def run_parse(self):
        """:returns list of system and dict with {"request" : urls}"""
        results = ParsingResult(self.system)
        for text in self.requests:
            d = {}
            for i in range(self.repeats):
                if "yandex" not in self.system:
                    # res = one_google_request(text, self.__search_parameter,
                    #                          self.__links_on_page, self.BASE_URL)
                    res = timed_lru_cache(docache=self.docache)(one_google_request)(text, self.__search_parameter, self.__links_on_page,
                                                                              self.BASE_URL)
                    code = self.__parse_google_response(res, d)
                    if code == "captcha":
                        pass
                else:
                    inx = 0
                    while len(d.keys()) < self.count and inx < 16:
                        time.sleep(self.delay_requests)
                        # res = one_yandex_request(text, self.region, self.BASE_URL, self.__links_on_page, page=inx)
                        res = timed_lru_cache(docache=self.docache)(one_yandex_request)(text, self.region, self.BASE_URL, self.__links_on_page, page=inx)
                        code = self.__parse_yandex_response(res, d)
                        inx += 1
                        if code == "captcha":
                            break
                        time.sleep(self.delay_requests)
                time.sleep(self.delay_repeats)
            # print(d)
            for k in d:
                d[k] = sum(d[k]) / len(d[k])
            sorted_d = sorted(d.items(), key=lambda x: x[1])
            results.result[text] = sorted_d
        # print("*" * 100)
        # print(results)
        # print("*" * 100)
        return results
