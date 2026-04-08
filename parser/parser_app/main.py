import random
import functools
import requests
import os
from flask import Flask, render_template, request, Response, flash, render_template_string, redirect, url_for, Blueprint

from . import request_parser, db
from flask_login import login_required, current_user
import urllib.parse
from . import request_parser_with_ya_xml
from .parser_utils import colors, prepare_xls, save_csv, save_xls
from . import xmlriver
from .resultobj import ParsingResult, SingleResult
from collections import Counter
from logging import info


main = Blueprint('main', __name__)
info(f"{__name__.split('.')[0]}/lrs.txt")
regions_ya = list(
    map(lambda s: s.strip().replace('"', '').split(','),
        open(f"{__name__.split('.')[0]}/lrs.txt", encoding='utf-8').readlines()))
regions_goo = list(
    map(lambda s: s.strip().replace('"', '').split(','),
        open(f"{__name__.split('.')[0]}/geo.txt", encoding='utf-8').readlines()))

in_search = None
search = None
region = None
engine = None
depth = None
iteration = None
result_of_parsing = ['error']




@main.route("/yasha", methods=['GET'])
def yasha():
    base_link = "https://yandex.ru/search/xml?user=rapcoolglok&key=03.301518843:05b89a7572f21ab21aacd73d7a8e044c"
    res = requests.get(base_link + "&query=собака")
    return render_template('test.html', result=res.text)


@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html', curent_user=current_user)


@main.route("/", methods=["POST", "GET"])
@main.route("/index", methods=["POST", "GET"])
@login_required
def index():
    global result_of_parsing
    info(regions_ya)
    if current_user.user_limit <= 0:
        return redirect('./subscribe')
    same_urls_keys = {}
    if request.method == "POST":
        print("post")
    if request.method == "GET":
        print("get")
    title = "Выгрузка сайтов по запросам в Яндекс и Google"
    # print("keys", request.form.get('keys'))
    # print("cluster_key", request.form.get('cluster_key'))
    # print("cluster-name", request.form.get('cluster-name'))
    try:
        if request.form.get("klastery-inp") and result_of_parsing:
            barrier = request.form.get('klastery-inp')
            print("barrier:", barrier)
            same_urls_keys = get_same_urls_new(result_of_parsing)
            try:
                barrier = int(barrier)
            except:
                barrier = 50
            print(barrier)
            result_of_parsing.calc_clusters(barrier)

        elif request.form.get("keys"):
            global in_search, region, engine, depth, iteration
            in_search = request.form["keys"]
            search = list(filter(lambda x: bool(x), map(lambda x: x.strip(), in_search.split("\r\n"))))
            region = request.form["region"]
            engine = request.form["engine"]
            depth = request.form.get("depth", 10)
            iteration = request.form.get("iteration", "iteration-1")
            docache = True if request.form.get("docache") else False
            print("docache", docache)
            barrier = 50
            try:
                iteration = int(iteration)
                engine = int(engine)
                depth = int(depth)
                region = int(region)
            except Exception as e:
                print("error parser iterations: ", e)
                iteration = 1

            if search:
                result_of_parsing = launch_parser(tuple(search), engine, region, depth, repeats=iteration,
                                                  docache=docache)
                print("end parsing results")
                # Кластеризация выполняется только по запросу пользователя через форму cluster-form
                # Автоматический вызов удален для избежания дублирования
                print("cluster calculation skipped - waiting for user request")
                save_csv(result_of_parsing, current_user.id if current_user.is_authenticated else 'anon')
                #res = prepare_xls(result_of_parsing)
                save_xls(result_of_parsing, current_user.id if current_user.is_authenticated else 'anon')
                print("end save csv")
                same_urls_keys = get_same_urls_new(result_of_parsing)
                print("end get same urls")
                # print("keys=", keys)
                # print("res=", res)
        else:
            return render_template("index_2.html", title=title, progress=False, engine=12, region=str(213), depth=10,
                                   iteration=1,
                                   r_ya=regions_ya,
                                   r_goo=regions_goo)


    except Exception as e:
        print("error", e)
        title = "Произошла ошибка" + str(e)
        return render_template("index_2.html", title=title)
    # print("res.result============:", result_of_parsing.result)
    d_urls, d_hosts = get_urls_count(result_of_parsing.result)
    # pickle.dump(res.result, open("data.txt", "wb"))

    return render_template("index_2.html", title=title, keys=in_search, region=str(region), engine=engine,
                           answer=result_of_parsing.result,
                           same_urls=same_urls_keys, progress=False, depth=depth, iteration=iteration, r_ya=regions_ya,
                           r_goo=regions_goo, d_urls=d_urls, d_hosts=d_hosts, clusters=result_of_parsing.clusters,
                           clusters_colors=result_of_parsing.cluster_colors, barrier=barrier)


