# XMLRiver API - Полное исследование проекта parser

> Дата исследования: 10 апреля 2026 г.

---

## 📚 Часть 1: Документация XMLRiver API

### 🔑 Аутентификация
Все запросы требуют параметров:
- `user=[user_id]` - ID пользователя
- `key=[key]` - API ключ

**Наши credentials:**
```
user_id: 3089
ключ: 9305a49e48a27d38f87261f26a6346f4d6508b6d
```

⚠️ **Важно:** Ключи должны храниться в `.env`, НЕ в коде!

---

### 🌐 Основные endpoints

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

### 📝 Параметры запросов

#### Общие параметры (оба движка)

| Параметр | Тип | Обязательно | Описание | Пример |
|---|---|---|---|---|
| `query` | string | ✅ Да | Текст поискового запроса | `query=купить+окна` |
| `groupby` | int | Нет | Количество позиций (ТОП) | **Яндекс:** только `10`<br>**Google:** `10, 20, 30, 50, 100` |
| `page` | int | Нет | Номер страницы выдачи (с 0) | `page=0` |
| `filter` | int | Нет | Скрыть похожие результаты | `filter=1` |
| `highlights` | int | Нет | Подсветка ключевых слов | `highlights=1` → `<hlword>` теги |
| `within` | int | Нет | Фильтр по периоду | `77` - сутки<br>`1` - 2 недели<br>`2` - месяц<br>`0` - весь период |

#### География и локализация

| Параметр | Тип | Описание | Пример |
|---|---|---|---|
| `lr` | int | Регион (числовой ID) | `lr=213` (Москва для Яндекс) |
| `lang` | string | Код языка | `ru`, `uk`, ... |
| `domain` | string | Домен | Яндекс: `ru`, `com`, `ua`<br>Google: `10` (ru), `143` и др. |

#### Специальные параметры XMLRiver

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
| `setab` | Только рекламные объявления | `ads` |

#### Параметр `additional` - дополнительные блоки

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

### 🔄 Режимы работы

#### 1. Гибридный режим (синхронный)

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
- До 20% ошибок 500 - нормальное поведение

#### 2. Отложенный режим (асинхронный)

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

### 📦 Формат ответа (XML)

#### Структура ответа Яндекс

```xml
<?xml version="1.0" encoding="utf-8"?>
<yandexsearch version="1.0">
  <response date="ГГГГММДДTЧЧММСС">
    <!-- Общая информация -->
    <found priority="all">206775197</found>
    <displayed>10</displayed>
    <correct>исправленный запрос</correct>        <!-- опционально -->
    <fixtype>quotes</fixtype>                      <!-- опционально -->

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
        <type>firm</type>
        <name>Организация</name>
        <rating>4,5</rating>
        <countReviews>140</countReviews>
        <address>Москва, ул....</address>
        <phone>+7...</phone>
        <website>https://...</website>
        <mapurl>https://yandex.ru/maps/...</mapurl>
        <id>139354340355</id>
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

            <!-- Extended данные -->
            <extendedpassages>
              <passage>
                <type>Rating</type>
                <value>4,5</value>
              </passage>
              <passage>
                <type>Address</type>
                <value>Россия, Москва</value>
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

            <!-- Turbo-страницы -->
            <properties>
              <TurboLink>https://...turbopages.org/...</TurboLink>
            </properties>

            <!-- Лучший ответ (мобильная выдача) -->
            <microdata>Краткий ответ...</microdata>
            <microdatalong>Полный ответ...</microdatalong>
          </doc>
        </group>

      </grouping>
    </results>

    <!-- Карусель -->
    <scroller>
      <item>
        <domain>Яндекс.Маркет</domain>
      </item>
    </scroller>
  </response>
</yandexsearch>
```

#### Типы contenttype

| Тип | Описание |
|---|---|
| `organic` | Органический результат ✅ |
| `address` | Адрес |
| `afisha` | Афиша |
| `avia` | Авиабилеты |
| `businessChatCenter` | Бизнес-чат |
| `calculator` | Калькулятор |
| `colors` | Цвета |
| `converter` | Конвертер величин |
| `convertercurrency` | Конвертер валют |
| `fact` | Факты |
| `formula` | Формулы |
| `images` | Картинки |
| `index` | Индекс |
| `ipaddress` | Определение IP |
| `lyrics` | Тексты песен |
| `maps` | Карты |
| `market` | Маркет |
| `misspell` | Исправление опечаток |
| `music` | Музыка |
| `news` | Новости |
| `quotes` | Котировки |
| `shedule` | Расписание |
| `sportscore` | Спортивные результаты |
| `time` | Время |
| `translate` | Переводчик |
| `uslugi` | Услуги |
| `video` | Видео |
| `weather` | Погода |

