import random
import numpy as np
from . import get_data
from . import exceptions
from PIL import Image, ImageFont, ImageDraw
import os
from . import models as m
from .data_query import DataQuery
from . import img_table
import matplotlib.colors as mcl
from io import BytesIO
from . import static as stt
import umamusume_skill_parser as usp
from . import exceptions as err
import colorsys

spath = os.path.split(__file__)[0]
q = DataQuery()


class SkillDrawer:
    def __init__(self, skill_name=None, skill_data: m.t.Optional[m.UraraDbSkills] = None, current_jp=False):
        super().__init__()
        if skill_data is not None:
            self.skill = skill_data
        elif skill_name is None:
            raise NameError("skill_name 和 skill_data 至少填写一个参数")
        else:
            self.skill = q.search_skill(skill_name) if not current_jp else q.get_skill_from_umadb(skill_name)
            if self.skill is None:
                raise err.SkillNotFound(f"没有找到技能: {skill_name}")

    def draw_skill_icon(self, is_trans=False):
        """
        :param is_trans: 是否翻译
        """
        icon_id = self.skill.icon_id
        content = self.skill.name
        rarity = self.skill.rarity
        if rarity in [5, 4, 3]:
            skill_rare = 2  # 0-普通, 1-金色, 2-固有
        elif rarity == 2:
            skill_rare = 1
        else:
            skill_rare = 0

        if is_trans:
            content = get_data.get_trans(content)
        font = ImageFont.truetype(f"{spath}/src/fonts/msyh.ttc", size=32)
        pt = Image.open(f"{spath}/src/bg/skill_bg_{skill_rare}.png")
        im = Image.open(f"./pretty-derby/public/img/skill_icons/{icon_id}.png")

        Generator.paste_image(pt, im, 21, 12, 55, 55)
        draw = ImageDraw.Draw(pt)
        draw.text(xy=(91, 18), text=Generator.text_width_limit(content, font, 300), fill=(0, 0, 0), font=font)

        return pt

    @staticmethod
    def get_effect(sa: m.t.List[m.SkillsAbility]):
        if (not sa) or (sa is None):
            return "-"
        ret = ""
        for abality in sa:
            ret += f"\n{stt.skillType[abality.type]} {abality.value / 10000}"
        return ret[1:]

    def generate_skill_table(self, save, effect: str, conditions: str, keep: str, cooling: str, score: int, price: int,
                             conditions2=None, effect2=None, newline=18):
        def split_newline(content: str, nl: int):
            sections = []
            while len(content) > nl:
                ct = content[:nl]
                content = content[nl:]
                sections.append(ct)
            if content != "":
                sections.append(content)
            ret = ""
            for i in sections:
                ret += f"\n{i}"
            return ret[1:]

        if price != 0:
            perf = score / price
        else:
            perf = -1

        description = get_data.get_trans(self.skill.describe)
        # skill_name = get_data.get_skill_trans(self.skill.name)

        if conditions2 is not None and effect2 is not None:
            dat = [["技能描述", split_newline(description, newline).replace("・", "·")],
                   ["触发条件", split_newline(conditions, newline)],
                   ["技能效果", effect], ["触发条件2", split_newline(conditions2, newline)],
                   ["技能效果2", effect2], ["持续时间", keep], ["技能冷却", cooling],
                   ["评分/价格", f"{score} / {price if price != 0 else '-'}{f' = {perf}' if perf != -1 else ''}"]]
        else:
            dat = [["技能描述", split_newline(description, newline).replace("・", "·")],
                   ["触发条件", split_newline(conditions, newline)],
                   ["技能效果", effect], ["持续时间", keep], ["技能冷却", cooling],
                   ["评分/价格", f"{score} / {price if price != 0 else '-'}{f' = {perf}' if perf != -1 else ''}"]]
        b = mcl.to_rgba("white", 0)

        tb = img_table.DrawTable(dat, auto_set_column_width=1, colLabels=["技能名", "skill_name"], loc='center',
                                 cellLoc='center', colColours=[b] * len(dat[0]),
                                 cellColours=[[b] * len(dat[0])] * len(dat), font_size=18)
        # tb.add_cells(xys=[(-2, 0), (-2, 1)], text="", position="T")
        # tb.add_cells(xys=[(-1, 0), (-1, 1)], text="", position="B")
        # tb.add_cells(xys=[(0, 0), (0, 1)], text="", position="T")
        tb.add_cells(xys=[(-1, 0), (0, 0)], text="\n技能名", position="L", font_size=18)
        tb.add_cells(xys=[(-1, 1), (0, 1)], text="", position="none", facecolor=[1, 0, 0.5, 0.5], edgecolor="black")
        tb.save_image(save)

    def redraw_table_title(self, img: BytesIO):
        im = Image.open(img)
        w, h = im.size

        data = im.load()
        im_arr = np.asarray(im).astype("float")
        m_h = h / 4  # 只用判断上半部分

        img_point = {"x_min": w + 1, "x_max": -1, "y_min": int(m_h) + 1, "y_max": -1}

        for x in range(w):
            for y in range(h):
                if y >= m_h:
                    break
                r, g, b, a = data[x, y]
                if 100 < a < 180 and r > 200:
                    if x < img_point["x_min"]:
                        img_point["x_min"] = x
                    if x > img_point["x_max"]:
                        img_point["x_max"] = x
                    if y < img_point["y_min"]:
                        img_point["y_min"] = y
                    if y > img_point["y_max"]:
                        img_point["y_max"] = y

        top, bottom, right, left = img_point["y_min"], img_point["y_max"], img_point["x_max"], img_point["x_min"]

        _color = np.array([0, 0, 0, 0])
        for _x in range(left, right):
            for _y in range(top, bottom):
                # im.putpixel((_x + 1, _y + 1), (0, 0, 0, 0))  # 透明底色
                im_arr[_y + 1, _x + 1, 3] = 0
        im = Image.fromarray(np.uint8(im_arr))

        # 重画skill标题
        im_skill_h, im_skill_w = bottom - top, right - left
        im_skill = Image.new("RGBA", (im_skill_w, im_skill_h))
        draw = ImageDraw.Draw(im_skill)
        skill_name = get_data.get_skill_trans(self.skill.name)
        skill_name = f"{self.skill.name}\n{skill_name}" if self.skill.name != skill_name else f"{skill_name}\n-"

        icon_width = 250  # 技能图标宽度
        font = ImageFont.truetype(f"{spath}/src/fonts/msyh.ttc", size=115)
        t_w, t_h = Generator.get_font_size_s(font, skill_name, spacing=0.1)
        spacing = 20  # 图标和文本的间距
        full_w = icon_width + spacing + t_w

        # while full_w > im_skill_w:
        #     icon_width -= 1  # 技能图标宽度
        #     font = ImageFont.truetype(f"{spath}/src/fonts/msyh.ttc", size=icon_width - 10)
        #     t_w, t_h = font.getsize(skill_name)
        #     full_w = icon_width + 6 + t_w

        try:
            im_icon = Image.open(f"./pretty-derby/public/img/skill_icons/{self.skill.icon_id}.png")
        except BaseException as e:
            print(e)
            im_icon = Image.open(f"{spath}/src/icon_not_found.jpg")

        start_x = int((im_skill_w - full_w) / 2) - 20
        start_y = int((im_skill_h - icon_width) / 2)
        font_start_y = int((im_skill_h - t_h) / 2)
        Generator.paste_image(im_skill, im_icon, start_x, start_y, icon_width, icon_width)  # 图标
        draw.text(xy=(start_x + icon_width + spacing, font_start_y + 10), text=skill_name, fill="black", font=font)

        Generator.paste_image(im, im_skill, left, top)
        re_w = 600
        re_h = int(re_w * h / w)
        im = im.resize((re_w, re_h), Image.ANTIALIAS)
        return im

    def generate_skill_table_full(self):
        skill = self.skill
        sp = usp.UmaSkillCodeParser("cn")
        effect = self.get_effect(skill.ability)
        # _trans1 = get_data.get_trans(skill.condition)
        _trans1 = skill.condition
        conditions = sp.get_nature_lang(skill.condition) if _trans1 == skill.condition else _trans1
        keep = f"{skill.ability_time / 10000}s * 赛道长度 / 1000" if skill.ability_time != -1 else "-"
        cooling = f"{skill.cooldown / 10000}s * 赛道长度 / 1000" if skill.cooldown != 0 else "-"
        score = skill.grade_value
        price = skill.need_skill_point
        if (skill.condition2 is not None and skill.condition2 != "") and skill.ability2 is not None:
            effect2 = self.get_effect(skill.ability2)
            # _trans2 = get_data.get_trans(skill.condition2)
            _trans2 = skill.condition2
            conditions2 = sp.get_nature_lang(skill.condition2) if _trans2 == skill.condition2 else _trans2
            conditions2 = conditions2.replace("或", "或\n")
        else:
            effect2 = conditions2 = None

        conditions = conditions.replace("或", "或\n")

        im_table = BytesIO()  # 技能表格
        self.generate_skill_table(im_table, effect, conditions, keep, cooling, score, price, conditions2, effect2)
        return self.redraw_table_title(im_table)

    def generate_skill_image(self, is_full: bool):
        """
        生成技能信息
        :param is_full: False - 仅表格, True - 全图
        :return:
        """
        im_part_table = self.generate_skill_table_full()  # 表格部分
        if not is_full:
            return im_part_table

        im_part_table = Generator.image_zoom(im_part_table, zoom_w=1138)
        im_w, im_h = im_part_table.size

        char_list = q.get_char_list_from_skill(self.skill.id)
        support_card_list = q.get_support_card_from_skill(self.skill.id)

        char_count = len(char_list)
        support_card_count = len(support_card_list)
        char_line = char_count / 8
        char_line = int(char_line) if char_line % 2 == 0 else int(char_line) + 1
        card_line = support_card_count / 8
        card_line = int(card_line) if card_line % 2 == 0 else int(card_line) + 1

        pt_height = 30 + im_h + 80 + 142 * char_line + 96 + 182 * card_line + 40  # 计算整图高度

        pt = Image.new("RGBA", (1200, pt_height), (234, 247, 233))
        draw = ImageDraw.Draw(pt)

        Generator.paste_image(pt, im_part_table, 30, 32)  # 表格

        pos_y_char_start = 30 + im_h + 34
        draw.rectangle(xy=((30, pos_y_char_start), (40, pos_y_char_start + 40)), fill=(155, 20, 157))  # 色块

        font = ImageFont.truetype(f"{spath}/src/fonts/msyh.ttc", size=38)
        draw.text(xy=(48, pos_y_char_start - 8), text="相关角色", fill="black", font=font)

        x_p = y_p = 0
        for char in char_list:  # 角色头图
            im_path = char.imgUrl.split("/")
            if os.path.isfile(f"{spath}/src/chara_card/{im_path[-1]}"):
                im = Image.open(f"{spath}/src/chara_card/{im_path[-1]}")
            elif os.path.isfile(f"./pretty-derby/public/{char.imgUrl}"):
                im = Image.open(f"./pretty-derby/public/{char.imgUrl}")
            else:
                im = Generator.draw_unknown_img(252, 276, get_data.get_trans(char.name))
            Generator.paste_image(pt, im, 34 + 144 * x_p, pos_y_char_start + 44 + 144 * y_p, 126, 138)
            x_p += 1
            if x_p >= 8:
                x_p = 0
                y_p += 1

        pos_y_support_start = pos_y_char_start + 44 + 144 * char_line + 32

        draw.rectangle(xy=((30, pos_y_support_start), (40, pos_y_support_start + 40)), fill=(36, 157, 20))  # 色块
        draw.text(xy=(48, pos_y_support_start - 8), text="相关支援卡", fill="black", font=font)

        x_p = y_p = 0
        for card in support_card_list:  # 支援卡图
            if os.path.isfile(f"./pretty-derby/public/{card.imgUrl}"):
                im = Image.open(f"./pretty-derby/public/{card.imgUrl}")
            else:
                im = Generator.draw_unknown_img(252, 336, f"{get_data.get_trans(card.charaName)}\n"
                                                          f"{get_data.get_trans(card.name)}")
            Generator.paste_image(pt, im, 34 + 144 * x_p, pos_y_support_start + 60 + 182 * y_p, 126, 170)
            x_p += 1
            if x_p >= 8:
                x_p = 0
                y_p += 1
        # pt.save("skf.png")
        return pt


