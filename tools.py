import json
import math
import sys
from functools import partial
from PyQt5.QtWidgets import QApplication, QWidget, QPlainTextEdit, QPushButton, QLabel, QComboBox, QCheckBox
from umamusume_bot.race_calc import TitleData, RaceCalc


class Test(QWidget):
    def __init__(self):
        super(Test, self).__init__()

        self.run_list = []
        self.dirt_GI_count = 0

        self.MainWidget = QWidget(self)
        self.setFixedSize(1705, 710)

        self.cbox = []
        for _i in range(3):
            _cbox = []
            for _j in range(24):
                cbox = QComboBox(self.MainWidget)
                x = _j % 3
                y = math.floor(_j / 3)
                cbox.setGeometry(x * 180 + 25 + _i * 560, y * 55 + 25, 175, 50)
                _cbox.append(cbox)
                cbox.setStyleSheet('font-family: Microsoft Yahei;'
                                   'font-size: 15px;')
                cbox.currentIndexChanged.connect(partial(self.item_change, _i, _j))
            self.cbox.append(_cbox)

        for _i in range(3):
            for _j in range(12):
                for _k in range(2):
                    for _ in range(len(ret[_i][_j][_k])):
                        self.cbox[_i][_j * 2 + _k].addItem(
                            f'{ret[_i][_j][_k][_].level} '
                            f'{"芝" if ret[_i][_j][_k][_].place_type == "草" else "ダ"} '
                            f'{ret[_i][_j][_k][_].distence}m '
                            f' id{ret[_i][_j][_k][_].race_index}'
                            f'\n{ret[_i][_j][_k][_].name_jp}')
                    self.cbox[_i][_j * 2 + _k].addItem('-')

        self.btn_reset = QPushButton('清空赛程', self.MainWidget)
        self.btn_reset.clicked.connect(self.reset)
        self.btn_reset.setGeometry(25, 650, 100, 30)

        pos = [[0, 0], [0, 1], [1, 0], [1, 1], [1, 2], [1, 3], [2, 0], [2, 1], [2, 2], [2, 3], [3, 0]]
        self.adaptation = []
        _adaptation = ['草', '泥', '短', '英', '中', '长', 'GI', 'GII', 'GIII', 'OP', '夏合宿']
        for _i in range(11):
            checkbox = QCheckBox(_adaptation[_i], self.MainWidget)
            checkbox.setGeometry(25 + pos[_i][1] * 60, 500 + pos[_i][0] * 35, 60, 30)
            self.adaptation.append(checkbox)

        self.adaptation[0].setChecked(True)
        self.adaptation[1].setChecked(True)
        self.adaptation[3].setChecked(True)
        self.adaptation[4].setChecked(True)
        self.adaptation[5].setChecked(True)
        self.adaptation[6].setChecked(True)

        self.btn1 = QPushButton('预筛选', self.MainWidget)
        self.btn1.clicked.connect(self.search)
        self.btn1.setGeometry(135, 650, 100, 30)

        self.btn2 = QPushButton('查询奖励', self.MainWidget)
        self.btn2.clicked.connect(self.check_award)
        self.btn2.setGeometry(245, 650, 100, 30)

        self.msgbox = QPlainTextEdit(self.MainWidget)
        self.msgbox.setGeometry(400, 480, 700, 200)
        self.msgbox.setStyleSheet('font-family: Microsoft Yahei;font-size:15px;')

    def item_change(self, _i, _j):
        color = {"GI": '#3685ec', "GII": '#f95884', "GIII": '#4ecc6b', "OP": '#fdaa20', "Pre-OP": '#fdaa20',
                 "-": 'black'}
        self.cbox[_i][_j].setStyleSheet('font-family: Microsoft Yahei;'
                                        'font-size: 15px;'
                                        f'color:{color[self.cbox[_i][_j].currentText().split()[0]]}')

    def reset(self):
        for _i in range(3):
            for _j in range(24):
                self.cbox[_i][_j].setCurrentIndex(len(self.cbox[_i][_j]) - 1)
        self.check_award()

    def search(self):
        _text = ''
        global ret
        for _i in range(6):
            _adaptation = ['草', '泥', '短', '英', '中', '长']
            if self.adaptation[_i].isChecked():
                _text += _adaptation[_i]
        ret = RaceCalc(_text, False if self.adaptation[10].isChecked() else True).race_get()

        for _i in range(3):
            for _j in range(24):
                self.cbox[_i][_j].currentIndexChanged.disconnect()
                self.cbox[_i][_j].clear()
                self.cbox[_i][_j].currentIndexChanged.connect(partial(self.item_change, _i, _j))

        _label = {"GI": 6, "GII": 7, "GIII": 8, "OP": 9, "Pre-OP": 9}
        for _i in range(3):
            for _j in range(12):
                for _k in range(2):
                    for _ in range(len(ret[_i][_j][_k])):
                        if self.adaptation[_label[ret[_i][_j][_k][_].level]].isChecked():
                            self.cbox[_i][_j * 2 + _k].addItem(
                                f'{ret[_i][_j][_k][_].level} '
                                f'{"芝" if ret[_i][_j][_k][_].place_type == "草" else "ダ"} '
                                f'{ret[_i][_j][_k][_].distence}m '
                                f' id{ret[_i][_j][_k][_].race_index}'
                                f'\n{ret[_i][_j][_k][_].name_jp}')
                    self.cbox[_i][_j * 2 + _k].addItem('-')

    def check_award(self):
        self.msgbox.clear()
        self.run_list = []
        for _i in range(3):
            for _j in range(24):
                if self.cbox[_i][_j].currentText().split()[0] != '-':
                    self.run_list.append(int(self.cbox[_i][_j].currentText().split()[3][2:]))

        fm = [15, 16, 17, 18]
        checked = []
        remain = []
        remain_jp = []
        achieved = 0
        dirt_GI_count = 0
        get_point = 0
        for _i in range(len(title_data)):
            if _i not in fm:
                num = len(title_data[_i].races)
                for _j in range(num):
                    if type(title_data[_i].races[_j]) == int:
                        _ = False
                        if title_data[_i].races[_j] in self.run_list:
                            if title_data[_i].races[_j] not in checked:
                                achieved += 1
                                _ = True
                        checked.append(title_data[_i].races[_j])
                        if not _:
                            remain.append(title_data[_i].races[_j])
                            name, p_t, level = self.check_name(title_data[_i].races[_j])
                            if name not in remain_jp:
                                remain_jp.append(name)
                    else:
                        _ = False
                        for _k in range(len(title_data[_i].races[_j])):
                            if title_data[_i].races[_j][_k] not in checked:
                                if title_data[_i].races[_j][_k] in self.run_list:
                                    achieved += 1
                                    _ = True
                                checked.append(title_data[_i].races[_j][_k])
                            if _:
                                break
                        if not _:
                            __ = []
                            __jp = []
                            for _k in range(len(title_data[_i].races[_j])):
                                __.append(title_data[_i].races[_j][_k])
                                __name, p_t, level = self.check_name(title_data[_i].races[_j][_k])
                                if __name not in __jp:
                                    __jp.append(__name)
                            remain_jp.append(__jp)
                            remain.append(__)

            else:
                for _ in range(len(self.run_list)):
                    x, p_t, level = self.check_name(self.run_list[_])
                    if p_t == '泥' and level == 'GI':
                        dirt_GI_count += 1
                achieved = dirt_GI_count
                remain_jp = ['-']
                if _i == 15:
                    num = 5
                elif _i == 16:
                    num = 4
                elif _i == 17:
                    num = 3
                else:
                    num = 9

            print(f'{achieved}/{num} {title_data[_i].name} {title_data[_i].get_effect}')
            self.msgbox.appendPlainText(f'{achieved}/{num} {title_data[_i].name} {title_data[_i].get_effect}')
            if remain_jp == [] or remain_jp == ['-']:
                pass
            else:
                print(f'未达成的比赛: {remain_jp}')
                self.msgbox.appendPlainText(f'未达成的比赛: {remain_jp}')
            if achieved >= num:
                get_point += title_data[_i].get_effect_value
            checked = []
            remain = []
            remain_jp = []
            achieved = 0
            dirt_GI_count = 0
        self.msgbox.appendPlainText(f'可获得的总点数: {str(get_point)}')
        print(self.run_list)

    def check_name(self, id):
        for _i in range(3):
            for _j in range(12):
                for _k in range(2):
                    for _ in range(len(_ret[_i][_j][_k])):
                        if _ret[_i][_j][_k][_].race_index == id:
                            return _ret[_i][_j][_k][_].name_jp, \
                                   _ret[_i][_j][_k][_].place_type, \
                                   _ret[_i][_j][_k][_].level


if __name__ == '__main__':
    with open("umamusume_bot/data_ex/titleDatas.json", "r", encoding="utf8") as f:
        data = json.load(f)
        title_data = [TitleData(i) for i in data]  # 事件信息
    ret = RaceCalc('草泥中英短长', False).race_get()
    _ret = ret
    app = QApplication(sys.argv)
    # apply_stylesheet(app, theme='dark_teal.xml')
    test = Test()
    test.show()
    sys.exit(app.exec_())
