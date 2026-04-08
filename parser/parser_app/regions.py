import json
region_y = map(lambda x: x.strip().split(","), open('lrs.txt').readlines())
region_g = json.load(open('geo.json'))

print(region_g)
print(type(region_g))

