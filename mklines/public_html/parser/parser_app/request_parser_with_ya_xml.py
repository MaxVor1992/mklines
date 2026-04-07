import time
import bs4
import requests
from .resultobj import SingleResult, ParsingResult
from .utils import print_error
from .for_cache import timed_lru_cache
from flask_login import current_user
from . import db

def one_yandex_request(search_string: str, count, region, page=0):
    base_link = "https://yandex.ru/search/xml"
    params = {
        # "user": "rapcoolglok", #production
        # "key": "03.301518843:05b89a7572f21ab21aacd73d7a8e044c", # production
        "user": "igor-exist",  # test
        "key": "03.17714018:ae35c9b26c7d4281b1e85311811a277a",  # test
        "query": search_string,
        "groupby": f"attr=d.mode=deep.groups-on-page={count}.docs-in-group=3",
        "filter": "none",
        "lr": region,
        "page": f"{page}"
    }
    # print(f"request for {search_string}")
    current_user.limits = current_user.limits - 1
    print("yaxml limits:", current_user.limits)
    db.session.commit()

    return requests.get(base_link, params=params)


# my yandex XML
# https://yandex.ru/search/xml?user=igor-exist&key=03.17714018:ae35c9b26c7d4281b1e85311811a277a

class YaXmlSearchParser:
    """search and parse with yandex XML"""

    def __init__(self, user_requests, count=10, repeats=1, verbose=False,
                 region="213",docache=True):
        self.requests = user_requests
        self.region = region
        self.delay_repeats = 1
        self.delay_requests = 1
        self.count = count
        self.repeats = repeats
        self.verbose = verbose
        self.docache = docache

    def __parse_yandex_response(self, response: requests.Response, previous_results: dict):
        print(response.status_code)
        if response.status_code == 200:
            page = response.text
            # print(page)
            soup = bs4.BeautifulSoup(page, 'html5lib')
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
                title = doc.title.text.replace("<hlword>", "").replace('</hlword>', "")
                single_result = SingleResult(url, title)
                previous_results.setdefault(single_result, []).append(c)
                if c > self.count:
                    break
        else:
            print_error(f"bad request: {response.status_code}")

    def run_parse(self):
        print("PARSING")
        results = ParsingResult("yandex")
        for text in self.requests:
            d = {}
            for i in range(self.repeats):
                inx = 0
                # res = one_yandex_request(text, self.count, self.region, page=inx)
                res = timed_lru_cache(docache=self.docache)(one_yandex_request)(text, self.count, self.region,
                                                                                    page=inx)
                self.__parse_yandex_response(res, d)
                time.sleep(self.delay_repeats)
            # print(d)
            for k in d:
                d[k] = sum(d[k]) / len(d[k])
            sorted_d = sorted(d.items(), key=lambda x: x[1])
            results.result[text] = sorted_d
        # print("*" * 100)
        # print(results.result)
        # print("*" * 100)
        return results
