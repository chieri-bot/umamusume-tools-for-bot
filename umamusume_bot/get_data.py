import json
from . import models
import os
from . import fts
import requests
import time


spath = os.path.split(__file__)[0]
cache_time = {}

with open("./pretty-derby/src/assert/cn.json", "r", encoding="utf8") as f:
    i18n_cn = json.load(f)


def update_database(folder="pretty-derby", tree="master"):
    """
    使用git命令更新仓库
    :param folder: 目标文件夹
    :param tree: 目标分支
    :return: git执行结果
    """
    result = os.popen(f"cd {folder} && git pull origin {tree}")
    return result.read()


def load_db(file_path: str):
    with open(file_path, "r", encoding="utf8") as f:
        data = json.load(f)
    return models.UraraDb(**data)


def get_trans(name):
    return i18n_cn[name] if name in i18n_cn else name

def get_skill_trans(name: str):
    with open(f"{spath}/data/skills.json", "r", encoding="utf8") as fl:
        skill_trans = json.load(fl)
    return skill_trans[name][0] if name in skill_trans else get_trans(name)


def query_alias(name: str, fuzzy_match=False):
    """
    别称查找马娘
    :param name: 别称
    :param fuzzy_match: 是否模糊匹配
    :return: uma_name, card_name, alias
    """
    max_result = ["", "", ""]
    max_r = 0.0
    with open(f"{spath}/data/uma_alias.json", "r", encoding="utf8") as f:
        data = json.load(f)

    for uma_name in data:
        for card_name in data[uma_name]:
            if name == card_name:
                return [uma_name, card_name, card_name]
            elif name == uma_name:
                return [uma_name, card_name, card_name]

            for alias in data[uma_name][card_name]:
                if name == alias:
                    return [uma_name, card_name, alias]

                if fuzzy_match:
                    _simi = fts.get_str_similarity(name, alias)
                    if _simi > max_r:
                        max_r = _simi
                        max_result = [uma_name, card_name, alias]

    return max_result

def get_official_char_info(use_cache=True):
    global cache_time

    def get_char_data():
        get_data = []
        count = 0
        while True:
            count += 1
            url = f"https://umamusume.jp/app/wp-json/wp/v2/character?per_page=12&page={count}"
            headers = {"Referer": "https://umamusume.jp/character/"}
            response = requests.request("GET", url, headers=headers)
            if response.status_code == 200:
                try:
                    _data = json.loads(response.text)
                    get_data += _data
                    if len(_data) < 12:
                        break
                except:
                    return

        with open(f"{spath}/web_character.json", "w", encoding="utf8") as fl:
            fl.write(json.dumps(get_data, indent=4, ensure_ascii=False))
            cache_time["web_char"] = time.time()

    if os.path.isfile(f"{spath}/web_character.json") and use_cache:
        if "web_char" not in cache_time:
            cache_time["web_char"] = time.time()
        last_refresh = cache_time["web_char"]
        time_pass = time.time() - last_refresh
        if time_pass > 21600:
            get_char_data()
    else:
        get_char_data()

    with open(f"{spath}/web_character.json", "w", encoding="utf8") as fl:
        data = json.load(fl)
    return data

def get_uma_measurements(name_jp: str):
    with open(f"{spath}/src/umamusume_info.json", "r", encoding="utf8") as f:
        data = json.load(f)
    if name_jp in data:
        if "measurements" in data[name_jp]:
            return data[name_jp]["measurements"]
    return None
