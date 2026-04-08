colors = {
    "aqua": "#00ffff",
    "azure": "#f0ffff",
    "beige": "#f5f5dc",
    # "black": "#000000",
    "blue": "#0000ff",
    "brown": "#a52a2a",
    "cyan": "#00ffff",
    # "darkblue": "#00008b",
    "darkcyan": "#008b8b",
    "darkgrey": "#a9a9a9",
    # "darkgreen": "#006400",
    "darkkhaki": "#bdb76b",
    "darkmagenta": "#8b008b",
    # "darkolivegreen": "#556b2f",
    "darkorange": "#ff8c00",
    "darkorchid": "#9932cc",
    # "darkred": "#8b0000",
    "darksalmon": "#e9967a",
    "darkviolet": "#9400d3",
    "fuchsia": "#ff00ff",
    "gold": "#ffd700",
    "green": "#008000",
    # "indigo": "#4b0082",
    "khaki": "#f0e68c",
    "lightblue": "#add8e6",
    "lightcyan": "#e0ffff",
    "lightgreen": "#90ee90",
    "lightgrey": "#d3d3d3",
    "lightpink": "#ffb6c1",
    "lightyellow": "#ffffe0",
    "lime": "#00ff00",
    "magenta": "#ff00ff",
    "maroon": "#800000",
    # "navy": "#000080",
    "olive": "#808000",
    "orange": "#ffa500",
    "pink": "#ffc0cb",
    "purple": "#800080",
    "red": "#ff0000",
    "silver": "#c0c0c0",
    "white": "#ffffff",
    "yellow": "#ffff00"}


class ParsingResult:

    def __init__(self, engine):
        self.engine = engine
        self.result = {}
        self.clusters = None
        self.cluster_colors = None

    def __str__(self):
        return str(self.result)

    def calc_clusters(self, barrier=50):
        print("barrier:", barrier)
        data = {}
        for k in self.result:
            data[k] = set(map(lambda x: x[0].url, self.result[k]))

        keys = list(data.keys())
        res = {}
        for i in range(len(keys)):
            k1 = keys[i]
            for j in range(len(keys)):
                k2 = keys[j]
                bar = len(data[k1] & data[k2]) / len(data[k1]) * 100
                if bar >= barrier:
                    res.setdefault(k1, set()).add(k2)
        # {'остекление веранды новосибирск': {'остекление веранды новосибирск', 'остекление веранды цена'}, 'остекление веранды цена': {'остекление веранды новосибирск', 'остекление веранды цена'}, 'остекление лоджий +в новосибирске цены': {'остекление балкона цена', 'остекление лоджий +в новосибирске цены', 'балкон под ключ +в новосибирске цены'}, 'остекление балкона цена': {'остекление балкона цена', 'остекление лоджий +в новосибирске цены', 'балкон под ключ +в новосибирске цены'}, 'балкон под ключ +в новосибирске цены': {'остекление балкона цена', 'лоджии под ключ новосибирск', 'остекление лоджий +в новосибирске цены', 'балкон под ключ +в новосибирске цены'}, 'лоджии под ключ новосибирск': {'лоджии под ключ новосибирск', 'балкон под ключ +в новосибирске цены'}}
        # wrong asymmetric calc
        d = {}
        for k in res:
            if res[k] not in d.values():
                d[k] = res[k]
        # print(res)
        # print(d)
        d = list(enumerate(d.values()))
        print(d)
        d = {frozenset(item[1]): item[0] for item in d}
        res = []
        for k in keys:
            for k2 in d:
                if k in k2:
                    res.append((k, d[k2]))
                    break

        res.sort(key=lambda x: x[1])
        res = dict(res)
        self.clusters = res
        self.result = {k: self.result[k] for k in res}
        self.cluster_colors = {}
        color_v = list(colors.values())
        for k in res:
            self.cluster_colors[k] = color_v[self.clusters[k]]
        print(self.clusters)

    def get_cluster_index(self, key):
        if not self.clusters:
            return 0
        for k in self.clusters:
            if key in k:
                return self.clusters[k]


class SingleResult:

    def __init__(self, url, title):
        self.url = url
        self.title = title
        self.ismain = SingleResult.is_main(url)

    @staticmethod
    def is_main(url: str):
        if "://" not in url:
            return False
        res = url.split("://")[1]
        if res.count("/") == 1 and res.endswith("/"):
            return True
        elif res.count("/") == 0:
            return True
        else:
            return False

    def __hash__(self):
        return hash(self.url)
        # return hash((self.url, self.title))

    def __eq__(self, other):
        return self.url == other.url  # and self.title == other.title

    def __str__(self):
        return f"url={self.url}, title={self.title}"
