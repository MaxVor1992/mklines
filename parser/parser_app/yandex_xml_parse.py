import bs4
import requests

with open('ya.xml') as file:
    res = file.read()


def __one_yandex_request(search_string: str):
    base_link = "https://yandex.ru/search/xml?user=rapcoolglok&key=03.301518843:05b89a7572f21ab21aacd73d7a8e044c"
    params = {
        "user": "rapcoolglok",
        "key": "03.301518843:05b89a7572f21ab21aacd73d7a8e044c",
        "query": search_string,
        "groupby": f"attr%3D.mode%3Dflat.groups-on-page%3D10.docs-in-group%3D1",
        "lr": 213,
        "filter": "none"
    }
    return requests.get(base_link, params=params)


def parse_ya(text):
    soup = bs4.BeautifulSoup(text, 'html5lib')
    results = soup.find_all('results')

    if not results:
        results = "no results"
    else:
        content = results[0]
        urls = content.find_all('url')
        results = f"length:{len(urls)}"
        urls = map(lambda x: x.contents[0], urls)
        results = results + "\n" + "\n".join(urls)