#### Extendedpassages типы

| Тип | Описание |
|---|---|
| `Address` | Адрес организации |
| `Text` | Произвольный текст (телеф, описание) |
| `Rating` | Рейтинг |
| `Consulting` | Консультация |
| `VerifiedIcon` | Верифицированная организация |
| `Video` | Видео |
| `Image` | Изображение |

---

### ❌ Коды ошибок

#### Критические ошибки (остановка сбора)

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

#### Временные ошибки (повтор запроса)

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

#### Штатные "ошибки"

| Код | Описание | Действие |
|---|---|---|
| `15` | Нет результатов | Обработать как пустой ответ |
| `20-24` | Внутренняя ошибка | Обратиться в поддержку |

---

### 📊 Органическая выдача - детально

#### Поля результата

| Тег | Описание |
|:---|:---|
| `<response date="...">` | Корневой контейнер ответа с датой и временем запроса |
| `<found priority="all">` | Общее количество найденных документов в базе |
| `<displayed>` | Количество документов, возвращённых в текущей выдаче |
| `<correct>` | Исправленная поисковая фраза (автоисправление опечаток) |
| `<fixtype>` | Тип корректировки (`quotes` = без учёта кавычек) |
| `<results>` | Контейнер для групп результатов поиска |
| `<group id="...">` | Группа выдачи (id = позиция результата) |
| `<doccount>` | Количество документов внутри группы (всегда 1) |
| `<doc>` | Отдельный элемент выдачи |
| `<url>` | URL целевой страницы |
| `<title>` | Заголовок страницы/результата (содержит `<hlword>` при highlights=1) |
| `<passages> / <passage>` | Основной текстовый сниппет |
| `<contenttype>` | Тип блока (`organic`, `address`, `news`, `images`, и др.) |
| `<sitelinks> / <oneline_sitelinks>` | Контейнер быстрых ссылок |
| `<sitelink> / <url>, <title>, <snippet>` | Элемент быстрой ссылки |
| `<extendedpassages> / <passage>` | Расширенный сниппет (пары `<type>` и `<value>`) |
| `<fullsnippet>` | Полный текст сниппета (требует настройки в кабинете) |
| `<microdata>` | Краткая версия блока «Лучший ответ» (мобильная выдача) |
| `<microdatalong>` | Полная версия блока «Лучший ответ» |
| `<properties> / <TurboLink>` | Прямая ссылка на турбо-страницу Яндекс |

---

### 📊 AI Обзор (Обзор от ИИ)

#### Параметры
- `ai=1` - для получения содержимого блока
- Без `ai=1` - только метаинформация (координаты)

#### Структура ответа

**Базовый режим (без ai=1):**
```xml
<ai>
  <item>
    <type>center</type>
    <position>0</position>
    <content></content>
  </item>
</ai>
```

**Расширенный режим (с платными параметрами):**
```xml
<ai>
  <item>
    <content>PGhxIHN0eWxlPSJtYXJnaW46IDA7cGFkZGluZzogMDtjb2...</content>
    <position>0</position>
    <type>right</type>
  </item>
</ai>
```

> `<content>` содержит HTML в кодировке Base64. Декодировать для получения HTML.

---

### 📊 Реклама

#### Активация
Добавить параметр `setab=ads` для получения только рекламных объявлений.

#### Структура ответа

```xml
<advcount>2</advcount>
<topads>
  <query>
    <url>apple.com</url>
    <title>%3Cb%3EiPhone%3C/b%3E - Официальный сайт</title>
    <snippet>%3C!-- --%3E Новые %3Cb%3EiPhone%3C/b%3E 13...</snippet>
  </query>
</topads>
<bottomads>
  <query>
    <url>shop.mts.ru</url>
    <title>Купи смартфон Apple iPhone в МТС</title>
    <snippet>...описание...</snippet>
  </query>
</bottomads>
<rightads>
  <query>...</query>
</rightads>
```

> `title` и `snippet` возвращаются в URL-кодированном виде. Декодировать через `urllib.parse.unquote()`.

---

### 📊 Карусель (Scroller)

```xml
<scroller>
  <item>
    <domain>Яндекс.Маркет</domain>
  </item>
</scroller>
```

> Возвращается только при наличии карусели в результатах поиска.

