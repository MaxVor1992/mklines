# XMLRiver API - Полная документация

## 📚 Источники
- https://xmlriver.com/api/api-connect/
- https://xmlriver.com/api/api-alt/
- https://xmlriver.com/api/api-methods/
- https://xmlriver.com/api/api-answer/
- https://xmlriver.com/api/api-errors/
- https://xmlriver.com/api/api-po/
- https://xmlriver.com/apiydoc/apiy-about/
- https://xmlriver.com/apiydoc/apiy-organic/
- https://xmlriver.com/apiysearch/apiys-params/
- https://xmlriver.com/apiysearch/apiys-modes/

---

## 🔑 Аутентификация

Все запросы требуют параметров:
- `user=[user_id]` - ID пользователя
- `key=[key]` - API ключ

**Наши credentials:**
```
user_id: 3089
ключ: 9305a49e48a27d38f87261f26a6346f4d6508b6d
```

**Важно:** Храните credentials в `.env` файле, НЕ в коде!

---

## 🌐 Endpoints

### Основные endpoints для поиска

| Поисковая система | URL |
|---|---|
| **Google** | `http://xmlriver.com/search/xml` |
| **Яндекс** | `http://xmlriver.com/search_yandex/xml` |

### Service API endpoints

| Метод | URL | Описание |
|---|---|---|
| `get_balance` | `http://xmlriver.com/api/get_balance/?user=X&key=Y` | Баланс счёта |
| `get_cost/google` | `http://xmlriver.com/api/get_cost/google/?user=X&key=Y` | Стоимость 1000 запросов Google |
| `get_cost/yandex` | `http://xmlriver.com/api/get_cost/yandex/?user=X&key=Y` | Стоимость 1000 запросов Яндекс |
| `get_cost/yaxml` | `http://xmlriver.com/api/get_cost/yaxml/?user=X&key=Y` | Стоимость 1000 запросов Yandex Search API |
| `get_cost/wordstat` | `http://xmlriver.com/api/get_cost/wordstat/?user=X&key=Y` | Стоимость 1000 запросов Wordstat |
| `get_tarif` | `http://xmlriver.com/api/get_tarif/?user=X&key=Y` | Текущий тариф |
| `get_tarif_expire` | `http://xmlriver.com/api/get_tarif_expire/?user=X&key=Y` | Дата окончания тарифа |

---

## 📝 Параметры запросов

### Обязательные параметры

| Параметр | Описание | Пример |
|---|---|---|
| `query` | Текст поискового запроса | `query=купить+окна` |

**ВАЖНО:** Символ `&` в query нужно заменять на `%26`!

### Параметры выдачи

| Параметр | Тип | Описание | Допустимые значения |
|---|---|---|---|
| `groupby` | int | Количество позиций (ТОП) | **Яндекс:** только `10`<br>**Google:** `10, 20, 30, 50, 100` |
| `page` | int | Номер страницы выдачи | Начиная с `0` |
| `filter` | int | Скрыть похожие результаты | `1` - включить |
| `highlights` | int | Подсветка ключевых слов | `1` - слова в `<hlword>` |
| `within` | int | Фильтр по периоду | `77` - сутки<br>`1` - 2 недели<br>`2` - месяц<br>`0` - весь период |

### География и локализация

| Параметр | Тип | Описание | Пример |
|---|---|---|---|
| `lr` | int | Регион Яндекса (числовой ID) | `lr=213` (Москва) |
| `lang` | string | Код языка | `ru`, `uk`, ... |
| `domain` | string | Домен Яндекса | `ru`, `com`, `ua`, `com.tr`, `by`, ` kz` |

### Специальные параметры XMLRiver

| Параметр | Описание | Значения |
|---|---|---|
| `device` | Эмуляция устройства | `desktop` (по умолчанию), `mobile`, `tablet` |
| `os` | Операционная система (при device=mobile) | `ios`, `android` |
| `format` | Формат выдачи | `xml` (по умолчанию), `html` |
| `ai` | Парсинг "Обзор от ИИ" | `1` (платный, снижает скорость) |
| `raw` | Возврат полного HTML страницы | `page` (отключает delayed режим) |
| `inindex` | Проверка индексации URL | `1` + в query передать URL |
| `strict` | Строгое соответствие URL | `1` (учитывает регистр) |
| `additional` | Дополнительные блоки выдачи | См. ниже |
| `delayed` | Отложенный режим | `1` (асинхронный) |

