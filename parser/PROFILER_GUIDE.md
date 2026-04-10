# 📊 Руководство по профилированию парсера

Полное руководство по использованию системы профилирования производительности парсера XMLRiver.

---

## 📋 Содержание

1. [Обзор возможностей](#обзор-возможностей)
2. [Быстрый старт](#быстрый-старт)
3. [Flask Middleware](#flask-middleware)
4. [Программное использование](#программное-использование)
5. [Веб-интерфейс](#веб-интерфейс)
6. [Форматы отчётов](#форматы-отчётов)
7. [Анализ результатов](#анализ-результатов)
8. [Оптимизация производительности](#оптимизация-производительности)
9. [Устранение проблем](#устранение-проблем)

---

## 🎯 Обзор возможностей

### Что умеет система профилирования:

| Функция | Описание |
|---|---|
| **⏱ Замер времени** | Автоматический замер времени каждого HTTP запроса |
| **💾 Анализ памяти** | Профилирование потребления памяти через `tracemalloc` |
| **📊 cProfile** | Детальный анализ времени выполнения каждой функции |
| **🌐 Веб-интерфейс** | Просмотр отчётов через браузер |
| **📝 Логирование** | Автоматическое логирование медленных операций |
| **🎨 Декораторы** | Простое профилирование через `@profile_function` |

---

## 🚀 Быстрый старт

### 1. Через веб-интерфейс

Откройте в браузере:
```
https://mklines.ru/parser/profile_reports
```

1. Введите поисковые запросы
2. Выберите движок, регион, глубину
3. Нажмите **"🔍 Запустить профилирование"**
4. Просмотрите результат на странице отчётов

### 2. Из кода Python

```python
from parser_app.profiler import ParserProfiler

# Создаём профилировщик
profiler = ParserProfiler("test_parse")

# Запускаем функцию с профилированием
result = profiler.run(my_function, arg1, arg2)

# Сохраняем отчёт
profiler.save_report()

# Выводим сводку
print(profiler.get_summary())
```

---

## ⚙️ Flask Middleware

### Автоматический замер времени запросов

Middleware автоматически:
- ✅ Замеряет время выполнения каждого запроса
- ✅ Добавляет header `X-Response-Time`
- ✅ Логирует медленные запросы (>1 сек)
- ✅ Записывает в лог все запросы (DEBUG уровень)

### Пример лога:

```
2026-04-09 13:30:00,123 INFO: ⏱ REQUEST: POST /index took 0.5234s
2026-04-09 13:30:05,456 WARNING: 🐌 SLOW REQUEST: POST /index took 52.1234s
```

### Проверка времени запроса:

**Через curl:**
```bash
curl -I https://mklines.ru/parser/login

# Ответ содержит:
# X-Response-Time: 0.1234s
```

**Через браузер (DevTools):**
1. Откройте DevTools (F12)
2. Вкладка **Network**
3. Выберите запрос
4. В **Response Headers** найдите `X-Response-Time`

---

## 💻 Программное использование

### 1. PerformanceTimer - замер времени

Простой замер времени выполнения блока кода:

```python
from parser_app.profiler import PerformanceTimer

# Использование как контекстного менеджера
with PerformanceTimer("parse_operation") as timer:
    result = parser.run_parse()

# После выхода из блока доступны данные:
print(f"Время выполнения: {timer.duration:.2f} сек")
```

**Вывод в лог:**
```
⏱ START: parse_operation
⏱ DONE: parse_operation completed in 45.23s
🐌 SLOW OPERATION: parse_operation took 45.23s  # если > 10 сек
```

### 2. MemoryProfiler - анализ памяти

Профилирование потребления памяти:

```python
from parser_app.profiler import MemoryProfiler

with MemoryProfiler("parse_memory", top_n=20) as mem:
    result = parser.run_parse()

# Получаем топ распределений памяти
print(mem.get_top_allocations())

# Получаем статистику
stats = mem.get_stats()
print(f"Пик памяти: {stats['peak_size_kb']:.0f} KB")
print(f"Текущая память: {stats['current_size_kb']:.0f} KB")
print(f"Выделено: {stats['allocated_kb']:.0f} KB")
print(f"Освобождено: {stats['freed_kb']:.0f} KB")
```

**Вывод в лог:**
```
💾 START: parse_memory - memory profiling started
💾 DONE: parse_memory
   Current memory: 15234.56 KB
   Peak memory: 18456.78 KB
   Allocated: 25678.90 KB
   Freed: 10444.34 KB
```

### 3. ParserProfiler - комплексный анализ

Полное профилирование (cProfile + Memory + Time):

```python
from parser_app.profiler import ParserProfiler

# Создаём профилировщик
profiler = ParserProfiler("full_parse_analysis")

# Запускаем функцию
def my_parse_function():
    # ... код парсинга ...
    return result

result = profiler.run(my_parse_function)

# Сохраняем отчёты (3 формата: .prof, .txt, .json)
filepath = profiler.save_report()

# Получаем сводку
summary = profiler.get_summary()
print(f"Время: {summary['time_seconds']:.2f} сек")
print(f"Память пик: {summary['memory_peak_kb']:.0f} KB")
```

### 4. Декоратор @profile_function

Автоматическое профилирование функции:

```python
from parser_app.profiler import profile_function

@profile_function
def launch_parser(search, engine, region, depth, repeats):
    # ... код парсера ...
    return result

# При вызове функции автоматически:
# 1. Запустится профилирование
# 2. Сохранятся отчёты
# 3. Запишется сводка в лог
result = launch_parser(("запрос",), 12, 213, 10, 1)
```

### 5. analyze_parser_performance()

Быстрый анализ парсера:

```python
from parser_app import profiler

profiler_obj, result = profiler.analyze_parser_performance(
    search_queries=("окна", "двери"),
    engine=12,           # Yandex XML River
    region=213,          # Москва
    depth=10,            # ТОП-10
    repeats=1            # 1 итерация
)

# Отчёт уже сохранён в /parser_app/profiles/
print(profiler_obj.get_summary())
```

---

## 🌐 Веб-интерфейс

### Страница отчётов: `/parser/profile_reports`

**Возможности:**
- ✅ Просмотр последних 20 отчётов
- ✅ Запуск нового профилирования через форму
- ✅ Таблица с метриками (время, память, timestamp)

**Пример таблицы:**

| Операция | Время (сек) | Память Peak (KB) | Память Current (KB) | Timestamp |
|---|---|---|---|---|
| parse_yandex_213 | 45.23 | 18456 | 15234 | 20260409_133000 |
| parse_google_1000028 | 32.10 | 12345 | 9876 | 20260409_132500 |

### Страница результата: `/parser/run_profile_analysis`

Показывает детальный результат одного профилирования:
- Общее время выполнения
- Пик потребления памяти
- Текущее потребление памяти
- Timestamp запуска

---

## 📁 Форматы отчётов

### 1. .prof (cProfile)

**Файл:** `profile_parse_yandex_213_20260409_133000.prof`

**Использование с SnakeViz:**
```bash
# Установка SnakeViz
pip install snakeviz

# Запуск визуализации
snakeviz profile_parse_yandex_213_20260409_133000.prof
```

**Откроется браузер с:**
- 🔥 Flame graph
- 📊 Каллграф
- 📈 Статистика по функциям

### 2. .txt (Текстовый отчёт)

**Файл:** `profile_parse_yandex_213_20260409_133000.txt`

**Содержимое:**
```
================================================================================
PARSER PERFORMANCE REPORT: parse_yandex_213
Timestamp: 20260409_133000
================================================================================

⏱ TIME STATISTICS:
   Total time: 45.23 seconds

💾 MEMORY STATISTICS:
   current_size_kb: 15234.56
   peak_size_kb: 18456.78
   allocated_kb: 25678.90
   freed_kb: 10444.34
   net_change_kb: 4567.89

📊 TOP 30 FUNCTIONS BY CUMULATIVE TIME:
--------------------------------------------------------------------------------
         123456 function calls in 45.230 seconds

   Ordered by: cumulative time

   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
        1    0.001    0.001   45.230   45.230 xmlriver.py:394(run_parse)
       10    0.234    0.023   44.567    4.457 xmlriver.py:125(parse_query)
       10   40.123    4.012   40.123    4.012 {built-in method sleep}
      234    2.345    0.010    3.456    0.015 request.py:123(get)
     1234    1.234    0.001    2.345    0.002 beautifulsoup4:456(find)
     ...

--------------------------------------------------------------------------------
TOP 30 FUNCTIONS BY TOTAL TIME:
--------------------------------------------------------------------------------
   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
       10   40.123    4.012   40.123    4.012 {built-in method sleep}
      234    2.345    0.010    3.456    0.015 request.py:123(get)
        1    0.567    0.567    0.567    0.567 xmlriver.py:200(_parse_xml_response)
     1234    0.234    0.000    0.234    0.000 {method 'find' of 'bs4' objects}
     ...
```

### 3. .json (Машиночитаемый отчёт)

**Файл:** `profile_parse_yandex_213_20260409_133000.json`

**Структура:**
```json
{
  "operation": "parse_yandex_213",
  "timestamp": "20260409_133000",
  "time": {
    "total_time": 45.23,
    "timestamp": "20260409_133000"
  },
  "memory": {
    "current_size_kb": 15234.56,
    "peak_size_kb": 18456.78,
    "allocated_kb": 25678.90,
    "freed_kb": 10444.34,
    "net_change_kb": 4567.89
  }
}
```

**Чтение из Python:**
```python
import json

with open('profile_parse_yandex_213_20260409_133000.json') as f:
    report = json.load(f)

print(f"Время: {report['time']['total_time']} сек")
print(f"Память пик: {report['memory']['peak_size_kb']} KB")
```

**Получение списка отчётов:**
```python
from parser_app.profiler import get_profile_reports

reports = get_profile_reports(limit=10)
for report in reports:
    print(f"{report['operation']}: {report['time']['time_seconds']}s")
```

---

## 📈 Анализ результатов

### Интерпретация метрик

#### Время выполнения

| Время | Оценка | Действие |
|---|---|---|
| < 10 сек | ✅ Отлично | Нет проблем |
| 10-30 сек | ⚠️ Нормально | Допустимо для парсинга |
| 30-60 сек | ⚠️ Медленно | Проверить логи |
| > 60 сек | ❌ Критично | Оптимизировать код |

#### Потребление памяти

| Память | Оценка | Действие |
|---|---|---|
| < 10 MB | ✅ Отлично | Нет проблем |
| 10-50 MB | ⚠️ Нормально | Мониторить |
| 50-100 MB | ⚠️ Много | Проверить утечки |
| > 100 MB | ❌ Критично | Оптимизировать |

### Поиск узких мест

**1. По cProfile отчёту:**
```
ncalls  tottime  cumtime  function
10      40.123   40.123   {built-in method sleep}  ← 89% времени!
```

**Вывод:** Большинство времени тратится на `sleep()` - это ожидания между запросами к API.

**2. По Memory отчёту:**
```
#1: 15234.5 KB
    xmlriver.py:200(_parse_xml_response)

#2: 8765.4 KB
    beautifulsoup4:456(find_all)
```

**Вывод:** BeautifulSoup потребляет много памяти при парсинге больших XML.

### Рекомендации по оптимизации

| Проблема | Решение |
|---|---|
| Много `sleep()` | Уменьшить `delay_repeats` или использовать async |
| Большой XML | Использовать `lxml` вместо `html5lib` |
| Повторные запросы | Включить кэширование (`docache`) |
| Много повторов | Увеличить `max_retries_500` или ждать дольше |
| Утечки памяти | Освобождать объекты после использования |

---

## 🛠 Оптимизация производительности

### Настройка параметров

#### 1. Уменьшение времени сна

**Файл:** `xmlriver.py`

```python
class SearchParser:
    def __init__(self, ...):
        self.delay_repeats = 0.5  # Было: 1 сек
```

**Эффект:** Ускоряет парсинг, но может вызвать rate limit.

#### 2. Оптимизация парсинга XML

**Файл:** `xmlriver.py`

```python
# Вместо html5lib использовать lxml (быстрее и меньше памяти)
soup = BeautifulSoup(response.text, 'lxml')  # Вместо 'html5lib'
```

**Требует установки:**
```bash
pip install lxml
```

#### 3. Увеличение количества повторов

**Файл:** `xmlriver.py`

```python
class XMLRiverParser:
    def __init__(self):
        self.max_retries_500 = 6  # Было: 4
```

**Эффект:** Больше попыток при ошибках 500, но дольше выполнение.

### Кэширование

Всегда включайте кэширование для повторных запросов:

```python
# В форме поставьте галочку "Кешировать запросы"
# Или в коде:
docache = True
```

**Эффект:** Повторные запросы выполняются мгновенно (< 0.1 сек).

---

## ❓ Устранение проблем

### Проблема: Нет отчётов в `/parser/profile_reports`

**Причина:** Отчёты ещё не создавались.

**Решение:**
1. Откройте `/parser/profile_reports`
2. Заполните форму и нажмите "Запустить профилирование"
3. Дождитесь завершения

### Проблема: Отчёты занимают много места

**Проверка:**
```bash
ls -lh /home/r/rapcooc5/mklines/public_html/parser/parser_app/profiles/
du -sh profiles/
```

**Очистка:**
```python
from parser_app.profiler import PROFILE_DIR
import os
import glob

# Удаляем все отчёты старше 7 дней
import time
for filepath in glob.glob(os.path.join(PROFILE_DIR, '*')):
    if time.time() - os.path.getmtime(filepath) > 7 * 86400:
        os.remove(filepath)
        print(f"Удалён: {filepath}")
```

### Проблема: Ошибка памяти (MemoryError)

**Симптомы:**
```
MemoryError: Unable to allocate 123 MB
```

**Решение:**
1. Уменьшите `depth` (ТОП-10 вместо ТОП-30)
2. Уменьшите количество запросов
3. Используйте `lxml` вместо `html5lib`
4. Освобождайте память:
```python
import gc
del large_object
gc.collect()
```

### Проблема: Долгие запросы (>60 сек)

**Проверка логов:**
```bash
tail -100 logs/parser.log | grep -E "SLOW|ERROR"
```

**Возможные причины:**

| Причина | Решение |
|---|---|
| Ошибки 500 от XMLRiver | Увеличить `max_retries_500` |
| Rate limit (429) | Уменьшить параллельные запросы |
| Нет свободных каналов (111) | Подождать и повторить |
| Медленный интернет | Проверить соединение |

---

## 📚 Дополнительные материалы

### Полезные команды

**Проверка синтаксиса:**
```bash
cd /home/r/rapcooc5/mklines/public_html/parser/parser_app
python -m py_compile profiler.py __init__.py main.py
```

**Просмотр логов:**
```bash
tail -f logs/parser.log | grep -E "⏱|💾|🐌|📊"
```

**Размер директории профилей:**
```bash
du -sh profiles/
ls -lh profiles/ | head -20
```

### Файлы системы

| Файл | Описание |
|---|---|
| `profiler.py` | Основной модуль профилирования |
| `profiles/` | Директория с отчётами |
| `__init__.py` | Middleware для замеров времени |
| `main.py` | Эндпоинты для веб-интерфейса |
| `templates/profile_reports.html` | Страница отчётов |
| `templates/profile_result.html` | Страница результата |

---

## 📞 Поддержка

При возникновении проблем:

1. Проверьте логи: `logs/parser.log`
2. Запустите тестовое профилирование с 1 запросом
3. Проверьте синтаксис: `python -m py_compile profiler.py`
4. Перезапустите Passenger: `touch tmp/restart.txt`

---

**Последнее обновление:** 9 апреля 2026 г.  
**Версия:** 1.0
