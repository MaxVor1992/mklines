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
        """
        Кластеризация запросов по совпадению URL.
        
        Исправления:
        1. Симметричное сравнение: используем min(len(k1), len(k2))
        2. Union-Find для правильной транзитивной группировки
        3. Оптимизация: O(n²) вместо O(n³)
        
        barrier - минимальный процент совпадения URL (0-100)
        """
        print("barrier:", barrier)
        
        # Собираем URL для каждого запроса
        data = {}
        for k in self.result:
            data[k] = set(map(lambda x: x[0].url, self.result[k]))

        keys = list(data.keys())
        n = len(keys)
        
        if n <= 1:
            # 0 или 1 запрос - всё в одном "кластере"
            self.clusters = {k: 0 for k in keys} if keys else {}
            self.cluster_colors = {k: colors.get(0, "#000000") for k in keys} if keys else {}
            return

        # === Union-Find структура для правильной группировки ===
        parent = list(range(n))
        rank = [0] * n
        
        def find(x):
            """Найти представителя множества с path compression"""
            if parent[x] != x:
                parent[x] = find(parent[x])  # Path compression
            return parent[x]
        
        def union(x, y):
            """Объединить два множества по рангу"""
            px, py = find(x), find(y)
            if px == py:
                return
            if rank[px] < rank[py]:
                px, py = py, px
            parent[py] = px
            if rank[px] == rank[py]:
                rank[px] += 1

        # === Попарное сравнение всех запросов O(n²) ===
        for i in range(n):
            for j in range(i + 1, n):
                k1, k2 = keys[i], keys[j]
                urls1, urls2 = data[k1], data[k2]
                
                # Считаем пересечение
                intersection = len(urls1 & urls2)
                
                if intersection == 0:
                    continue
                
                # Симметричный расчёт процента: делим на МИНИМАЛЬНЫЙ размер
                # Это гарантирует что сравнение k1→k2 == k2→k1
                min_size = min(len(urls1), len(urls2))
                similarity = (intersection / min_size) * 100
                
                if similarity >= barrier:
                    union(i, j)

        # === Формируем кластеры ===
        # Группируем индексы по их представителю
        clusters_map = {}
        for i in range(n):
            root = find(i)
            if root not in clusters_map:
                clusters_map[root] = []
            clusters_map[root].append(i)

        # Нумеруем кластеры (только те, где > 1 элемента - это реальные кластеры)
        # Одиночные запросы тоже получают номер кластера
        cluster_idx = 0
        key_to_cluster = {}
        
        # Сортируем кластеры по размеру (большие сначала) для удобного отображения
        sorted_clusters = sorted(clusters_map.values(), key=lambda x: -len(x))
        
        for cluster_members in sorted_clusters:
            for member_idx in cluster_members:
                key_to_cluster[keys[member_idx]] = cluster_idx
            cluster_idx += 1

        self.clusters = key_to_cluster
        self.result = {k: self.result[k] for k in keys}
        
        # Цвета для кластеров
        self.cluster_colors = {}
        color_v = list(colors.values())
        for k in keys:
            cluster_num = key_to_cluster[k]
            self.cluster_colors[k] = color_v[cluster_num % len(color_v)]
        
        print(f"Кластеризация завершена: {len(keys)} запросов, {cluster_idx} кластеров")
        print(self.clusters)

    def get_cluster_index(self, key):
        if not self.clusters:
            return 0
        for k in self.clusters:
            if key in k:
                return self.clusters[k]


class SingleResult:

    def __init__(self, url, title, description=''):
        self.url = url
        self.title = title
        self.description = description
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