@main.route("/clusters", methods=['POST'])
def toclusters():
    return render_template('clusters.html',
                           title="clusters",
                           collision_percent=5,
                           )


@main.route("/getXLS", methods=['GET'])
@login_required
def getXLS():
    try:
        filename = f"results_{current_user.id}.csv"
        file = open(filename, 'rb')
        return Response(file.read(),
                        mimetype="text/csv",
                        headers={"Content-disposition":
                                     f"attachment; filename={filename}"})
    except Exception as e:
        # flash("что-то пошло не так при загрузке файла\n", e)
        return render_template_string("something goes wrong!!!")


@main.route('/subscribe')
def subscription_page():
    return render_template("subscribe.html", current_user=current_user)

def trigger_on_answer(d):
    print("triggered", d)


@functools.lru_cache
def launch_parser(search, engine, region, depth, repeats, docache=True):
    print(search, engine, region, depth, repeats, docache)
    if engine == 11:  # native
        parser = request_parser.SearchParser(search, "yandex", count=depth, repeats=repeats, output_file=None,
                                             region=region, docache=docache)
    elif engine == 12:  # yandex river
        parser = xmlriver.SearchParser(search, "yandex", count=depth, repeats=repeats, region=region, docache=docache)
    elif engine == 13:  # yandex xml
        parser = request_parser_with_ya_xml.YaXmlSearchParser(search, count=depth, repeats=repeats, region=region,
                                                              docache=docache)
    elif engine == 21:
        parser = request_parser.SearchParser(search, "google", count=depth, repeats=repeats, output_file=None,
                                             region=region, docache=docache)
    elif engine == 22:
        parser = xmlriver.SearchParser(search, "google", count=depth, repeats=repeats, region=region, docache=docache)
    else:
        raise Exception(f"wrong system exception {engine}")

    return parser.run_parse()


def get_same_urls_new(res: ParsingResult):
    print("start get same url function")
    # print("arg:", str(res))
    big_dict: dict = res.result
    # with open("parsingres.dat", "wb") as file:
    #     pickle.dump(res, file)
    keys = []
    for big_k in big_dict:
        print("=" * 80)
        print(dict(big_dict[big_k]).keys())
        keys.append(set(dict(big_dict[big_k]).keys()))
        print("=" * 80)
    # print("keys=", keys)
    uniq_urls = set()
    # uniq_urls = functools.reduce(lambda x, y: x & y, keys)
    for i in range(len(keys) - 1):
        for j in range(i + 1, len(keys)):
            uniq_urls.update(keys[i] & keys[j])
    # print("uniq_urls", uniq_urls)

    # return {url: f"#{random.randrange(0x1000000):06x}" for url in uniq_urls}
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
            d[uniq_urls[
                j]] = f"#{random.randrange(0x127):02x}{random.randrange(0x127):02x}{random.randrange(0x127):02x}"
        return d


def get_urls_count(result: dict):
    """counts urls and hosts and returns Counters"""
    d_urls = []
    d_hosts = []
    for k in result:
        last = list(map(lambda t: t[0].url, result[k]))
        d_urls += last
        d_hosts += list(map(lambda url: '{uri.scheme}://{uri.netloc}/'.format(uri=urllib.parse.urlparse(url)), last))
    print("get urls:", d_urls)
    print("get urls:", d_hosts)

    return dict(Counter(d_urls).most_common()), dict(Counter(d_hosts).most_common())
