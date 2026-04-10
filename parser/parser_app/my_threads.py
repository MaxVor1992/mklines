"""
Многопоточный/многопроцессный парсинг.

ParseThread — legacy-обёртка над threading (больше не используется в основном коде).
parse_batch — функция для параллельного парсинга через ProcessPoolExecutor.
"""
import os
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import Callable, Optional


def _parse_single(search_tuple: tuple, engine: int, region: int, depth: int, repeats: int, docache: bool) -> dict:
    """
    Отдельная функция для вызова в subprocess.
    Импортирует SearchParser внутри процесса, чтобы избежать проблем с serialisation.
    """
    if engine in (11,):
        from .request_parser import SearchParser
        parser = SearchParser(
            search_tuple, "yandex", count=depth, repeats=repeats,
            output_file=None, region=region, docache=docache
        )
    elif engine in (12, 22):
        from .xmlriver import SearchParser
        system = "yandex" if engine == 12 else "google"
        parser = SearchParser(
            search_tuple, system, count=depth, repeats=repeats,
            region=region, docache=docache
        )
    elif engine == 13:
        from .request_parser_with_ya_xml import YaXmlSearchParser
        parser = YaXmlSearchParser(
            search_tuple, count=depth, repeats=repeats,
            region=region, docache=docache
        )
    elif engine == 21:
        from .request_parser import SearchParser
        parser = SearchParser(
            search_tuple, "google", count=depth, repeats=repeats,
            output_file=None, region=region, docache=docache
        )
    else:
        raise ValueError(f"Unknown engine: {engine}")

    result = parser.run_parse()
    return result.result


def parse_batch(
    queries_list: list,
    engine: int,
    region: int,
    depth: int,
    repeats: int = 1,
    docache: bool = True,
    max_workers: Optional[int] = None,
    progress_callback: Optional[Callable] = None,
) -> dict:
    """
    Параллельный парсинг списка запросов через ProcessPoolExecutor.

    Args:
        queries_list: список строк-запросов
        engine: код движка (11, 12, 13, 21, 22)
        region: код региона
        depth: глубина (10/20/30)
        repeats: число повторений для усреднения
        docache: использовать кэширование
        max_workers: максимум процессов (по умолчанию — кол-во CPU)
        progress_callback: callback(current, total, query, result)

    Returns:
        dict: объединённый результат {query: [SingleResult, ...]}
    """
    if max_workers is None:
        max_workers = min(os.cpu_count() or 2, len(queries_list))

    combined_result = {}
    total = len(queries_list)

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        future_to_query = {
            executor.submit(
                _parse_single, (q,), engine, region, depth, repeats, docache
            ): q
            for q in queries_list
        }

        for i, future in enumerate(as_completed(future_to_query), 1):
            query = future_to_query[future]
            try:
                result = future.result()
                combined_result[query] = result.get(query, [])
            except Exception as exc:
                combined_result[query] = []

            if progress_callback:
                progress_callback(i, total, query, combined_result[query])

    return combined_result


# ─── Legacy: больше не используется ───
import threading


class ParseThread(threading.Thread):
    """Legacy-класс. Используйте parse_batch вместо него."""

    def __init__(self, search, engine, region, depth, callback=None):
        self.progress = 0
        super().__init__()
        self.search = search
        self.engine = engine
        self.region = region
        self.depth = depth
        self.callBack = callback

    def run(self):
        res = self.launch_parser(self.search, self.engine, self.region, self.depth)
        if self.callBack:
            self.callBack(res)

    @staticmethod
    def launch_parser(search, engine, region, depth):
        system = "yandex" if engine == 1 else "google"
        from . import request_parser
        parser = request_parser.SearchParser(
            search, system, count=depth, repeats=1,
            output_file=None, region=region
        )
        return parser.run_parse()
