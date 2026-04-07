from resultobj import ParsingResult, SingleResult
import pickle
from parser_utils import colors, prepare_xls, save_csv
import random






def get_same_urls_new(res: ParsingResult):
    print("start get same url function")
    # print("arg:", str(res))
    big_dict: dict = res.result
    # with open("parsingres.dat", "wb") as file:
    #     pickle.dump(res, file)
    keys = []
    for big_k in big_dict:
        print("=" * 80)
        print(dict(big_dict[big_k]).keys())
        keys.append(set(dict(big_dict[big_k]).keys()))
        print("=" * 80)
    # print("keys=", keys)
    uniq_urls = set()
    # uniq_urls = functools.reduce(lambda x, y: x & y, keys)
    for i in range(len(keys) - 1):
        for j in range(i + 1, len(keys)):
            uniq_urls.update(keys[i] & keys[j])
    # print("uniq_urls", uniq_urls)

    # return {url: f"#{random.randrange(0x1000000):06x}" for url in uniq_urls}
    if len(uniq_urls) <= len(colors):
        return {url: color for url, color in zip(uniq_urls, colors)}
    else:
        d = {}
        uniq_urls = list(uniq_urls)
        k = 0
        for i in range(len(colors)):
            d[uniq_urls[i]] = colors[list(colors.keys())[i]]
            k = i
        for j in range(k + 1, len(uniq_urls)):
            d[uniq_urls[
                j]] = f"#{random.randrange(0x127):02x}{random.randrange(0x127):02x}{random.randrange(0x127):02x}"
        return d


with open('parsingres.dat','rb') as file:
    obj = pickle.load(file)
    res = get_same_urls_new(obj)
    print(res)