class Generator:
    def __init__(self, umaname: str):
        # super().__init__()

        self.uma_name, self.card_name, self.alias = get_data.query_alias(umaname)
        if self.uma_name == "":
            raise exceptions.UmaNotFound(f"没有找到叫 {umaname} 的马娘")

    @staticmethod
    def hex_to_rgb(color_hex: str):
        if not color_hex.startswith("#"):
            color_hex = f"#{color_hex}"
        r = int(color_hex[1:3], 16)
        g = int(color_hex[3:5], 16)
        b = int(color_hex[5:7], 16)
        rgb = int(r), int(g), int(b)
        return rgb

    @staticmethod
    def get_max_height_per_line(imgs, count_per_line=2):
        lines = []
        line = []
        ret = []
        count = 0
        for im in imgs:
            count += 1
            im_w, im_h = im.size
            if count > count_per_line:
                lines.append(line)
                line = []
                count = 1
            line.append(im_h)
        lines.append(line)
        print(lines)
        for group in lines:
            ret.append(max(group))
        return ret

    @staticmethod
    def paste_image(pt, im, x, y, w=-1, h=-1, with_mask=True):
        w = im.width if w == -1 else w
        h = im.height if h == -1 else h
        im = im.resize((w, h), Image.ANTIALIAS)
        pt.paste(im, (x, y, x + w, y + h), im.convert("RGBA") if with_mask else None)

    @staticmethod
    def draw_text_middle(draw: ImageDraw, xy, text: str, fill, font: ImageFont):
        t_w, t_h = font.getsize(str(text))
        x, y = xy
        d_x = x - t_w / 2
        draw.text(xy=(d_x, y), text=str(text), fill=fill, font=font)

    @staticmethod
    def image_zoom(img: Image, zoom_w=None, zoom_h=None):
        im_w, im_h = img.size
        if zoom_w is not None:
            zoom_h = int(zoom_w * im_h / im_w)
            return img.resize((zoom_w, zoom_h), Image.ANTIALIAS)
        elif zoom_h is not None:
            zoom_w = int(im_w * zoom_h / im_h)
            return img.resize((zoom_w, zoom_h), Image.ANTIALIAS)
        else:
            return img

    @staticmethod
    def image_zoom_dec(zoom_w=None, zoom_h=None):
        def inner(func):
            def cll(*args, **kwargs):
                im = func(*args, **kwargs)
                return Generator.image_zoom(im, zoom_w=zoom_w, zoom_h=zoom_h)

            return cll

        return inner

    @staticmethod
    def text_width_limit(text: str, font, max_width: int):
        t_w, t_h = font.getsize(str(text))
        lm_text = text
        if t_w > max_width:
            while t_w > max_width:
                lm_text = lm_text[:-1]
                t_w, t_h = font.getsize(str(lm_text))
            lm_text = lm_text[:-1] + "..."
        return lm_text

    @staticmethod
    def get_font_size_s(font, text: str, spacing=0.1):
        """
        解决换行符问题
        :param font: 字体
        :param text: 文本
        :param spacing: 行距倍率(int - 固定值, float - 倍率)
        :return:
        """
        if "\n" in text:
            sp_text = text.split("\n")
            max_w = 0
            total_h = 0
            for t in sp_text:
                t_w, t_h = font.getsize(t)
                max_w = max(max_w, t_w)
                total_h += t_h + int(t_h * spacing) if type(spacing) == float else spacing
            return max_w, total_h
        else:
            return font.getsize(text)

    @staticmethod
    def _draw_skill_icon(icon_id, content: str, skill_rare: int, with_trans=False, only_trans=False):
        """
        技能图标(废弃)
        :param icon_id: 技能id
        :param content: 描述文本(日语)
        :param skill_rare: 技能稀有度, 0-普通, 1-金色, 2-固有
        :param with_trans: 是否带翻译
        :param only_trans: 是否仅翻译
        """
        font = ImageFont.truetype(f"{spath}/src/fonts/msyh.ttc", size=16)
        draw_text = content
        trans = get_data.get_trans(draw_text)
        if trans != draw_text:
            if only_trans:
                draw_text = trans
            elif with_trans:
                draw_text = f"{draw_text} ({trans})"

        t_w, t_h = font.getsize(draw_text)
        pt = Image.open(f"{spath}/src/bg/skill_bg_{skill_rare}.png")
        pt = pt.resize((t_w + 55, 35), Image.ANTIALIAS)
        im = Image.open(f"./pretty-derby/public/img/skill_icons/{icon_id}.png")
        icon_x = int(round((t_w + 51) * 0.06))
        Generator.paste_image(pt, im, icon_x, 5, 24, 24)
        draw = ImageDraw.Draw(pt)
        draw.text(xy=(icon_x + 24 + 7, 6), text=draw_text, fill=(0, 0, 0), font=font)
        return pt

    @staticmethod
    def draw_unknown_img(w: int, h: int, text: str, base_size=50, fill="black"):
        pt = Image.new("RGBA", (w, h), (255, 255, 255))
        base_size = base_size

        font = ImageFont.truetype(f"{spath}/src/fonts/msyh.ttc", size=base_size)
        t_w, t_h = Generator.get_font_size_s(font, text)

        while t_w > w or t_h > h:
            base_size -= 1
            font = ImageFont.truetype(f"{spath}/src/fonts/msyh.ttc", size=base_size)
            t_w, t_h = Generator.get_font_size_s(font, text)

        draw_x = int((w - t_w) / 2)
        draw_y = int((h - t_h) / 2)
        draw = ImageDraw.Draw(pt)
        draw.text(xy=(draw_x, draw_y), text=text, fill=fill, font=font)
        return pt

    @staticmethod
    def _func_zoom(func, *args, zoom_w=None, zoom_h=None, **kwargs):
        return Generator.image_zoom(func(*args, **kwargs), zoom_w=zoom_w, zoom_h=zoom_h)

    def draw_char_suit_table(self, char_db: m.UraraDbPlayer):
        pt = Image.open(f"{spath}/src/bg/char_suit_bg.png")
        pt = pt.resize((711, 122), Image.ANTIALIAS)

        pack_data = [[char_db.grass, char_db.dirt],
                     [char_db.shortDistance, char_db.mile, char_db.mediumDistance, char_db.longDistance],
                     [char_db.tracking, char_db.insert, char_db.leading, char_db.escape]]

        p_y = 0
        for i in pack_data:
            p_x = 0
            for v in i:
                im = Image.open(f"{spath}/src/alpha/{v.lower()}.png")
                self.paste_image(pt, im, 255 + 139 * p_x, 10 + 40 * p_y, 22, 22)
                p_x += 1
            p_y += 1
        return pt

    @staticmethod
    def generate_event_table(event: m.t.Optional[m.UraraDbEvents] = None, name=None):
        """
        生成事件分支表格
        """
        if event is None:
            event = q.get_event_from_name(name)
            if event is None:
                raise exceptions.EventNotFound(f"事件 {name} 未找到")

        dat = []
        for choice in event.choiceList:
            if len(choice) < 2:
                print(choice)
                continue
            title, effects = choice
            effect_str = ""
            for _eff in effects:
                effect_str += f"\n{get_data.get_trans(_eff)}"
            effect_str = effect_str[1:]
            title_trans = get_data.get_trans(title)
            title = title if title_trans == title else f"{title}\n{title_trans}"
            dat.append([title, effect_str])

        b = mcl.to_rgba("white", 0)
        tb = img_table.DrawTable(dat, auto_set_column_width=[0, 1], colLabels=["分支", "效果"], loc='center',
                                 cellLoc='center', colColours=[b] * len(dat[0]),
                                 cellColours=[[b] * len(dat[0])] * len(dat), font_size=18)
        _event_trans = get_data.get_trans(event.name)
        _event_trans = event.name if _event_trans == event.name else f"{event.name}\n{_event_trans}"

        # tb.add_cells(xys=[(-1, 0), (-1, 1)], text="", position="T", font_size=18)
        # tb.add_cells(xys=[(-1, 1), (0, 1)], text="", position="none", facecolor=[1, 0, 0.5, 0.5], edgecolor="black")
        im = BytesIO()
        tb.save_image(im)
        im = Image.open(im)
        pt = Image.new("RGBA", (im.width, im.height + 200), (255, 255, 255, 0))
        draw = ImageDraw.Draw(pt)
        Generator.paste_image(pt, im, 0, 200)

        count = 0
        im_data = im.load()
        start_search = 20
        for x in range(im.width):
            r, g, b, a = im_data[x, start_search]
            if a != 0:
                count += 1
                if count > 20:
                    count = 5
                    break
            else:
                break

        draw.rectangle(xy=((0, 0), (im.width, 200)), outline="black", width=count)

        font = ImageFont.truetype(f"{spath}/src/fonts/msyh.ttc", size=115)
        t_w, t_h = font.getsize(event.name)
        draw.text(xy=(int((im.width - t_w) / 2), int((200 - t_h) / 2) - 10), text=event.name, fill="black", font=font)
        return pt  # TODO 事件技能

    def draw_char_attr_table(self, char_db: m.UraraDbPlayer):
        card_id = char_db.db_id
        data = q.get_char_card_attr(card_id)

        pt = Image.open(f"{spath}/src/bg/char_attr_bg.png")
        pt = pt.resize((709, 209), Image.ANTIALIAS)

        draw = ImageDraw.Draw(pt)
        font = ImageFont.truetype(f"{spath}/src/fonts/msyh.ttc", size=18)

        p_y = 0
        for level in data:
            rarity, speed, stamina, power, guts, wiz = level
            pack_data = [speed, stamina, power, guts, wiz]
            p_x = 0
            for pd in pack_data:
                self.draw_text_middle(draw, xy=(177 + 118 * p_x, 52 + 41 * p_y), text=pd, fill=(0, 0, 0), font=font)
                p_x += 1
            p_y += 1

        pack_data = [char_db.speedGrow, char_db.staminaGrow, char_db.powerGrow, char_db.gutsGrow, char_db.wisdomGrow]
        p_x = 0
        for level in pack_data:
            self.draw_text_middle(draw, xy=(177 + 118 * p_x, 52 + 41 * p_y), text=level, fill=(0, 0, 0), font=font)
            p_x += 1
        return pt

    @staticmethod
    def get_image_src(path1: str, path2=None, filename=""):
        if os.path.isfile(f"{path1}{filename}"):
            return Image.open(f"{path1}{filename}")
        elif path2 is not None and os.path.isfile(f"{path2}{filename}"):
            return Image.open(f"{path2}{filename}")
        else:
            return None

    @staticmethod
    def _rgb_color_set_saturation(rgb, saturation=0.55, brightness=0.9):
        r, g, b = rgb
        h, s, v = colorsys.rgb_to_hsv(r, g, b)
        return tuple([int(i) for i in colorsys.hsv_to_rgb(h, saturation, 255 * brightness)])

    def get_uma_info(self, use_cache=True):
        img_interval = 20  # 图片纵向间距
        card = q.get_char_card(self.card_name)
        _save_card_name = card.name.replace('/', '_').replace('\\', '_')
        _save_char_name = card.charaName.replace('/', '_').replace('\\', '_')
        save_name = f"{spath}/cache/{_save_card_name}({_save_char_name}).jpg"
        if use_cache:
            if os.path.isfile(save_name):
                return save_name

        char_id = q.card_id_to_char_id(card.db_id)
        birth_year, birth_month, birth_day, ui_color_main, ui_color_sub, scale = q.get_char_baseinfo(char_id)

        suit_table = self.draw_char_suit_table(card)  # 适性表
        # suit_table.save("test.png")
        char_table = self.draw_char_attr_table(card)  # 属性表
        # char_table.save("test.png")
        uma_info = q.get_char_detail_info(char_id)

        # threads_skill = tdt.ThreadTasks()
        skill_imgs = []
        for skill_id in card.skillList:
            skill = q.get_skill_from_id(skill_id)
            if skill is not None:
                _dw = SkillDrawer(skill_data=skill)
                # threads_skill.add_thread(self._func_zoom, _dw.generate_skill_image, True, zoom_w=523)
                g_img = self._func_zoom(_dw.generate_skill_image, False, zoom_w=523)
                skill_imgs.append(g_img)
        # skill_imgs = threads_skill.get_results(30)  # 技能表
        if skill_imgs:
            skill_lines_height = self.get_max_height_per_line(skill_imgs, 2)
        else:
            skill_lines_height = [0]
        skill_images_total_height = sum(skill_lines_height) + len(skill_lines_height) * img_interval

        hide_event_imgs = []
        if card.hideEvent:
            # threads_hide_event = tdt.ThreadTasks()
            for event_id in card.hideEvent:
                event = q.get_event_from_id(event_id)
                if event is not None:
                    # threads_hide_event.add_thread(self._func_zoom, self.generate_event_table, event=event, zoom_w=523)
                    g_img = self._func_zoom(self.generate_event_table, event=event, zoom_w=523)
                    hide_event_imgs.append(g_img)
            # hide_event_imgs = threads_hide_event.get_results(30)  # 隐藏事件表
        else:
            hide_event_imgs = []
        if hide_event_imgs:
            hide_event_lines_height = self.get_max_height_per_line(hide_event_imgs, 2)
        else:
            hide_event_lines_height = [0]
        hide_event_lines_total_height = sum(hide_event_lines_height) + len(hide_event_lines_height) * img_interval

        # 属性表格底部 + 底部~技能标题头部 + 技能标题头部~技能表格头部 + 技能总高 + 技能表底~隐藏事件头 + 隐藏事件头~事件表格头 + 表格总
        pt_height = 838 + 30 + 55 + skill_images_total_height + 30 + 55 + hide_event_lines_total_height
        bg_rgb = self._rgb_color_set_saturation(self.hex_to_rgb(ui_color_sub))
        pt = Image.new("RGBA", (1200, pt_height), bg_rgb)
        draw = ImageDraw.Draw(pt)

        im = Image.open(f"{spath}/src/bg/char_top_bg.png")  # 白色半透明背景
        Generator.paste_image(pt, im, 32, 18, 1136, 203)
        im = Image.open(f"{spath}/src/bg/char_top_bg_rectangle.png")
        Generator.paste_image(pt, im, 32, 221, 1136, pt_height - 221 - 18)

        im = self.get_image_src(f"{spath}/src/chara_card/", "./pretty-derby/public/img/chara_card/",
                                card.imgUrl.split("/")[-1])
        if im is not None:
            Generator.paste_image(pt, im, 62, 18, 184, 202)  # 头像

        if os.path.isfile(f"{spath}/src/chara_full/{card.imgUrl.split('/')[-1]}"):
            im = Image.open(f"{spath}/src/chara_full/{card.imgUrl.split('/')[-1]}")
            Generator.paste_image(pt, im, 769, 40, 432, 760)  # 立绘

        font = ImageFont.truetype(f"{spath}/src/fonts/msyh.ttc", size=35)
        name_trans = get_data.get_trans(card.charaName)
        draw.text(xy=(274, 59),
                  text=f"{card.charaName if name_trans == card.charaName else f'{card.charaName} ({name_trans})'}",
                  fill="black", font=font)  # 名字

        font = ImageFont.truetype(f"{spath}/src/fonts/msyh.ttc", size=30)
        draw.text(xy=(274, 115), text=f"{card.name}", fill="black", font=font)  # 卡名
        draw.text(xy=(274, 170), text=f"CV. {uma_info.cv}", fill="black", font=font)  # cv

        font = ImageFont.truetype(f"{spath}/src/fonts/msyh.ttc", size=25)
        uinfo_text = f"{uma_info.class_} · {uma_info.dorm}   生日: {birth_year} 年 {birth_month} 月 {birth_day} 日   " \
                     f"身高: {uma_info.height}\n"
        uma_measurements = "" if uma_info.measurements is None else f"三围: {uma_info.measurements}   "
        uinfo_text = f"{uinfo_text}{uma_measurements}体重: {uma_info.weight}\n" \
                     f"鞋码: {uma_info.shoe_size}"
        draw.text(xy=(80, 245), text=f"{uinfo_text}", fill="black", font=font)  # 角色信息

        font = ImageFont.truetype(f"{spath}/src/fonts/msyh.ttc", size=35)

        draw.rectangle(xy=((64, 364), (74, 402)), fill=(110, 208, 245))
        draw.text(xy=(81, 357), text="适性", fill="black", font=font)
        Generator.paste_image(pt, suit_table, 64, 420, 712, 122)  # 适性表

        draw.rectangle(xy=((64, 576), (74, 614)), fill=(155, 20, 157))
        draw.text(xy=(81, 569), text="属性", fill="black", font=font)
        Generator.paste_image(pt, char_table, 64, 629, 712, 209)  # 属性表

        draw.rectangle(xy=((64, 868), (74, 906)), fill=(238, 72, 99))
        draw.text(xy=(81, 861), text="技能", fill="black", font=font)  # 技能列表

        p_x = p_y = 0
        now_y = 923
        for skill_img in skill_imgs:
            try:
                p_y_value = skill_lines_height[p_y]
            except IndexError:
                print("IndexError: 角色 - 技能 in image_generate on line 665")
                p_y_value = img_interval + 265

            Generator.paste_image(pt, skill_img, 64 + 558 * p_x, now_y)  # 技能图片

            p_x += 1
            if p_x >= 2:
                now_y += p_y_value + img_interval
                p_y += 1
                p_x = 0

        hide_event_img_start = pt_height - hide_event_lines_total_height
        hide_event_head_start = pt_height - hide_event_lines_total_height - 55

        draw.rectangle(xy=((64, hide_event_head_start), (74, hide_event_head_start + 38)), fill=(238, 224, 72))

        p_x = p_y = 0
        now_y = hide_event_img_start
        if card.hideEvent:
            draw.text(xy=(81, hide_event_head_start - 7), text="隐藏事件", fill="black", font=font)  # 隐藏事件
            for hide_event_img in hide_event_imgs:
                try:
                    p_y_value = hide_event_lines_height[p_y]
                except IndexError:
                    print("IndexError: 角色 - 隐藏事件 in image_generate on line 688")
                    p_y_value = img_interval + 200
                Generator.paste_image(pt, hide_event_img, 64 + 558 * p_x, now_y)

                p_x += 1
                if p_x >= 2:
                    now_y += p_y_value + img_interval
                    p_y += 1
                    p_x = 0
        else:
            draw.text(xy=(81, hide_event_head_start - 7), text="隐藏事件 - (无)", fill="black", font=font)

        pt = pt.convert("RGB")
        pt.save(save_name, quality=90)
        return save_name


