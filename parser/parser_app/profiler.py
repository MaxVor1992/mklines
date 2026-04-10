"""
Модуль профилирования производительности парсера
Включает: cProfile, tracemalloc, middleware для Flask
"""

import os
import time
import cProfile
import pstats
import tracemalloc
import io
import json
from datetime import datetime
from functools import wraps
from logging import info, warning, error

# Директория для результатов профилирования
_MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
PROFILE_DIR = os.path.join(_MODULE_DIR, 'profiles')
os.makedirs(PROFILE_DIR, exist_ok=True)


class PerformanceTimer:
    """
    Контекстный менеджер для замера времени выполнения кода
    
    Использование:
    with PerformanceTimer("parse_operation"):
        result = parser.run_parse()
    """
    
    def __init__(self, operation_name):
        self.operation_name = operation_name
        self.start_time = None
        self.end_time = None
        self.duration = None
    
    def __enter__(self):
        self.start_time = time.time()
        info(f"⏱ START: {self.operation_name}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time()
        self.duration = self.end_time - self.start_time
        
        if exc_type:
            error(f"⏱ ERROR: {self.operation_name} failed after {self.duration:.2f}s")
        else:
            info(f"⏱ DONE: {self.operation_name} completed in {self.duration:.2f}s")
        
        # Логирование медленных операций (>10 секунд)
        if self.duration > 10:
            warning(f"🐌 SLOW OPERATION: {self.operation_name} took {self.duration:.2f}s")


class MemoryProfiler:
    """
    Профилировщик памяти на основе tracemalloc
    
    Использование:
    with MemoryProfiler("parse_memory") as profiler:
        result = parser.run_parse()
    print(profiler.get_top_allocations())
    """
    
    def __init__(self, operation_name, top_n=20):
        self.operation_name = operation_name
        self.top_n = top_n
        self.start_snapshot = None
        self.end_snapshot = None
        self.stats = {}
    
    def __enter__(self):
        # Запускаем tracemalloc если не запущен
        if not tracemalloc.is_tracing():
            tracemalloc.start(25)  # 25 кадров стека
        
        self.start_snapshot = tracemalloc.take_snapshot()
        info(f"💾 START: {self.operation_name} - memory profiling started")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_snapshot = tracemalloc.take_snapshot()
        
        # Вычисляем статистику
        self._calculate_stats()
        
        info(f"💾 DONE: {self.operation_name}")
        info(f"   Current memory: {self.stats.get('current_size_kb', 0):.2f} KB")
        info(f"   Peak memory: {self.stats.get('peak_size_kb', 0):.2f} KB")
        info(f"   Allocated: {self.stats.get('allocated_kb', 0):.2f} KB")
        info(f"   Freed: {self.stats.get('freed_kb', 0):.2f} KB")
    
    def _calculate_stats(self):
        """Вычисляет статистику использования памяти"""
        current, peak = tracemalloc.get_traced_memory()
        
        # Сравниваем снапшоты
        top_stats = self.end_snapshot.compare_to(self.start_snapshot, 'lineno')
        
        allocated = 0
        freed = 0
        
        for stat in top_stats:
            if stat.size_diff > 0:
                allocated += stat.size_diff
            else:
                freed += abs(stat.size_diff)
        
        self.stats = {
            'current_size_kb': current / 1024,
            'peak_size_kb': peak / 1024,
            'allocated_kb': allocated / 1024,
            'freed_kb': freed / 1024,
            'net_change_kb': (current - tracemalloc.get_traced_memory()[0]) / 1024
        }
    
    def get_top_allocations(self):
        """Возвращает топ распределений памяти"""
        if not self.end_snapshot:
            return "Memory profiling not completed"
        
        top_stats = self.end_snapshot.compare_to(self.start_snapshot, 'lineno')
        
        output = io.StringIO()
        output.write(f"\n{'='*80}\n")
        output.write(f"TOP {self.top_n} MEMORY ALLOCATIONS: {self.operation_name}\n")
        output.write(f"{'='*80}\n\n")
        
        for idx, stat in enumerate(top_stats[:self.top_n], 1):
            output.write(f"#{idx}: {stat.size_diff / 1024:.1f} KB\n")
            output.write(f"    {stat.traceback}\n\n")
        
        return output.getvalue()
    
    def get_stats(self):
        """Возвращает словарь статистики"""
        return self.stats


class ParserProfiler:
    """
    Комплексный профилировщик парсера (cProfile + Memory)
    
    Использование:
    profiler = ParserProfiler("full_parse")
    result = profiler.run(parser.run_parse)
    profiler.save_report()
    """
    
    def __init__(self, operation_name):
        self.operation_name = operation_name
        self.cprofile_stats = None
        self.memory_stats = {}
        self.time_stats = {}
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    def run(self, func, *args, **kwargs):
        """
        Запускает функцию с полным профилированием
        
        Args:
            func: Функция для запуска
            *args, **kwargs: Аргументы функции
        
        Returns:
            Результат функции
        """
        result = None
        
        # Запускаем memory profiler
        with MemoryProfiler(self.operation_name) as mem_profiler:
            # Запускаем cProfile
            pr = cProfile.Profile()
            start_time = time.time()
            
            try:
                pr.enable()
                result = func(*args, **kwargs)
            finally:
                pr.disable()
                end_time = time.time()
            
            # Сохраняем статистику
            self.cprofile_stats = pstats.Stats(pr)
            self.time_stats = {
                'total_time': end_time - start_time,
                'timestamp': self.timestamp
            }
            self.memory_stats = mem_profiler.get_stats()
        
        return result
    
    def save_report(self, filename=None):
        """
        Сохраняет отчёт профилирования
        
        Args:
            filename: имя файла (по умолчанию auto)
        """
        if not filename:
            filename = f"profile_{self.operation_name}_{self.timestamp}"
        
        filepath = os.path.join(PROFILE_DIR, filename)
        
        # Сохраняем cProfile
        self.cprofile_stats.dump_stats(f"{filepath}.prof")
        
        # Создаём текстовый отчёт
        report = self._generate_text_report()
        with open(f"{filepath}.txt", 'w', encoding='utf-8') as f:
            f.write(report)
        
        # Сохраняем JSON отчёт
        json_report = {
            'operation': self.operation_name,
            'timestamp': self.timestamp,
            'time': self.time_stats,
            'memory': self.memory_stats
        }
        with open(f"{filepath}.json", 'w', encoding='utf-8') as f:
            json.dump(json_report, f, indent=2)
        
        info(f"📊 Profile report saved: {filepath}")
        return filepath
    
    def _generate_text_report(self):
        """Генерирует текстовый отчёт"""
        output = io.StringIO()
        
        output.write(f"\n{'='*80}\n")
        output.write(f"PARSER PERFORMANCE REPORT: {self.operation_name}\n")
        output.write(f"Timestamp: {self.timestamp}\n")
        output.write(f"{'='*80}\n\n")
        
        # Время выполнения
        output.write("⏱ TIME STATISTICS:\n")
        output.write(f"   Total time: {self.time_stats.get('total_time', 0):.2f} seconds\n\n")
        
        # Память
        output.write("💾 MEMORY STATISTICS:\n")
        for key, value in self.memory_stats.items():
            output.write(f"   {key}: {value:.2f} KB\n")
        output.write("\n")
        
        # cProfile топ функций
        output.write("📊 TOP 30 FUNCTIONS BY CUMULATIVE TIME:\n")
        output.write(f"{'-'*80}\n")
        
        s = io.StringIO()
        temp_stats = pstats.Stats(self.cprofile_stats, stream=s)
        temp_stats.sort_stats('cumulative')
        temp_stats.print_stats(30)
        output.write(s.getvalue())
        
        output.write(f"\n{'-'*80}\n")
        output.write(f"TOP 30 FUNCTIONS BY TOTAL TIME:\n")
        output.write(f"{'-'*80}\n")
        
        s2 = io.StringIO()
        temp_stats2 = pstats.Stats(self.cprofile_stats, stream=s2)
        temp_stats2.sort_stats('tottime')
        temp_stats2.print_stats(30)
        output.write(s2.getvalue())
        
        return output.getvalue()
    
    def get_summary(self):
        """Возвращает краткую сводку"""
        return {
            'operation': self.operation_name,
            'time_seconds': self.time_stats.get('total_time', 0),
            'memory_peak_kb': self.memory_stats.get('peak_size_kb', 0),
            'memory_current_kb': self.memory_stats.get('current_size_kb', 0),
            'timestamp': self.timestamp
        }


def profile_function(func):
    """
    Декоратор для профилирования функций
    
    Использование:
    @profile_function
    def my_function():
        ...
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        profiler = ParserProfiler(func.__name__)
        result = profiler.run(func, *args, **kwargs)
        
        # Логируем сводку
        summary = profiler.get_summary()
        info(f"📊 {func.__name__}: {summary['time_seconds']:.2f}s, "
             f"peak: {summary['memory_peak_kb']:.0f}KB")
        
        # Сохраняем отчёт
        profiler.save_report()
        
        return result
    return wrapper


def get_profile_reports(limit=10):
    """
    Возвращает список последних отчётов профилирования
    
    Args:
        limit: количество последних отчётов
    
    Returns:
        list: список отчётов
    """
    try:
        files = []
        for filename in os.listdir(PROFILE_DIR):
            if filename.endswith('.json'):
                filepath = os.path.join(PROFILE_DIR, filename)
                with open(filepath, 'r') as f:
                    report = json.load(f)
                    files.append(report)
        
        # Сортируем по времени
        files.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        return files[:limit]
        
    except Exception as e:
        error(f"Failed to load profile reports: {e}")
        return []


def analyze_parser_performance(search_queries, engine, region, depth, repeats=1):
    """
    Запускает комплексный анализ производительности парсера
    
    Args:
        search_queries: список запросов
        engine: поисковая система
        region: регион
        depth: глубина
        repeats: количество итераций
    
    Returns:
        ParserProfiler: объект с результатами
    """
    from . import xmlriver
    from .resultobj import ParsingResult
    
    profiler = ParserProfiler(f"parser_{engine}_{region}")
    
    def run_parse():
        parser = xmlriver.SearchParser(
            search_queries,
            "yandex" if engine in [11, 12, 13] else "google",
            count=depth,
            repeats=repeats,
            region=region,
            docache=False
        )
        return parser.run_parse()
    
    result = profiler.run(run_parse)
    profiler.save_report()
    
    return profiler, result
