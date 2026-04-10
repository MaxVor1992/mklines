import requests
import bs4
import time
import os
from resultobj import ParsingResult, SingleResult
from utils import print_error, print_ok, print_warning, engines

# БЕЗОПАСНОСТЬ: Чтение ключей из переменных окружения
USER_ID = os.environ.get('XMLRIVER_USER_ID', '3089')
KEY = os.environ.get('XMLRIVER_KEY', '9305a49e48a27d38f87261f26a6346f4d6508b6d')


class SearchParser:
    YA = f"http://xmlriver.com/search_yandex/xml"
    GOO = f"http://xmlriver.com/search/xml"

    def __init__(self, user_requests, engine="yandex", count=10, repeats=1, verbose=True,
                 region="213"):
        self.requests = user_requests
        self.system = engine
        self.region = region
        self.delay_repeats = 0.01
        self.count = count
        self.repeats = repeats
        self.verbose = verbose

    def __one_google_request(self, search_string: str):
        base_link = SearchParser.GOO
        params = {
            "user": USER_ID,
            "key": KEY,
            "query": search_string,
            "groupby": f"{self.count}",
            "lr": 143,  # language code ru
            "country": 2643,
            # "loc": self.region,
            "page": f"{1}",
            "domain": 143  # domain ru
        }
        print("google search string ", search_string)
        return requests.get(base_link, params=params, timeout=30)

    def __one_yandex_request(self, search_string: str, page=0):
        base_link = SearchParser.YA
        params = {
            "user": USER_ID,
            "key": KEY,
            "query": search_string,
            "groupby": f"attr=d.mode=deep.groups-on-page={self.count}.docs-in-group=3",
            "lr": self.region,
            "page": f"{page}"
        }
        print("yandex search string ", search_string)
        print(params)
        return requests.get(base_link, params=params, timeout=30)

    def __parse_river_response(self, response: requests.Response, previous_results: dict):
        print(response.status_code)
        if response.status_code == 200:
            page = response.text
            print(page)
            soup = bs4.BeautifulSoup(page, 'lxml')
            results = soup.find_all('results')  # results of search <results>
            if not results:
                results = soup.find_all('error')
                print('no results', results)
                if results:
                    previous_results[SingleResult(results[0].contents[0], "error")] = [0]
                else:
                    previous_results[SingleResult("fatal", "error")] = [0]
                return "captcha"

            content = results[0]
            groups = content.find_all('group')
            c = len(previous_results.keys())
            for group in groups:
                c += 1
                doc = group.doc
                url = doc.url.text
                title = doc.title.text
                single_result = SingleResult(url, title)
                previous_results.setdefault(single_result, []).append(c)
                if c > self.count:
                    break
        else:
            print_error(f"bad request: {response.status_code}")

    def run_parse(self):
        results = ParsingResult(self.system)
        for text in self.requests:
            d = {}
            for i in range(self.repeats):
                if "yandex" not in self.system:
                    res = self.__one_google_request(text)
                    self.__parse_river_response(res, d)
                else:
                    inx = 0
                    res = self.__one_yandex_request(text, page=inx)
                    self.__parse_river_response(res, d)
                time.sleep(self.delay_repeats)
            print(d)
            for k in d:
                d[k] = sum(d[k]) / len(d[k])
            sorted_d = sorted(d.items(), key=lambda x: x[1])
            results.result[text] = sorted_d
        print("*" * 100)
        print(results.result)
        print("*" * 100)
        return results
