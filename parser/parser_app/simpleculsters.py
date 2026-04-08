import pickle

data = pickle.load(open("data.txt", "rb"))
print(data)
res = []
inx = 0
urls = []
for k in data:
    inx += 1
    data[k] = set(map(lambda x: x[0].url, data[k]))

keys = list(data.keys())
# print(keys)
res = {}
maxk = ""
barrier = 40
for i in range(len(keys)):
    k1 = keys[i]
    for j in range(len(keys)):
        k2 = keys[j]
        bar = len(data[k1] & data[k2]) / len(data[k1]) * 100
        if bar > barrier:
            res.setdefault(k1, set()).add(k2)

d = {}
for k in res:
    if res[k] not in d.values():
        d[k] = res[k]
print(res)
print(d)
d = list(enumerate(d.values()))
print(d)
d = {frozenset(item[1]):item[0] for item in d}
res = {}
for k in keys:
    for k2 in d:
        if k in k2:
            res[k] = d[k2]
            break
print(res)