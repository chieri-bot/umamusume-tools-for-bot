import json
import sqlite3
from . import get_data
from . import exceptions
from . import models as m
import os


spath = os.path.split(__file__)[0]
conn = sqlite3.connect("./pretty-derby/src/assert/master.mdb", check_same_thread=False)
umadb = get_data.load_db("./pretty-derby/src/assert/db.json")

class DataQuery:
    def __init__(self):
        self.conn = conn
        self.cursor = self.conn.cursor()
        self.umadb = umadb


    def get_char_baseinfo(self, char_id: int):
        """
        获取角色基本信息
        :param char_id: 角色ID
        :return: birth_year, birth_month, birth_day, ui_color_main, ui_color_sub, scale
        """
        query = self.cursor.execute("SELECT birth_year, birth_month, birth_day, ui_color_main,ui_color_sub, scale "
                                    "FROM chara_data WHERE id = ?", [char_id]).fetchone()
        birth_year, birth_month, birth_day, ui_color_main, ui_color_sub, scale = query
        return birth_year, birth_month, birth_day, ui_color_main, ui_color_sub, scale

    def get_char_detail_info(self, char_id: int) -> m.UmaDetailInfo:
        """
        获取角色详细信息
        :param char_id: 角色ID
        :return:
        """
        query = self.cursor.execute("SELECT id, category, text FROM text_data WHERE \"index\"=?", [char_id]).fetchall()
        print(114, char_id, query)
        return m.UmaDetailInfo(query, get_measurements=get_data.get_uma_measurements)


    def card_id_to_char_id(self, card_id: int):
        query = self.cursor.execute("SELECT chara_id FROM card_data WHERE id = ?", [card_id]).fetchone()
        if query is None:
            raise exceptions.UmaNotFound(f"没有找到角色卡ID: {card_id}")
        return query[0]

    def get_char_card(self, uma_card_name: str):
        for uma in self.umadb.players:
            card_name = uma.name
            if card_name == uma_card_name:
                return uma
        raise exceptions.UmaNotFound(f"没有找到角色卡: {uma_card_name}")

    def get_char_card_attr(self, card_id: int):
        query = self.cursor.execute("SELECT rarity, speed, stamina, pow, guts, wiz FROM card_rarity_data "
                                    "WHERE card_id = ? AND rarity >= 3", [card_id]).fetchall()
        if not query:
            raise exceptions.UmaNotFound(f"没有找到角色卡id: {card_id}")
        query = sorted(query, key=lambda x: x[0])
        return query

    def search_skill_from_alias(self, query_name: str, startswith=False):
        """
        在 skills.json 中查找
        """
        with open(f"{spath}/data/skills.json", "r", encoding="utf8") as f:
            skill_data = json.load(f)

        get_name_jp = None
        for skill_name_jp in skill_data:
            if (skill_name_jp.startswith(query_name) if startswith else query_name == skill_name_jp):
                get_name_jp = skill_name_jp
                break
            for skill_name_cn in skill_data[skill_name_jp]:
                if (skill_name_cn.startswith(query_name) if startswith else query_name == skill_name_cn):
                    get_name_jp = skill_name_jp
                    break
            if get_name_jp is not None:
                break

        if get_name_jp is None:
            if startswith:
                return self.get_skill_from_umadb(query_name)
            else:
                return self.search_skill_from_alias(query_name, startswith=True)
        else:
            return self.get_skill_from_umadb(get_name_jp)


    def get_skill_from_umadb(self, name: str):
        """
        从umadb精确匹配技能
        """
        for skill in self.umadb.skills:
            if name == skill.name:
                return skill
        return None

    def search_skill(self, query_name: str):
        return self.search_skill_from_alias(query_name)

    def get_skill_from_id(self, skill_id: str):
        for skill in self.umadb.skills:
            if skill.id == skill_id:
                return skill

    def get_char_from_id(self, char_id):
        for char in self.umadb.players:
            if char.id == char_id:
                return char
        return None

    def get_support_card_from_id(self, card_id):
        for card in self.umadb.supports:
            if card.id == card_id:
                return card
        return None

    def get_char_list_from_skill(self, skill_id):
        ret = []
        for char in self.umadb.players:
            if skill_id in char.skillList:
                ret.append(char)
        return ret

    def get_support_card_from_skill(self, skill_id):
        ret = []
        for card in self.umadb.supports:
            if skill_id in card.skillList:
                ret.append(card)
        return ret

    def get_event_from_name(self, event_name: str):
        for event in self.umadb.events:
            if event_name == event.name:
                return event
        return None

    def get_event_from_id(self, event_id: str):
        for event in self.umadb.events:
            if event_id == event.id:
                return event
        return None
