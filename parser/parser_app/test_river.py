import requests

USER_ID = "3089"
KEY = "9305a49e48a27d38f87261f26a6346f4d6508b6d"

YA = f"http://xmlriver.com/search_yandex/xml"
GOO = f"http://xmlriver.com/search/xml"


def one_google_request(search_string: str, count):
    base_link = GOO
    params = {
        "user": USER_ID,
        "key": KEY,
        "query": search_string,
        "groupby": f"{count}",
        # "lr": self.region,
        # "filter": "none",
        "page": f"{1}"
    }
    return requests.get(base_link, params=params)


resp = one_google_request("окна", 20)
with open('river_test2.xml', 'w') as file:
    file.write(resp.text)
print("Done")
