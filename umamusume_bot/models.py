from pydantic import BaseModel
import typing as t


class UraraDbPlayer(BaseModel):
    name: str
    grass: str
    dirt: str
    shortDistance: str
    mile: str
    mediumDistance: str
    longDistance: str
    escape: str
    leading: str
    insert: str
    tracking: str
    speedGrow: str
    staminaGrow: str
    powerGrow: str
    gutsGrow: str
    wisdomGrow: str
    skillList: t.List[t.Optional[str]]
    eventList: t.List[t.Optional[str]]
    id: str
    rare: str
    raceList: dict
    gwId: str
    uniqueSkillList: t.List[t.Optional[str]]
    initialSkillList: t.List[t.Optional[str]]
    awakeningSkillList: t.List[t.Optional[str]]
    imgUrl: str
    charaName: str
    db_id: int
    default_rarity: int
    hideEvent: t.List[t.Optional[str]]
    eventList0: t.List[t.Optional[str]]
    eventList1: t.List[t.Optional[str]]
    eventList2: t.List[t.Optional[str]]
    eventList3: t.List[t.Optional[str]]
    eventList4: t.List[t.Optional[str]]


class UraraDbSupport(BaseModel):
    class UraraDbSupportEffects(BaseModel):
        id: int
        type: int
        init: int
        limit_lv5: int
        limit_lv10: int
        limit_lv15: int
        limit_lv20: int
        limit_lv25: int
        limit_lv30: int
        limit_lv35: int
        limit_lv40: int
        limit_lv45: int
        limit_lv50: int

    class BaseAbality(BaseModel):
        name: str
        ability: t.List[t.List[t.Union[str, t.List[str]]]]

    class UniqueEffect(BaseModel):
        id: int
        lv: int
        type_0: int
        value_0: int
        value_0_1: int
        value_0_2: int
        value_0_3: int
        value_0_4: int
        type_1: int
        value_1: int
        value_1_1: int
        value_1_2: int
        value_1_3: int
        value_1_4: int

    name: str
    rare: str
    skillList: t.List[t.Optional[str]]
    eventList: t.List[t.Optional[str]]
    id: str
    gwId: str
    imgUrl: str
    trainingEventSkill: t.List[t.Optional[str]]
    possessionSkill: t.List[t.Optional[str]]
    charaName: str
    db_id: int
    effects: t.List[UraraDbSupportEffects]
    rarity: int
    baseAbility: BaseAbality
    unique_effect: t.Optional[UniqueEffect]
    type: str

class SkillsAbility(BaseModel):
    type: int
    value: int
    target_type: int
    target_value: int

class UraraDbSkills(BaseModel):
    name: str
    imgUrl: str
    rare: str
    describe: t.Optional[str]
    id: str
    condition: t.Optional[str]
    rarity: t.Optional[int]
    db_id: t.Optional[int]
    icon_id: t.Optional[int]
    ability_value: t.Optional[int]
    ability_time: t.Optional[int]
    cooldown: t.Optional[int]
    ability: t.Optional[t.List[t.Optional[SkillsAbility]]]
    need_skill_point: t.Optional[int]
    grade_value: t.Optional[int]
    condition2: t.Optional[str]
    ability2: t.Optional[t.List[t.Optional[SkillsAbility]]]


class UraraDbRaces(BaseModel):
    name: str
    date: str
    dateNum: int
    uniqueName: str
    class_: t.Optional[str]
    grade: str
    place: str
    ground: str
    distance: str
    distanceType: str
    direction: str
    side: t.Optional[str]
    id: str

    def __init__(self, **data):
        super().__init__(**data)
        self.class_ = data["class"]


class UraraDbBuffs(BaseModel):
    id: str
    name: str
    describe: str


class UraraDbEvents(BaseModel):
    name: str
    choiceList: t.List[t.List[t.Union[str, t.List[str]]]]
    id: str
    pid: t.Optional[str]
    skills: t.Optional[t.List[str]]

    def __init__(self, **data):
        super().__init__(**data)
        if self.skills is not None:
            self.skills = list(set(self.skills))


class UraraDb(BaseModel):
    players: t.List[UraraDbPlayer]
    supports: t.Optional[t.List[UraraDbSupport]]
    skills: t.List[UraraDbSkills]
    updateTime: int  # ms
    races: t.List[UraraDbRaces]
    buffs: t.List[UraraDbBuffs]
    effects: t.Dict  # "number": {"name": str, "description": str}
    events: t.List[UraraDbEvents]

    def __init__(self, **data):
        supports = data.pop("supports")
        super().__init__(**data)
        _supports = []
        for s in supports:
            try:
                _supports.append(UraraDbSupport(**s))
            except BaseException as e:
                print(e)
                continue
        self.supports = _supports


class UmaDetailInfo:
    def __init__(self, query_data: t.List[t.List], measurements=None, get_measurements=None):
        self.name = None
        self.cv = None
        self.dorm = None  # 宿舍
        self.weight = None
        self.birth = None
        self.height = None
        self.class_ = None
        self.introduce = None
        self.good_at = None
        self.not_good_at = None
        self.about_ear = None
        self.about_tail = None
        self.shoe_size = None
        self.about_family = None
        self.measurements = measurements

        self.id_self = {
            6: "name", 7: "cv", 8: "dorm", 9: "weight", 157: "birth", 158: "height", 162: "class_", 163: "introduce",
            164: "good_at", 165: "not_good_at", 166: "about_ear", 167: "about_tail", 168: "shoe_size",
            169: "about_family"
        }
        self.id_str = {
            6: "名字", 7: "CV", 8: "宿舍区", 9: "体重", 157: "生日", 158: "身高", 162: "年级", 163: "自我介绍", 164: "擅长的事",
            165: "不擅长的事", 166: "关于耳朵", 167: "关于尾巴", 168: "鞋码", 169: "关于家族"
        }

        self.data = query_data
        self.parse_data()
        if get_measurements is not None:
            self.measurements = get_measurements(self.name)


    def parse_data(self):
        id_self = self.id_self
        for data in self.data:
            if data:
                _id, category, text = data
                if int(_id) in id_self:
                    setattr(self, id_self[int(_id)], text)

    def get_text(self, ignore_none=True):
        ret = ""
        for ids in self.id_self:
            text = getattr(self, self.id_self[ids])
            if text is None and ignore_none:
                continue
            ret += f"\n{self.id_str[ids]}: {text}"
        return ret[1:]

    def get_dict(self, ignore_none=False):
        ret = {}
        for ids in self.id_self:
            text = getattr(self, self.id_self[ids])
            if text is None and ignore_none:
                continue
            ret[self.id_str[ids]] = text
        return ret

    def __str__(self):
        return self.get_text()


class UmaRace(BaseModel):
    level: str
    name_jp: str
    name_cn: str
    place: str
    place_type: str
    distence: int
    direction: str
    distence_str: t.Optional[str]
    race_index: t.Optional[int]

    def __init__(self, **data):
        super().__init__(**data)

        if self.distence < 1600:
            self.distence_str = "短"
        elif 1600 <= self.distence <= 1800:
            self.distence_str = "英"
        elif 1800 < self.distence <= 2400:
            self.distence_str = "中"
        else:
            self.distence_str = "长"
