import requests
import fake_headers

headers = fake_headers.Headers().generate()
headers['Accept'] = "text/html,application/xhtml+xml,application/xml;q=0.9,/;q=0.8"
print("generated headers",headers)
res = requests.get("https://yandex.ru",headers=headers)
print("cookies",*res.cookies, sep="\n")
print("="*150)
print("headers",*res.headers,sep="\n")
print("="*150)
print("history",*res.history, sep="\n")