### Параметр `additional` - дополнительные блоки

Значения (через запятую):

| Значение | Описание |
|---|---|
| `y_topads` | Реклама вверху выдачи |
| `y_bottomads` | Реклама внизу выдачи |
| `y_rightads` | Реклама справа |
| `searchsters` | Колдунщики |
| `searchsters_side` | Колдунщики боковые |
| `scroller` | Карусель |
| `rs_y` | Related Searches |
| `extended_snippet` | Расширенные сниппеты |
| `displayed` | Кол-во показов в месяц |
| `y_cachelink` | Сохранённая копия |
| `y_sitelinks` | Sitelinks (витальный запрос) |
| `y_oneline_sitelinks` | Доп. ссылки в сниппете |
| `knowledge_graph_y` | Карточка компании |
| `y_fullsnippet` | Fullsnippet |
| `y_of` | Блок цен в магазине |
| `y_news` | Блок новостей |

---

## 🔄 Режимы работы

### 1. Гибридный режим (синхронный)

**Для совместимости с Яндекс Search API v1**

- **Формат:** XML
- **Таймаут:** до 10 секунд
- **Активация:** Без параметров

**Пример запроса:**
```
http://xmlriver.com/search_yandex/xml?user=3089&key=YOUR_KEY&query=тест&groupby=10&lr=213
```

**Особенности:**
- Если за 10 сек ответ не получен → ошибка **500**
- После 4 подряд ошибок 500 → ошибка **202**
- Результат хранится **24 часа**
- При ошибке 500 повтор через **5-10 секунд**

### 2. Отложенный режим (асинхронный)

**Для неблокирующего сбора**

- **Формат:** JSON
- **Активация:** `&delayed=1`
- **Недоступен для Яндекс.XML**

**Шаг 1: Создание задачи**
```
GET http://xmlriver.com/search/xml?user=X&key=Y&query=test&delayed=1
→ Ответ: 101 (числовой ID)
```

**Шаг 2: Получение результата**
```
GET http://xmlriver.com/search/xml?req_id=101
```

**Возможные ответы:**
1. **Готовый результат** - обычная XML
2. **`WAIT`** - результат ещё не готов
3. **`ERROR Bad request id`** - ID не найден

**Особенности:**
- Опрос разрешён не чаще чем раз в **10 секунд**
- Результат хранится **менее 10 минут** (не гарантируется дольше)
- Ранний опрос → ошибка **203**

---

## 📦 Формат ответа (XML)

### Структура ответа

```xml
<?xml version="1.0" encoding="utf-8"?>
<yandexsearch version="1.0">
  <response date="20120928T103130">
    <!-- Общая информация -->
    <found priority="all">206775197</found>
    
    <!-- Дополнительные результаты -->
    <addresults>
      <zeroposition>
        <title>Нулевая позиция</title>
        <url>https://...</url>
      </zeroposition>
      <relatedQuestions>
        <question>
          <title>Похожий запрос</title>
        </question>
      </relatedQuestions>
      <knowledge_graph>
        <place_id>ChIJrTLr-GyuEmsRBfy61i59si0</place_id>
        <name>Организация</name>
        <rating>4.5</rating>
        <countReviews>140</countReviews>
        <address>Адрес</address>
        <phone>+7...</phone>
      </knowledge_graph>
    </addresults>
    
    <!-- Основные результаты -->
    <results>
      <grouping>
        <page first="1" last="2">0</page>
        
        <group id="1">
          <doccount>1</doccount>
          <doc>
            <url>http://example.com/</url>
            <title>Заголовок страницы</title>
            <contenttype>organic</contenttype>
            <pubDate>29 авг. 2018 г.</pubDate>
            
            <!-- Сниппеты -->
            <passages>
              <passage>Текст пассажа...</passage>
            </passages>
            
            <fullsnippet>Полный сниппет...</fullsnippet>
            
            <extendedpassages>
              <passage>
                <type>Rating</type>
                <value>4.5</value>
              </passage>
              <passage>
                <type>Address</type>
                <value>Москва, ул....</value>
              </passage>
            </extendedpassages>
            
            <!-- Sitelinks -->
            <sitelinks>
              <sitelink>
                <url>http://example.com/about</url>
                <title>О нас</title>
                <snippet>Информация</snippet>
              </sitelink>
            </sitelinks>
            
            <oneline_sitelinks>
              <sitelink>
                <url>example.com</url>
                <title>Главная</title>
              </sitelink>
            </oneline_sitelinks>
          </doc>
        </group>
        
        <!-- Ещё группы... -->
        
      </grouping>
    </results>
  </response>
</yandexsearch>
```

