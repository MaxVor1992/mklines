# -*- coding: utf-8 -*-
import random
import functools
import requests
import os
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from flask import Flask, render_template, request, Response, flash, render_template_string, redirect, url_for, Blueprint, session, jsonify

from . import db
from flask_login import login_required, current_user
import urllib.parse
from .parser_utils import colors, prepare_xls, save_csv, save_xls
from .resultobj import ParsingResult, SingleResult
from collections import Counter
from logging import info
import pickle
import json

main = Blueprint('main', __name__)

# Глобальные переменные для хранения состояния парсинга
parsing_tasks = {}
parsing_results = {}

info(f"{__name__.split('.')[0]}/lrs.txt")

# Загрузка регионов
def load_regions():
    """Загружает списки регионов из файлов"""
    try:
        with open(f"{__name__.split('.')[0]}/lrs.txt", encoding='utf-8') as f:
            regions_ya = [s.strip().replace('"', '').split(',') for s in f.readlines()]
    except Exception as e:
        info(f"Error loading lrs.txt: {e}")
        regions_ya = []
    
    try:
        with open(f"{__name__.split('.')[0]}/geo.txt", encoding='utf-8') as f:
            regions_goo = [s.strip().replace('"', '').split(',') for s in f.readlines()]
    except Exception as e:
        info(f"Error loading geo.txt: {e}")
        regions_goo = []
    
    return regions_ya, regions_goo

regions_ya, regions_goo = load_regions()

# Константы по умолчанию
DEFAULT_ENGINE = 12
DEFAULT_REGION = 213
DEFAULT_DEPTH = 10
DEFAULT_ITERATION = 1


@main.route("/yasha", methods=['GET'])
def yasha():
    base_link = "https://yandex.ru/search/xml?user=rapcoolglok&key=03.301518843:05b89a7572f21ab21aacd73d7a8e044c"
    res = requests.get(base_link + "&query=собака", timeout=30)
    return render_template('test.html', result=res.text)


@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html', curent_user=current_user)


def run_parser_async(task_id, search, engine, region, depth, iteration, docache):
    """Асинхронный запуск парсера в отдельном потоке"""
    try:
        result = launch_parser(tuple(search), engine, region, depth, repeats=iteration, docache=docache)
        parsing_results[task_id] = {
            'status': 'completed',
            'result': result,
            'error': None
        }
    except Exception as e:
        info(f"Parser error: {e}")
        parsing_results[task_id] = {
            'status': 'failed',
            'result': None,
            'error': str(e)
        }


@main.route("/", methods=["POST", "GET"])
@main.route("/index", methods=["POST", "GET"])
@login_required
def index():
    global regions_ya, regions_goo
    
    if current_user.user_limit <= 0:
        return redirect('./subscribe')
    
    same_urls_keys = {}
    title = "Выгрузка сайтов по запросам в Яндекс и Google"
    
    # Обработка POST запроса
    if request.method == "POST":
        info("Processing POST request")
        
        # Проверка на кластеризацию
        if request.form.get("klastery-inp"):
            barrier = request.form.get('klastery-inp')
            info(f"Clustering with barrier: {barrier}")
            
            task_id = session.get('last_task_id')
            if task_id and task_id in parsing_results:
                result_of_parsing = parsing_results[task_id]['result']
                if result_of_parsing:
                    try:
                        barrier = int(barrier)
                    except:
                        barrier = 50
                    
                    result_of_parsing.calc_clusters(barrier)
                    same_urls_keys = get_same_urls_new(result_of_parsing)
                    
                    # Сохранение результатов
                    save_csv(result_of_parsing, current_user.id if current_user.is_authenticated else 'anon')
                    save_xls(result_of_parsing, current_user.id if current_user.is_authenticated else 'anon')
                else:
                    flash('Результаты парсинга не найдены')
        
        # Запуск нового парсинга
        elif request.form.get("keys"):
            in_search = request.form["keys"]
            search = list(filter(lambda x: bool(x), map(lambda x: x.strip(), in_search.split("\r\n"))))
            
            try:
                region = int(request.form["region"])
                engine = int(request.form["engine"])
                depth = int(request.form.get("depth", 10))
                iteration = int(request.form.get("iteration", "1"))
            except Exception as e:
                info(f"Error parsing form data: {e}")
                region = DEFAULT_REGION
                engine = DEFAULT_ENGINE
                depth = DEFAULT_DEPTH
                iteration = DEFAULT_ITERATION
            
            docache = True if request.form.get("docache") else False
            barrier = 50
            
            if search:
                # Ограничение количества запросов для предотвращения 504
                max_queries = current_user.user_limit if not current_user.has_role('Admin') else 100
                if len(search) > max_queries:
                    flash(f'Слишком много запросов. Максимум: {max_queries}')
                    return render_template("index_2.html", title=title, progress=False, 
                                         engine=engine, region=str(region), depth=depth,
                                         iteration=iteration, r_ya=regions_ya, r_goo=regions_goo)
                
                # Создаем уникальный ID задачи
                task_id = f"{current_user.id}_{int(time.time())}"
                session['last_task_id'] = task_id
                
                # Запускаем парсер в фоновом потоке
                thread = threading.Thread(
                    target=run_parser_async,
                    args=(task_id, search, engine, region, depth, iteration, docache)
                )
                thread.daemon = True
                thread.start()
                
                parsing_tasks[task_id] = {
                    'status': 'running',
                    'started_at': time.time(),
                    'query_count': len(search)
                }
                
                # Возвращаем страницу с прогрессом
                return render_template("index_2.html", title=title, keys=in_search, 
                                     region=str(region), engine=engine,
                                     progress=True, task_id=task_id,
                                     depth=depth, iteration=iteration, 
                                     r_ya=regions_ya, r_goo=regions_goo)
    
    # GET запрос или после завершения парсинга
    task_id = session.get('last_task_id')
    result_of_parsing = None
    
    if task_id and task_id in parsing_results:
        task_result = parsing_results[task_id]
        if task_result['status'] == 'completed':
            result_of_parsing = task_result['result']
            same_urls_keys = get_same_urls_new(result_of_parsing)
            d_urls, d_hosts = get_urls_count(result_of_parsing.result)
            
            return render_template("index_2.html", title=title, keys=None, 
                                 region=str(DEFAULT_REGION), engine=DEFAULT_ENGINE,
                                 answer=result_of_parsing.result,
                                 same_urls=same_urls_keys, progress=False, 
                                 depth=DEFAULT_DEPTH, iteration=DEFAULT_ITERATION, 
                                 r_ya=regions_ya, r_goo=regions_goo, 
                                 d_urls=d_urls, d_hosts=d_hosts, 
                                 clusters=result_of_parsing.clusters,
                                 clusters_colors=result_of_parsing.cluster_colors, 
                                 barrier=50)
        elif task_result['status'] == 'failed':
            flash(f"Ошибка парсинга: {task_result['error']}")
    
    # Показываем форму
    return render_template("index_2.html", title=title, progress=False, 
                         engine=DEFAULT_ENGINE, region=str(DEFAULT_REGION), 
                         depth=DEFAULT_DEPTH, iteration=DEFAULT_ITERATION,
                         r_ya=regions_ya, r_goo=regions_goo)


