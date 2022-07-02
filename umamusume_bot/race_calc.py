import json
import os
from typing import List
from . import models as m


spath = os.path.split(__file__)[0]


class TitleData:
    def __init__(self, srace: dict):
        self.id = srace["id"]  # 比赛ID
        self.name = srace["n"]  # 事件名称
        self.get_effect = srace["ben"]  # 获得效果描述
        self.get_effect_value = srace["bv"]  # 获得能力值
        self.site = srace["f"]  # 场地适性
        self.dist = srace["d"]  # 距离适性
        self.races = srace["fm"]  # 比赛二维列表
        # self.race_list = srace["r"]  # 比赛列表
        self.text = srace["txt"]  # 描述文本


class RaceScreening:
    def __init__(self, adaptation: str, include_summer_v=True):
        replaces = {"芝": "草", "ダ": "泥", "マ": "英", "長": "长"}
        known_types_dist = "短英中长"
        known_types_site = "草泥"

        self.include_summer_v = include_summer_v  # 包含夏合宿期间的比赛
        self.adaptation_str = adaptation  # 适性str
        self.adaptation_dist = []  # 距离适性
        self.adaptation_site = []  # 场地适性
        for i in adaptation:
            if i in replaces:
                self.adaptation_str = self.adaptation_str.replace(i, replaces[i])

            if i not in known_types_dist and i not in known_types_site:
                self.adaptation_str = self.adaptation_str.replace(i, "")

        self.adaptation_str = "".join(list(set(self.adaptation_str)))

        for i in self.adaptation_str:
            if i in known_types_dist:
                self.adaptation_dist.append(i)
            elif i in known_types_site:
                self.adaptation_site.append(i)

        # print(self.adaptation_str, self.adaptation_dist, self.adaptation_site)

    def race_get(self, is_screening=True) -> List[List[List[List[m.UmaRace]]]]:
        """
        获取所有能跑的比赛
        """
        with open(f"{spath}/data_ex/race_table.json", "r", encoding="utf8") as f:
            data = json.load(f)
        ret = [[[[] for _ in range(2)] for _ in range(12)] for _ in range(3)]

        for year in range(len(data)):
            for month in range(len(data[year])):
                for month_time in range(len(data[year][month])):
                    for race in data[year][month][month_time]:
                        if self.include_summer_v:  # 夏合宿
                            if month in [6, 7]:
                                continue

                        if is_screening:
                            race_data = m.UmaRace(**race)
                            if race_data.distence_str in self.adaptation_dist and \
                                    race_data.place_type in self.adaptation_site:
                                ret[year][month][month_time].append(race_data)
                        else:
                            ret[year][month][month_time].append(m.UmaRace(**race))
        return ret


class RaceCalc(RaceScreening):
    def __init__(self, adaptation, include_summer_v=True):
        super().__init__(adaptation, include_summer_v)
        with open(f"{spath}/data_ex/titleDatas.json", "r", encoding="utf8") as f:
            data = json.load(f)
        self.title_data = [TitleData(i) for i in data]  # 事件信息
        self.race_data = self.race_get(is_screening=True)


    def check_race_in(self, race_id: int):  # 检查比赛能不能跑
        data = self.race_data
        for year in range(len(data)):
            for month in range(len(data[year])):
                for month_time in range(len(data[year][month])):
                    for race in data[year][month][month_time]:
                        if race.race_index == race_id:
                            return True
        return False


    def race_ids_calc(self, ids: m.t.List[int]):
        effect_titles = []
        effect_race_ids = []

        for event in self.title_data:
            is_effect = True
            cache_race_ids = []
            for race_id in event.races:
                if race_id in ids:
                    cache_race_ids.append(race_id)
                    continue
                else:
                    is_effect = False
                    break
            if is_effect:
                effect_titles.append(event)
                cache_race_ids += effect_race_ids

        return effect_titles, list(set(effect_race_ids))

    @staticmethod
    def titles_score_calc(titles: m.t.List[TitleData]):
        total_score = 0
        for i in titles:
            total_score += i.get_effect_value
        return total_score


    def calc(self):
        for event in self.title_data:
            for race_id in event.races:
                ...
