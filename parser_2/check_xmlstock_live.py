import os
import sys
import requests
from bs4 import BeautifulSoup

USER = (os.getenv('XMLSTOCK_USER_ID') or '14050').strip()
KEY = (os.getenv('XMLSTOCK_API_KEY') or '44f372573b32c1e7e741e2d903df37eb').strip()
QUERY = ' '.join(sys.argv[1:]).strip() or 'окна'
TIMEOUT = 60

ENDPOINTS = [
    ('yandex_xml', 'https://xmlstock.com/yandex/xml/', {'groupby': 10, 'lr': 213, 'page': 0}),
    ('yandex_live', 'https://xmlstock.com/yandexlive/xml/', {'lr': 213, 'page': 0}),
    ('google_xml', 'https://xmlstock.com/google/xml/', {'lr': 213, 'page': 0}),
]

for name, url, extra in ENDPOINTS:
    params = {'user': USER, 'key': KEY, 'query': QUERY}
    params.update(extra)
    print('=' * 80)
    print(name, url)
    response = requests.get(url, params=params, timeout=TIMEOUT)
    print('HTTP:', response.status_code)
    print(response.text[:1200])
    soup = BeautifulSoup(response.text, 'xml')
    print('error:', bool(soup.find('error')))
