#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Тест скорости парсера XMLRiver
Запуск: venv38_flask/bin/python speed_test.py
"""

import os, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv(override=True)

from parser_app import create_app
app = create_app()

with app.app_context():
    from parser_app.xmlriver import SearchParser

QUERIES_11 = [
    "установка пластиковых окон", "установка окон цена",
    "остекление балконов", "остекление лоджий",
    "пластиковые окна на дачу", "цены на окна",
    "мягкое остекление", "остекление террас",
    "мягкое остекление террас", "остекление беседок", "дома под ключ"
]

QUERIES_5 = [
    "установка пластиковых окон", "установка окон цена",
    "остекление балконов", "остекление лоджий", "пластиковые окна на дачу"
]

# Конфигурация: (название, запросы, итерация, регион, город)
RUNS = [
    ("11 запросов", QUERIES_11, 1, 213, "Москва"),
    ("11 запросов", QUERIES_11, 2, 65, "Новосибирск"),
    ("5 запросов", QUERIES_5, 1, 213, "Москва"),
    ("5 запросов", QUERIES_5, 2, 65, "Новосибирск"),
]

def main():
    print("\n" + "="*80)
    print("🚀 ТЕСТ СКОРОСТИ XMLRiver ПАРСЕРА")
    print("="*80)

    all_results = []

    for test_name, queries, run_num, region, city in RUNS:
        print(f"\n--- {test_name} — запуск {run_num}/2 ({city}, регион {region}) ---")
        start = time.time()

        with app.app_context():
            parser = SearchParser(
                user_requests=queries, engine="yandex", count=10,
                repeats=1, region=str(region), docache=False
            )
            result = parser.run_parse()

        elapsed = time.time() - start
        successful = len(result.result)
        total = sum(len(v) for v in result.result.values())

        all_results.append({
            'test': test_name, 'run': run_num, 'city': city,
            'time_sec': round(elapsed, 1), 'queries': len(queries),
            'successful': successful, 'total_results': total
        })

        print(f"  ✅ Время: {elapsed:.1f} сек | Запросов: {len(queries)} | Успешно: {successful} | Результатов: {total}")

    # Статистика
    times = [r['time_sec'] for r in all_results]
    print(f"\n{'='*80}")
    print("📊 СТАТИСТИКА:")
    print(f"  Среднее: {sum(times)/len(times):.1f} сек")
    print(f"  Мин:     {min(times):.1f} сек")
    print(f"  Макс:    {max(times):.1f} сек")
    print(f"{'='*80}\n")

if __name__ == '__main__':
    main()