### Парсинг органических результатов

**Алгоритм:**

1. Найти все `<group id="N">` - `id` = позиция результата
2. Внутри `<group>` найти `<doc>`
3. Проверить `<contenttype>`:
   - `organic` - органический результат ✅
   - Другие значения - пропустить (реклама, колдунщики)
4. Извлечь данные:
   - `<url>` - ссылка
   - `<title>` - заголовок (убрать `<hlword>` теги)
   - `<passages>` - сниппет
   - `<extendedpassages>` - расширенные данные

**Типы contenttype:**
- `organic` - органический результат
- `address` - адрес
- `news` - новости
- `images` - картинки
- `video` - видео
- `maps` - карты
- `market` - маркет
- и другие...

### Подсветка ключевых слов

При `highlights=1`:
- Слова запроса в `<title>` и `<passage>` оборачиваются в `<hlword>`
- Текст заключается в `<![CDATA[...]]>`

**Пример:**
```xml
<title><![CDATA[Купить <hlword>окна</hlword> в Москве]]></title>
```

**Очистка:**
```python
title = title.replace('<hlword>', '').replace('</hlword>', '')
```

---

## ❌ Коды ошибок

### Критические ошибки (остановка сбора)

| Код | Описание | Действие |
|---|---|---|
| `2` | Пустой поисковый запрос | Передать query |
| `31` | Пользователь не зарегистрирован | Проверить user_id |
| `42` | Ошибка в API ключе | Проверить key и URL |
| `45` | IP запрещён | Разрешить IP в настройках |
| `102` | Неверный groupby | Яндекс: 10, Google: 10/20/30/50/100 |
| `103` | Неверный lr | Проверить регион |
| `107` | Для Яндекс только ТОП=10 | Установить groupby=10 |
| `120` | Недопустимые символы | Исправить запрос |
| `200` | Нет денег на счёте | Пополнить баланс |

### Временные ошибки (повтор запроса)

| Код | Описание | Действие |
|---|---|---|
| `101` | Сервис на обновлении | Повторить позже |
| `110` | Превышен лимит потоков | Подождать и повторить |
| `111` | Нет свободных каналов | Подождать и повторить |
| `115` | Превышена частота (HTTP 429) | Ждать N секунд/10 мин |
| `202` | Запрос ещё не обработан | Не останавливать сбор, повторить |
| `203` | Повтор через X сек | Подождать X секунд |
| `204` | Задача не найдена | Повторить запрос |
| `500*` | Сетевая ошибка | **Повторить запрос** (до 20% - норма) |

### Штатные "ошибки"

| Код | Описание | Действие |
|---|---|---|
| `15` | Нет результатов | Обработать как пустой ответ |
| `20-24` | Внутренняя ошибка | Обратиться в поддержку |

---

## 💰 Лимиты и тарифы

### Стандартный аккаунт (Basic)
- **Потоков:** 10 параллельных
- **Яндекс:** ~150,000 запросов/сутки
- **Google:** ~200,000 запросов/сутки

### Тарификация
- Тарифицируются только успешные запросы к поисковику
- Ошибки 500 не тарифицируются
- Повторные запрос тарифицируются

---

## 🛠 Практические рекомендации

### 1. Таймауты

```python
# Для гибридного режима
timeout = 70  # 60 сек max ответ + 10 сек запас

# Задержка между повторами при ошибке 500
time.sleep(10)

# Задержка при rate limit 429
time.sleep(wait_time)  # wait_time = attempt * 10
```

### 2. Retry логика

```python
max_retries_500 = 4

for attempt in range(max_retries_500 + 1):
    try:
        response = requests.get(url, timeout=70)
        
        if response.status_code == 500:
            if attempt < max_retries_500:
                time.sleep(10)
                continue
            else:
                raise Exception("Max retries exceeded")
        
        # Parse response
        break
        
    except requests.Timeout:
        if attempt < max_retries_500:
            time.sleep(10)
            continue
```

### 3. Обработка ошибки 500

> **До 20% ответов с ошибкой 500 - нормальное поведение сервиса**
> Не останавливать сбор, выполнять перезапрос!

