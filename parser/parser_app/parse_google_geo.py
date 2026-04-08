import re
import json

s = '1000002,Kabul,"Kabul,Afghanistan",2004,AF,City,Active'


def parse_line(s):
    if '"' not in s:
        return None
    # print(s)
    groups = re.findall(r'".*?"', s)
    # print(groups)
    cname = groups[-1]
    sp = s.replace(cname + ",", "").split(",")
    if len(groups) > 1:
        name = groups[0]
        return {"id": sp[0], "name": name, "cname": cname, "parent id": sp[1], "country": sp[2], "type": sp[3],
                "status": sp[4]}

    return {"id": sp[0], "name": sp[1], "cname": cname, "parent id": sp[2], "country": sp[3], "type": sp[4],
            "status": sp[5]}


# Criteria ID,Name,Canonical Name,Parent ID,Country Code,Target Type,Status
geo = list(map(lambda x: x.strip(), open('geo.csv').readlines()))
del geo[0]
geo = list(filter(lambda el: el and el.get('country') in ['RU', "UA", "BY", "KZ"], map(parse_line, geo)))
json.dump(geo, open('geo.json', "w"))
file = open("geo.txt", "w")
for item in geo:
    file.write(f"{item['id']},{item['name']}\n")
print(*geo, sep="\n")
