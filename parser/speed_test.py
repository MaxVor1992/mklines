#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Тест скорости парсера XMLRiver
Запускать из директории /home/r/rapcooc5/mklines/public_html/parser/

Использование:
    python speed_test.py           # Все тесты
    python speed_test.py --runs=2  # Количество повторов (по умолч. 2)

ВАЖНО: Запускать через Python из виртуального окружения:
    venv38_flask/bin/python speed_test.py
    ИЛИ
    source venv38_flask/bin/activate && python speed_test.py
"""

import os
import sys

# Проверяем что Flask доступен
try:
    import flask
except ImportError:
    print("❌ Flask не найден! Запустите через виртуальное окружение:")
    print("   venv38_flask/bin/python speed_test.py")
    sys.exit(1)

import time

# Добавляем пути
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Загружаем .env
from dotenv import load_dotenv
load_dotenv(override=True)

# Инициализируем Flask приложение
from parser_app import create_app

app = create_app()

# Теперь импортируем SearchParser в контексте приложения
with app.app_context():
    from parser_app.xmlriver import SearchParser

# ============================================================================
# Тестовые наборы из task.txt
# ============================================================================

QUERIES_10 = [
    "установка пластиковых окон",
    "установка окон цена",
    "остекление балконов",
    "остекление лоджий",
    "пластиковые окна на дачу",
    "цены на окна",
    "мягкое остекление",
    "остекление террас",
    "мягкое остекление террас",
    "остекление беседок",
    "дома под ключ",  # 11 запросов
]

QUERIES_5 = [
    "установка пластиковых окон",
    "установка окон цена",
    "остекление балконов",
    "остекление лоджий",
    "пластиковые окна на дачу",
]

REGION_MOSCOW = 213  # Москва
ENGINE = "yandex"    # Яндекс XML River
DEPTH = 10           # ТОП-10
REPEATS = 1          # 1 итерация
DEVICE = "desktop"

# ============================================================================


def run_test(name, queries, runs=2):
    """Запустить тест N раз и показать статистику"""
    print(f"\n{'='*80}")
    print(f"ТЕСТ: {name}")
    print(f"Запросов: {len(queries)}")
    print(f"Повторов: {runs}")
    print(f"Регион: Москва ({REGION_MOSCOW})")
    print(f"Движок: Яндекс XML River")
    print(f"{'='*80}")

    times = []

    for run_num in range(1, runs + 1):
        print(f"\n--- Запуск {run_num}/{runs} ---")
        start = time.time()

        with app.app_context():
            parser = SearchParser(
                user_requests=queries,
                engine=ENGINE,
                count=DEPTH,
                repeats=REPEATS,
                region=str(REGION_MOSCOW),
                docache=False,  # Без кэша для чистого теста
                device=DEVICE
            )

            result = parser.run_parse()
            elapsed = time.time() - start
            times.append(elapsed)

            successful = len(result.result)
            total_results = sum(len(v) for v in result.result.values())

            print(f"  ✅ Время: {elapsed:.1f} сек")
            print(f"  ✅ Запросов обработано: {successful}/{len(queries)}")
            print(f"  ✅ Всего результатов: {total_results}")

    # Статистика
    if times:
        print(f"\n{'='*80}")
        print(f"СТАТИСТИКА ({runs} запусков):")
        print(f"  Среднее время: {sum(times)/len(times):.1f} сек")
        print(f"  Минимальное:   {min(times):.1f} сек")
        print(f"  Максимальное:  {max(times):.1f} сек")
        if len(times) > 1:
            print(f"  Разброс:       {max(times)-min(times):.1f} сек")
        print(f"{'='*80}")

    return times


def main():
    runs = 2

    # Проверка аргументов командной строки
    for arg in sys.argv[1:]:
        if arg.startswith('--runs='):
            runs = int(arg.split('=')[1])

    print("\n" + "="*80)
    print("🚀 ТЕСТ СКОРОСТИ XMLRiver ПАРСЕРА")
    print("="*80)

    # Тест 1: 10+ запросов (2 раза)
    run_test("11 запросов (Москва)", QUERIES_10, runs=runs)

    # Тест 2: 5 запросов (2 раза)
    run_test("5 запросов (Москва)", QUERIES_5, runs=runs)

    print("\n✅ Все тесты завершены!\n")


if __name__ == '__main__':
    main()