@main.route("/task_status/<task_id>")
@login_required
def task_status(task_id):
    """API endpoint для проверки статуса задачи"""
    if task_id in parsing_results:
        result = parsing_results[task_id]
        return jsonify({
            'status': result['status'],
            'error': result['error']
        })
    elif task_id in parsing_tasks:
        return jsonify({'status': 'running'})
    else:
        return jsonify({'status': 'not_found'}), 404


@main.route("/clusters", methods=['POST'])
def toclusters():
    return render_template('clusters.html', title="clusters", collision_percent=5)


@main.route("/getXLS", methods=['GET'])
@login_required
def getXLS():
    try:
        filename = f"results_{current_user.id}.csv"
        file = open(filename, 'rb')
        return Response(file.read(),
                        mimetype="text/csv",
                        headers={"Content-disposition": f"attachment; filename={filename}"})
    except Exception as e:
        info(f"Error downloading file: {e}")
        flash("Что-то пошло не так при загрузке файла")
        return redirect(url_for('main.index'))


@main.route('/subscribe')
def subscription_page():
    return render_template("subscribe.html", current_user=current_user)


def trigger_on_answer(d):
    info(f"Triggered: {d}")


@functools.lru_cache(maxsize=128)
def launch_parser(search, engine, region, depth, repeats, docache=True):
    """Запуск парсера с кэшированием результатов"""
    info(f"Launching parser: search={len(search)} queries, engine={engine}, region={region}, depth={depth}, repeats={repeats}")
    
    if engine == 11:  # native yandex
        from . import request_parser
        parser = request_parser.SearchParser(
            search, "yandex", count=depth, repeats=repeats, 
            output_file=None, region=region, docache=docache
        )
    elif engine == 12:  # yandex river
        from . import xmlriver
        parser = xmlriver.SearchParser(
            search, "yandex", count=depth, repeats=repeats, 
            region=region, docache=docache
        )
    elif engine == 13:  # yandex xml
        from . import request_parser_with_ya_xml
        parser = request_parser_with_ya_xml.YaXmlSearchParser(
            search, count=depth, repeats=repeats, 
            region=region, docache=docache
        )
    elif engine == 21:  # native google
        from . import request_parser
        parser = request_parser.SearchParser(
            search, "google", count=depth, repeats=repeats, 
            output_file=None, region=region, docache=docache
        )
    elif engine == 22:  # google river
        from . import xmlriver
        parser = xmlriver.SearchParser(
            search, "google", count=depth, repeats=repeats, 
            region=region, docache=docache
        )
    else:
        raise Exception(f"wrong system exception {engine}")

    return parser.run_parse()


def get_same_urls_new(res: ParsingResult):
    """Получение одинаковых URL между запросами"""
    info("Getting same URLs")
    big_dict = res.result
    keys = []
    
    for big_k in big_dict:
        keys.append(set(dict(big_dict[big_k]).keys()))
    
    uniq_urls = set()
    for i in range(len(keys) - 1):
        for j in range(i + 1, len(keys)):
            uniq_urls.update(keys[i] & keys[j])
    
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
            d[uniq_urls[j]] = f"#{random.randrange(0x127):02x}{random.randrange(0x127):02x}{random.randrange(0x127):02x}"
        return d


def get_urls_count(result: dict):
    """Подсчет URL и хостов"""
    d_urls = []
    d_hosts = []
    
    for k in result:
        last = list(map(lambda t: t[0].url, result[k]))
        d_urls += last
        d_hosts += list(map(lambda url: '{uri.scheme}://{uri.netloc}/'.format(uri=urllib.parse.urlparse(url)), last))
    
    info(f"Found {len(d_urls)} URLs, {len(set(d_hosts))} unique hosts")
    return dict(Counter(d_urls).most_common()), dict(Counter(d_hosts).most_common())