### 4. Фильтрация органики

```python
contenttype = doc.find('contenttype')
if contenttype and contenttype.text.strip().lower() != 'organic':
    continue  # Пропустить рекламу
```

### 5. Парсинг сниппетов

```python
# Обычный сниппет
passages = doc.find('passages')
if passages:
    snippet = passages.find('passage').text

# Полный сниппет (приоритет)
fullsnippet = doc.find('fullsnippet')
if fullsnippet:
    snippet = fullsnippet.text

# Очистка от hlword
snippet = snippet.replace('<hlword>', '').replace('</hlword>', '')
```

### 6. Extended данные

```python
extended = []
ext_passages = doc.find('extendedpassages')
if ext_passages:
    for passage in ext_passages.find_all('passage'):
        type_tag = passage.find('type')
        value_tag = passage.find('value')
        if type_tag and value_tag:
            extended.append({
                'type': type_tag.text,
                'value': value_tag.text
            })

# Типы: Rating, Address, Text, Consulting, VerifiedIcon, Video, Image
```

---

## 📝 Примеры кода

### Python - базовый запрос

```python
import requests
from bs4 import BeautifulSoup

user_id = "3089"
key = "YOUR_KEY"
query = "купить окна"

# Формируем запрос
url = f"http://xmlriver.com/search_yandex/xml"
params = {
    'user': user_id,
    'key': key,
    'query': query,
    'groupby': 10,
    'lr': 213,
    'highlights': 1
}

response = requests.get(url, params=params, timeout=70)
soup = BeautifulSoup(response.text, 'html5lib')

# Проверка ошибок
error = soup.find('error')
if error:
    print(f"Error {error.get('code')}: {error.text}")
else:
    # Парсинг результатов
    for group in soup.find_all('group'):
        position = group.get('id')
        doc = group.find('doc')
        
        contenttype = doc.find('contenttype')
        if contenttype.text == 'organic':
            url = doc.find('url').text
            title = doc.find('title').text.replace('<hlword>', '').replace('</hlword>', '')
            print(f"{position}. {title} - {url}")
```

### Проверка баланса

```python
url = f"http://xmlriver.com/api/get_balance/?user=3089&key=YOUR_KEY"
response = requests.get(url)
balance = float(response.text.strip())
print(f"Balance: {balance}")
```

### Отложенный режим (Google)

```python
import time

# Шаг 1: Создание задачи
url = "http://xmlriver.com/search/xml"
params = {
    'user': '3089',
    'key': 'YOUR_KEY',
    'query': 'test',
    'delayed': 1
}

response = requests.get(url, params=params)
req_id = response.text.strip()  # "101"

# Шаг 2: Ожидание и получение
while True:
    time.sleep(10)  # Минимум 10 секунд
    
    url = f"http://xmlriver.com/search/xml?req_id={req_id}"
    response = requests.get(url)
    
    if response.text == 'WAIT':
        continue
    elif 'ERROR' in response.text:
        print("Error:", response.text)
        break
    else:
        # Готовый результат
        soup = BeautifulSoup(response.text, 'html5lib')
        # Парсинг...
        break
```

---

## 🔗 Полезные ссылки

- [XMLRiver - главная](https://xmlriver.com/)
- [Документация API](https://xmlriver.com/api/api-connect/)
- [Настройки сбора](https://xmlriver.com/account/settings) (в личном кабинете)
- [Поддержка](https://xmlriver.com/support)

---

## 📊 Сводная таблица параметров

| Параметр | Яндекс | Google | Обязательный |
|---|---|---|---|
| `query` | ✅ | ✅ | Да |
| `groupby` | Только 10 | 10/20/30/50/100 | Нет (по умолч. 10) |
| `page` | ✅ | ✅ | Нет (0) |
| `lr` | ✅ | ✅ | Нет |
| `filter` | ✅ | ✅ | Нет |
| `highlights` | ✅ | ✅ | Нет |
| `within` | ✅ | ✅ | Нет |
| `lang` | ✅ | ✅ | Нет |
| `domain` | ✅ | ✅ | Нет |
| `device` | ✅ | ✅ | Нет (desktop) |
| `ai` | ✅ | ❌ | Нет |
| `raw` | ✅ | ✅ | Нет |
| `delayed` | ❌ | ✅ | Нет |
| `additional` | ✅ | ✅ | Нет |

---

**Последнее обновление:** 9 апреля 2026 г.
