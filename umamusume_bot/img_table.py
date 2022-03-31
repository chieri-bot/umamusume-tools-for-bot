import matplotlib.pyplot as plt


class DrawTable:
    def __init__(self, data, auto_set_font_size=False, auto_set_column_width=None, font_size=None,
                 cell_height_ratio=0.05, **kwargs):
        plt.rcParams['font.sans-serif'] = ["SimHei"]
        plt.rcParams['axes.unicode_minus'] = False  # 显示负号

        self.data = data
        self.fig, self.ax = plt.subplots()
        self.ax.axis('off')
        self.table = self.ax.table(cellText=data, **kwargs)
        cells = self.table.get_celld()

        self.table.auto_set_font_size(auto_set_font_size)
        if font_size is not None:
            self.table.set_fontsize(font_size)

            for i in cells:
                cells[i].set_height(1 / font_size + cell_height_ratio)

        _type_auto_set_column_width = type(auto_set_column_width)
        if _type_auto_set_column_width == str:
            if auto_set_column_width.lower() == "all":
                [self.table.auto_set_column_width(i) for i in range(len(data))]
        elif _type_auto_set_column_width in [list, tuple]:
            for i in auto_set_column_width:
                self.table.auto_set_column_width(i)
        elif _type_auto_set_column_width == int:
            self.table.auto_set_column_width(auto_set_column_width)

        self.h = cells[(0, 0)].get_height()
        self.w = cells[(0, 0)].get_width()
        cells_max_ncount = {}
        for i in cells:
            cell_line, cell_y = i
            _text = cells[i].get_text().get_text()
            _ncount = _text.count("\n")

            if "[cdt:ignore_n=true]" in _text:
                cells[i].get_text().set_text(_text.replace("[cdt:ignore_n=true]", ""))
            else:
                if _ncount > 0:
                    if cell_line not in cells_max_ncount:
                        cells_max_ncount[cell_line] = {"ncount": _ncount, "cell_info": i}
                    elif cells_max_ncount[cell_line]["ncount"] >= _ncount:
                        continue
                    else:
                        # self._change_height(cells, cells[i].get_height() * (_ncount + 1), i[0])
                        cells_max_ncount[cell_line]["ncount"] = _ncount

        for cell_line in cells_max_ncount:
            _ncount = cells_max_ncount[cell_line]["ncount"]
            cell_info = cells_max_ncount[cell_line]["cell_info"]
            self._change_height(cells, cells[cell_info].get_height() * (_ncount + 1), cell_info[0])

    @staticmethod
    def _change_height(cells, height: int, row: int):
        for x, y in cells:
            if x == row:
                cells[(x, y)].set_height(height)

    def add_cells(self, xys, text: str, position=None, double_space=False, facecolor="none", font_size=None, **kwargs):
        """
        加入合并表格
        :param xys: 表格位置二维数组, 顺序为左到右/上到下
        :param text: 文本内容
        :param position: T, B, L, R
        :param double_space : 双倍空格量, 仅当position为T/B时有效
        :param facecolor : 颜色
        :param font_size : 字号
        """
        adds = [self.table.add_cell(px, py, self.w, self.h, loc="center", facecolor=facecolor, **kwargs) for
                px, py in xys]

        p = {  # [开头格, 结尾格, 中间格]
            "T": ["TL", "TR", "T"],
            "B": ["LB", "RB", "B"],
            "L": ["TL", "LB", "L"],
            "R": ["TR", "LR", "R"]
        }

        total_count = len(adds)

        if position in ["L", "R"]:
            write_text = f"\n{text}" if total_count % 2 == 0 else text
            adds[int(total_count / 2) - 1].get_text().set_text(write_text)

        elif position in ["T", "B"]:
            if total_count % 2 == 0:
                adds[int(total_count / 2) - 1].get_text().set_text("  " if double_space else " " * len(text) * 4 + text)
            else:
                adds[int(total_count / 2)].get_text().set_text(text)

        else:
            adds[0].get_text().set_text(text)

        n = 0
        for add in adds:
            if font_size is not None:
                add.set_fontsize(font_size)
            if position in p:
                if n == 0:
                    add.visible_edges = p[position][0]
                elif n == total_count - 1:
                    add.visible_edges = p[position][1]
                else:
                    add.visible_edges = p[position][2]
            n += 1

    def save_image(self, save, dpi=500):
        bbox = self.table.get_window_extent(self.fig.canvas.get_renderer())
        bbox_inches = bbox.transformed(self.fig.dpi_scale_trans.inverted())
        self.fig.savefig(save, dpi=dpi, bbox_inches=bbox_inches, transparent=True, facecolor="none", edgecolor='none')