---

### 📊 Knowledge Graph (для Яндекс)

```xml
<knowledge_graph>
  <type>firm</type>
  <name>Krasnogorsk club</name>
  <countReviews>2</countReviews>
  <address>Успенская ул., 12, Красногорск</address>
  <phone>+7 (977) 833-81-43</phone>
  <website>https://vk.com/krasnogorsk_club</website>
  <mapurl>https://yandex.ru/maps/org/...</mapurl>
  <id>139354340355</id>
  <rating>4,1</rating>
</knowledge_graph>
```

> Возвращает данные только для графа знаний, относящегося к предприятиям (фирмам).

---

## 🔍 Часть 2: Как API используется в нашем проекте

### 📁 Файлы проекта

| Файл | Назначение |
|---|---|
| `xmlriver.py` | **Основной файл** - работа с XMLRiver API |
| `request_parser.py` | Нативный HTML-парсинг (без XMLRiver) |
| `request_parser_with_ya_xml.py` | Прямой Яндекс XML (не через XMLRiver) |
| `xmlriver_multi.py` | Альтернативная реализация XMLRiver (устарела) |
| `main.py` | Маршруты Flask, диспетчеризация движков |
| `parse_google_geo.py` | Парсинг geo.csv (не относится к XMLRiver) |

---

### 🎯 Движки парсинга

| Код | Движок | Класс | API |
|---|---|---|---|
| **11** | Yandex native (HTML) | `request_parser.SearchParser` | Прямой HTML парсинг yandex.ru |
| **12** | Yandex XMLRiver | `xmlriver.SearchParser` | `http://xmlriver.com/search_yandex/xml` |
| **13** | Yandex XML (прямой) | `request_parser_with_ya_xml.YaXmlSearchParser` | `https://yandex.ru/search/xml` |
| **21** | Google native (HTML) | `request_parser.SearchParser` | Прямой HTML парсинг google.com |
| **22** | Google XMLRiver | `xmlriver.SearchParser` | `http://xmlriver.com/search/xml` |

---

### 🔧 xmlriver.py - основной файл

#### Используемые endpoints

| Endpoint | Назначение |
|---|---|
| `http://xmlriver.com/search_yandex/xml` | Поиск через Яндекс |
| `http://xmlriver.com/search/xml` | Поиск через Google |
| `http://xmlriver.com/api/get_balance/` | Получение баланса |
| `http://xmlriver.com/api/get_cost/{system}/` | Стоимость 1000 запросов |

#### Параметры запросов

**Общие (оба движка):**
- `user`, `key` - credentials
- `query` - поисковый запрос (`&` → `%26`)
- `groupby` - ТОП (Яндекс: только 10, Google: 10/20/30/50/100)
- `page` - страница выдачи (с 0)
- `filter` - фильтр дублей (1 если filter_dup=True)
- `highlights` - подсветка слов (1 если highlights=True)
- `within` - фильтр по периоду (77=сутки, 1=2нед, 2=мес, 0=весь)

**Специфичные для Яндекс:**
- `lang` - код языка (ru)
- `domain` - домен Яндекса (ru, com, ua)
- `device` - устройство (desktop, mobile, tablet)
- `lr` - регион Яндекса (213 = Москва)

**Специфичные для Google:**
- `lr=143` - язык ru
- `country=2643` - страна
- `domain=143` - домен ru
- `device` - устройство

#### Парсинг ответа

Извлекаемые данные:
- ✅ `found/displayed` - число результатов
- ✅ `correct/fixtype` - исправленный запрос
- ✅ **organic результаты** - ТОЛЬКО `<contenttype>organic</contenttype>`
- ✅ `url`, `title`, `snippet` (из passages/fullsnippet)
- ✅ `extendedpassages` - расширенные данные (рейтинг, отзывы, цены)
- ✅ `sitelinks` - дополнительные ссылки

НЕ извлекаются:
- ❌ Колдунщики (фильтруются по contenttype != organic)
- ❌ Реклама (фильтруется)
- ❌ Карусель
- ❌ Knowledge Graph
- ❌ AI Обзор
- ❌ Related Searches
- ❌ Новости

#### Обработка ошибок