class Gacha(DataQuery):
    @staticmethod
    def _generate_gacha_result(p_r=790, p_sr=180, p_ssr=30, count=10):
        total = p_r + p_sr + p_ssr
        rare_types = ["-", "r", "sr", "ssr"]
        data_result = []
        ret = []
        for i in range(count):
            rand = random.randint(1, total)
            if rand <= p_r:
                data_result.append(1)
            elif p_r < rand <= p_r + p_sr:
                data_result.append(2)
            else:
                print(rand)
                data_result.append(3)
        data_result = sorted(data_result, reverse=True)
        for i in data_result:
            ret.append(rare_types[i])
        return ret

    def get_uma_rare_data(self):
        umas = self.umadb.players
        cards_rare = {"r": [], "sr": [], "ssr": [], "-": []}
        rare_types = ["-", "r", "sr", "ssr"]
        for uma in umas:
            if uma.default_rarity > 3:
                continue
            cards_rare[rare_types[uma.default_rarity]].append(uma)
        return cards_rare

    def get_card_rare_data(self):
        cards = self.umadb.supports
        cards_rare = {"r": [], "sr": [], "ssr": []}
        for card in cards:
            if card.rare.lower() in cards_rare:
                cards_rare[card.rare.lower()].append(card)
        return cards_rare

    def generate_gacha_uma_result(self, count=10) -> m.t.List[m.UraraDbPlayer]:
        gacha_result_r = self._generate_gacha_result(count=count)
        uma_rare = self.get_uma_rare_data()
        gacha_result: m.t.List[m.UraraDbPlayer] = []
        for i in gacha_result_r:
            rand = random.randint(0, len(uma_rare[i]) - 1)
            gacha_result.append(uma_rare[i][rand])
        return gacha_result

    def generate_gacha_card_result(self, count=10) -> m.t.List[m.UraraDbSupport]:
        gacha_result_r = self._generate_gacha_result(count=count)
        card_rare = self.get_card_rare_data()
        gacha_result: m.t.List[m.UraraDbSupport] = []
        for i in gacha_result_r:
            rand = random.randint(0, len(card_rare[i]) - 1)
            gacha_result.append(card_rare[i][rand])
        return gacha_result

    def generate_image_uma(self, cs, count=10):
        """
        马娘十连
        :param cs: 扣除前cs点
        :param count: 10
        :return: 图片路径
        """
        uma_result = self.generate_gacha_uma_result(count=count)

        base_position = [[89, 221], [345, 221], [611, 221], [193, 480], [490, 480], [89, 221 + 518], [345, 221 + 518],
                         [611, 221 + 518], [193, 480 + 518], [490, 480 + 518]]  # y+259*2
        pt = Image.open(f"{spath}/src/gacha/bg/uma_back.png")

        for i in range(len(uma_result)):
            b_x = base_position[i][0]
            b_y = base_position[i][1]
            imgt = Generator.get_image_src(f"{spath}/src/chara_card/", "./pretty-derby/public/img/chara_card/",
                                           uma_result[i].imgUrl.split("/")[-1])
            if imgt is None:
                continue
            Generator.paste_image(pt, imgt, b_x, b_y, 200, 219)
            if uma_result[i].default_rarity == 3:
                imgt = Image.open(f"{spath}/src/gacha/角色卡彩框.png")
                Generator.paste_image(pt, imgt, b_x, b_y)
            imgt = Image.open(f"{spath}/src/gacha/stars/{uma_result[i].default_rarity}.png").resize((136, 36))
            Generator.paste_image(pt, imgt, b_x + 31, b_y + 204)

        draw = ImageDraw.Draw(pt)
        font = ImageFont.truetype(font=f"{spath}/src/fonts/MILanProVF-Medium.ttf", size=25)
        draw.text(xy=(620, 1277), text=str(int(cs) - 5), fill=(122, 61, 14), font=font)  # 扣除后cs点
        t_w, t_h = font.getsize(str(cs))
        draw.text(xy=(568 - t_w, 1277), text=str(cs), fill=(122, 61, 14), font=font)  # 扣除前cs点

        rdname = f"{random.randint(100000, 999999)}.jpg"
        pt = pt.convert('RGB')
        pt.save(f"{spath}/temp/{rdname}", quality=90)
        return f"{spath}/temp/{rdname}"

    def generate_image_card(self, cs, count=10):
        """
        支援卡十连
        :param cs: 扣除前cs点
        :param count: 10
        :return: 图片路径
        """
        card_result = self.generate_gacha_card_result(count=count)

        base_position = [[109, 174], [358, 174], [609, 174], [217, 458], [468, 458], [109, 174 + 567], [358, 174 + 567],
                         [609, 174 + 567], [217, 458 + 567], [468, 458 + 567]]  # y+567
        pt = Image.open(f"{spath}/src/gacha/bg/supportcard_back.png")

        for i in range(len(card_result)):
            b_x = base_position[i][0]
            b_y = base_position[i][1]
            imgt = Generator.get_image_src(f"{spath}/src/support_card_with_icon/",
                                           "./pretty-derby/public/img/support_card_with_icon/",
                                           card_result[i].imgUrl.split("/")[-1])
            if imgt is None:
                continue
            Generator.paste_image(pt, imgt, b_x, b_y, 200, 267)

        draw = ImageDraw.Draw(pt)
        font = ImageFont.truetype(font=f"{spath}/src/fonts/MILanProVF-Medium.ttf", size=25)
        draw.text(xy=(622, 1312), text=str(int(cs) - 5), fill=(122, 61, 14), font=font)  # 扣除后cs点
        t_w, t_h = font.getsize(str(cs))
        draw.text(xy=(570 - t_w, 1312), text=str(cs), fill=(122, 61, 14), font=font)  # 扣除前cs点

        rdname = f"{random.randint(100000, 999999)}.jpg"
        pt = pt.convert('RGB')
        pt.save(f"{spath}/temp/{rdname}", quality=90)
        return f"{spath}/temp/{rdname}"

    def generate_image_uma_well(self, count=200):
        """
        马娘井
        :param count: 200
        :return: 图片路径
        """
        uma_result = self.generate_gacha_uma_result(count=count)

        line_count = int(count / 10)
        line_count += 1 if count % 10 != 0 else 0
        pt = Image.new("RGBA", (1005, 100 * line_count + 5), (255, 255, 255))

        p_x = p_y = 0
        for i in range(count):
            imgt = Generator.get_image_src(f"{spath}/src/chara_card/",
                                           "./pretty-derby/public/img/chara_card/",
                                           uma_result[i].imgUrl.split("/")[-1])
            if imgt is None:
                continue
            Generator.paste_image(pt, imgt, 5 + 100 * p_x, 5 + 100 * p_y, 95, 95)
            if uma_result[i].default_rarity == 3:
                imgt = Image.open(f"{spath}/src/gacha/角色卡彩框.png")
                Generator.paste_image(pt, imgt, 5 + 100 * p_x, 100 * p_y + 5, 95, 95)

            p_x += 1
            if p_x >= 10:
                p_x = 0
                p_y += 1

        rdname = f"{random.randint(100000, 999999)}.jpg"
        pt.convert('RGB').save(f"{spath}/temp/{rdname}", quality=90)
        return f"{spath}/temp/{rdname}"

    def generate_image_card_well(self, count=200):
        """
        支援卡井
        :param count: 200
        :return: 图片路径
        """
        card_result = self.generate_gacha_card_result(count=count)

        line_count = int(count / 10)
        line_count += 1 if count % 10 != 0 else 0
        pt = Image.new("RGBA", (1520, 200 * line_count + 10), (255, 255, 255))

        p_x = p_y = 0
        for i in range(count):
            imgt = Generator.get_image_src(f"{spath}/src/support_card_with_icon/",
                                           "./pretty-derby/public/img/support_card_with_icon/",
                                           card_result[i].imgUrl.split("/")[-1])
            if imgt is None:
                imgt = Generator.draw_unknown_img(150, 200, f"{card_result[i].rare}\n"
                                                            f"{get_data.get_trans(card_result[i].charaName)}\n"
                                                            f"{card_result[i].name}")
            Generator.paste_image(pt, imgt, 10 + 150 * p_x, 10 + 200 * p_y, 142, 190)
            p_x += 1
            if p_x >= 10:
                p_x = 0
                p_y += 1

        rdname = f"{random.randint(100000, 999999)}.jpg"
        pt.resize((760, 100 * line_count + 5), Image.ANTIALIAS).convert('RGB').save(f"{spath}/temp/{rdname}",
                                                                                    quality=90)
        return f"{spath}/temp/{rdname}"