| Код | Обработка |
|---|---|
| **15** | Нет результатов → возвращается `{'results': []}` |
| **101** | Сервис на обновлении → retry через 10 сек |
| **110, 111** | Нет свободных каналов → ожидание 60+30*attempt сек, retry |
| **115** | Превышена частота → ожидание 60 сек, retry |
| **500** | Сетевая ошибка → до 4 retry с задержкой (20с, 25с, 30с...) |
| **HTTP 429** | Rate limit → ожидание (attempt+1)*10 сек |
| **HTTP 5xx** | Серверная ошибка → до 4 retry с задержкой 10 сек |
| **2, 20-24, 31, 42, 45, 102, 103, 107, 120, 200** | Критические → исключение |

#### Режим работы

**Только гибридный режим (живой поиск)**. Отложенный режим НЕ используется.
- Таймаут: 70 секунд (60 сек max ответ + 10 сек запас)
- Retry при 500: до 4 попыток с нарастающей задержкой

#### Параллелизм

- `ThreadPoolExecutor` с `max_workers=min(len(requests), 5)`
- Максимум 5 параллельных запросов
- Потокобезопасность через `threading.Lock`

---

### 🔧 request_parser.py - нативный HTML парсинг

**НЕ использует XMLRiver API!**

| Endpoint | Назначение |
|---|---|
| `http://yandex.ru/search` | Прямой HTML парсинг Яндекса |
| `http://google.com/search` | Прямой HTML парсинг Google |

- Использует `fake_headers` для генерации заголовков
- LRU-кэш через `timed_lru_cache` (12 часов)
- CAPTCHA детектится по классам

---

### 🔧 request_parser_with_ya_xml.py - прямой Яндекс XML

| Endpoint | Назначение |
|---|---|
| `https://yandex.ru/search/xml` | Прямой Яндекс XML (не XMLRiver) |

- Минимальный парсер - только URL и title
- Нет обработки retry
- Credentials из env: `YANDEX_XML_USER`, `YANDEX_XML_KEY`

---

### 🔧 xmlriver_multi.py - альтернативная реализация

**⚠️ Устарела, ключи захардкожены!**

| Endpoint | Назначение |
|---|---|
| `http://xmlriver.com/search_yandex/xml` | Яндекс через XMLRiver |
| `http://xmlriver.com/search/xml` | Google через XMLRiver |

- Минимальный парсинг (только URL и title)
- `delay_repeats = 0.01` секунды (очень маленький)
- **Ключи захардкожены в файле** - небезопасно!

---

### 📊 Сводная таблица используемых API методов

| Метод XMLRiver | Используется? | Где |
|---|---|---|
| **organic (поиск)** | ✅ Да | `xmlriver.py` |
| **колдунщики/виджеты** | ❌ Нет | Фильтруются по contenttype != organic |
| **реклама** | ❌ Нет | Фильтруется |
| **подсказки (suggest)** | ❌ Нет | Не реализовано |
| **AI-обзор** | ❌ Нет | Не реализовано |
| **get_balance** | ✅ Да | `xmlriver.py` |
| **get_cost** | ✅ Да | `xmlriver.py` |
| **Карусель** | ❌ Нет | Не извлекается |
| **Knowledge Graph** | ❌ Нет | Не извлекается |
| **Related Searches** | ❌ Нет | Не извлекается |
| **Wordstat** | ❌ Нет | Маппинг есть, но не вызывается |

---

### 💡 Рекомендации по улучшению

#### 1. Добавить парсинг колдунщиков
Сейчас все не-organic результаты фильтруются. Можно извлекать:
- Карты (`maps`)
- Новости (`news`)
- Картинки (`images`)
- Видео (`video`)
- И другие

**Как:** Убрать фильтр `contenttype != organic` и добавить обработку разных типов.

#### 2. Добавить парсинг рекламы
Сейчас реклама пропускается. Можно собирать рекламные URL для анализа конкурентов.

**Как:** Добавить параметр `additional=y_topads,y_bottomads,y_rightads` и парсить `<topads>`, `<bottomads>`.

#### 3. Добавить AI Обзор
Платная опция, но даёт доступ к AI-генерированному контенту.

**Как:** Добавить параметр `ai=1` и парсить `<ai><item><content>` (Base64 декодировать).

#### 4. Добавить Knowledge Graph
Данные о компаниях (рейтинг, адрес, телефон, отзывы).

**Как:** Добавить параметр `additional=knowledge_graph_y` и парсить `<knowledge_graph>`.

#### 5. Добавить Related Searches
Похожие запросы от Яндекса.

**Как:** Парсить `<addresults><relatedQuestions><question><title>`.

#### 6. Добавить Zero Position
Нулевая позиция в выдаче.

**Как:** Парсить `<addresults><zeroposition><title>` и `<url>`.

#### 7. Использовать отложенный режим для больших объёмов
Сейчас используется только гибридный режим (таймаут 70 сек). Для больших списков запросов отложенный режим может быть эффективнее.

**Как:** Добавить параметр `delayed=1` и цикл опроса результата по `req_id`.

#### 8. Убрать хардкод ключей из `xmlriver_multi.py`
Ключи должны читаться из `.env` файла.

---

## 📊 Сводная таблица параметров движков

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

## 🚀 Тест скорости

### Как запустить тест из браузера Chrome:

1. Войди как **Admin** (admin@parser.ru / qwerty1#)
2. Открой: `https://mklines.ru/parser/index`
3. Нажми кнопку **🚀 Тест скорости** (рядом с заголовком, видна только Admin)
4. Тест запустится автоматически в фоне
5. Через 30-60 секунд появится таблица с результатами

> ⚠️ Кнопка доступна **только пользователям с ролью Admin**. Обычные пользователи её не видят.

**Конфигурация теста:**

| # | Запросы | Город | Регион ID | Кеширование |
|---|---|---|---|---|
| 1 | 11 запросов — запуск 1 | **Москва** | 213 | ❌ Отключено |
| 2 | 11 запросов — запуск 2 | **Новосибирск** | 65 | ❌ Отключено |
| 3 | 5 запросов — запуск 1 | **Москва** | 213 | ❌ Отключено |
| 4 | 5 запросов — запуск 2 | **Новосибирск** | 65 | ❌ Отключено |

> 💡 Разные города для разных запусков — тест проверяет работу с разными регионами Яндекса. Кеширование **полностью отключено** — каждый запрос реальный.

**Показывает:**
- Время выполнения каждого запуска (сек)
- Количество успешных запросов
- Общее количество результатов
- Статистику: среднее / мин / макс время

### Как запустить тест из консоли:

```bash
cd /home/r/rapcooc5/mklines/public_html/parser
venv38_flask/bin/python speed_test.py
```

### API endpoint для теста скорости:

| Метод | URL | Описание | Доступ |
|---|---|---|---|
| `POST` | `/parser/api/speed_test` | Запустить тест | Только Admin |
| `GET` | `/parser/api/speed_test` | Проверить статус | Только Admin |

**Пример ответа:**
```json
{
  "status": "done",
  "progress": 100,
  "current": "Завершено!",
  "results": [
    {
      "test": "11 запросов",
      "run": 1,
      "city": "Москва",
      "region_id": 213,
      "time_sec": 18.5,
      "queries": 11,
      "successful": 11,
      "total_results": 110,
      "cache": false
    },
    {
      "test": "11 запросов",
      "run": 2,
      "city": "Новосибирск",
      "region_id": 65,
      "time_sec": 22.1,
      "queries": 11,
      "successful": 11,
      "total_results": 110,
      "cache": false
    }
  ],
  "stats": {"avg": 20.3, "min": 18.5, "max": 22.1}
}
```

---

## ⚡ Оптимизации производительности

### Применённые оптимизации (10 апреля 2026):

| Параметр | Было | Стало | Эффект |
|---|---|---|---|
| Connection pool | Default (10) | **20** соединений | +15-20% при параллельных |
| Retry ошибка 500 | 8с/11с/14с | **5с/7с/9с** | В 1.6 раза быстрее |
| Retry ошибка 110/111 | 30с/45с/60с | **15с/25с/35с** | В 2 раза быстрее |
| Retry таймаут | 10 сек | **5 сек** | В 2 раза быстрее |
| Retry RequestException | 5 сек | **3 сек** | На 40% быстрее |
| Rate limit 115 | 60 сек | **30 сек** | В 2 раза быстрее |
| delay_repeats (XMLRiverParser) | 0.5 сек | **0.1 сек** | На 80% быстрее |
| delay_repeats (SearchParser) | 1 сек | **0.2 сек** | На 80% быстрее |
| Порог отложенного режима | ≥10 → ≥5 | **≥20** | Гибридный быстрее для <20 |
| max_workers | 5 → 8 | **10** | Полный лимит XMLRiver |

### Ожидаемое время выполнения:

| Сценарий | Ожидаю |
|---|---|
| 11 запросов, без ошибок | **~15-18 сек** |
| 11 запросов, 1-2 ошибки 500 | **~20-25 сек** |
| 5 запросов, без ошибок | **~8-10 сек** |

---

**Последнее обновление:** 10 апреля 2026 г.
**Версия документации:** 3.0
