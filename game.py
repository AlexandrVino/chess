from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import (Rectangle, Color, Ellipse)
from kivy.config import Config
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import Image
from kivy.lang import Builder
from kivy.core.text import LabelBase

# чтобы запустилось, нужно:
# python -m pip uninstall -y kivy.deps.glew kivy.deps.gstreamer kivy.deps.sdl2 kivy.deps.angle
# python -m pip install docutils pygments pypiwin32 kivy_deps.sdl2==0.1.* kivy_deps.glew==0.1.*
# python -m pip install kivy_deps.gstreamer==0.1.*
# python -m pip install kivy==1.11.1
# если я кривой, и что-то не так сделал, то https://kivy.org/doc/stable/installation/installation-windows.html
# также измените пути в 41, 68, 889, 898, 930, 940, т.к. почему-то при указании короткого путя видет только dict_of_coords.txt

PATH = 'E:/Python/Chess/'
Builder.load_string("""   
<Restart>  
    source: 'icons/restart.png'  
    pos: 50, 700
    size: 35, 35
    font_size: 20

<Save>  
    source: 'icons/save.png'  
    pos: 100, 700
    size: 35, 35
    font_size: 20
""")

switch = 0


def get_dict_of_coords():
    global switch
    file = open(PATH + 'saves/dict_of_coords.txt', 'r')
    dict_of_coords = file.read()
    file.close()
    dict_of = {}
    dict_of_coords = dict_of_coords.split(',')
    if dict_of_coords[-1] != ' ':
        switch = int(dict_of_coords[-1])
    dict_of_coords = dict_of_coords[:-1]
    for elem in dict_of_coords:
        elem = elem.split(':')
        coord = elem[0].split(';')
        if coord != [' ']:
            coord = [int(elem) for elem in coord]
            coord = tuple(coord)
            if len(elem) == 2:
                dict_of[coord] = elem[1].strip()
            else:
                dict_of[coord] = ''

    for i in range(8):
        for j in range(8):
            if (i, j) not in dict_of:
                dict_of[(i, j)] = ''
    return dict_of


def get_list_of_flags():
    file = open(PATH + 'saves/list_of_flags.txt', 'r')
    list_of = file.read()
    list_of_2 = []
    list_of = [elem.strip() for elem in list_of.split(',')]
    for elem in list_of:
        if elem == 'False':
            list_of_2.append(False)
        elif elem == 'True':
            list_of_2.append(True)
    file.close()
    return list_of_2


dict_of_coords = get_dict_of_coords()
list_of_flags = get_list_of_flags()

Config.set('graphics', 'resizable', 0)
Config.set('graphics', 'width', 740)
Config.set('graphics', 'height', 800)

choice = ['б', 'ч']

label = ''


class BoardWidget(Widget):
    def __init__(self, **kwargs):
        super(BoardWidget, self).__init__(**kwargs)
        global list_of_flags
        self.coords = []
        self.attact_figure = []
        self.dict_of_pawn_points = {}
        self.coord_pawn_transformation = ()
        self.is_mat, self.black_king_not_go, self.white_king_not_go, self.can_pawn_transform,\
        self.white_king_attact, self.black_king_attact = list_of_flags
        global dict_of_coords

        with self.canvas:
            self.canvas.add(Rectangle(size=(740, 800), source='canvas/background.png'))
            self.canvas.add(Rectangle(pos=(50, 50), size=(640, 640), source='canvas/board.png'))
            for coordinate in dict_of_coords:
                row, col = coordinate
                if dict_of_coords[coordinate]:
                    if 'б.' in dict_of_coords[coordinate]:
                        text = 'белые'
                    else:
                        text = 'черные'
                    if 'король' not in dict_of_coords[coordinate]:
                        if text == 'белые':
                            text = 'figures/white/' + dict_of_coords[coordinate][2:] + '.png'
                            self.canvas.add(
                                Rectangle(pos=(col * 80 + 50, (7 - row) * 80 + 50), size=(80, 80), source=text))
                        else:
                            text = 'figures/blaсk/' + dict_of_coords[coordinate][2:] + '.png'
                            self.canvas.add(
                                Rectangle(pos=(col * 80 + 50, (7 - row) * 80 + 50), size=(80, 80), source=text))
                    else:
                        if 'б.король' in dict_of_coords[coordinate]:
                            if not self.white_king_attact:
                                text = 'figures/white' + '/' + dict_of_coords[coordinate][2:] + '.png'
                                self.canvas.add(
                                    Rectangle(pos=(col * 80 + 50, (7 - row) * 80 + 50), size=(80, 80), source=text))
                            else:
                                text = 'figures/on_fire' + '/' + dict_of_coords[coordinate][2:] + '.png'
                                self.canvas.add(
                                    Rectangle(pos=(col * 80 + 50, (7 - row) * 80 + 50), size=(80, 80), source=text))
                        else:
                            if not self.black_king_attact:
                                text = 'figures/blaсk' + '/' + dict_of_coords[coordinate][2:] + '.png'
                                self.canvas.add(
                                    Rectangle(pos=(col * 80 + 50, (7 - row) * 80 + 50), size=(80, 80), source=text))
                            else:
                                text = 'figures/on_fire' + '/' + dict_of_coords[coordinate][2:] + '.png'
                                self.canvas.add(
                                    Rectangle(pos=(col * 80 + 50, (7 - row) * 80 + 50), size=(80, 80), source=text))

    def on_touch_down(self, touch):
        """
        Функция передвижения фигур
        """
        global dict_of_coords
        global choice
        global switch
        global list_of_flags

        if self.is_mat:
            return

        try:
            if not self.coords:  # тут вычисляются координаты фигуры и клетки куда она может сходить
                for i in range(50, 691, 80):
                    for j in range(50, 691, 80):
                        if touch.y + 80 > i > touch.y and touch.x + 80 > j > touch.x:
                            row, col = 7 - (i - 80) // 80, (j - 80) // 80
                            if self.correct_coords(row, col):
                                self.coords.append([row, col])
                                break

                if choice[switch] == 'б':
                    is_king_attacked = self.white_king_attact  # проверка атакован ли король тех, кто ходит
                else:
                    is_king_attacked = self.black_king_attact  # проверка атакован ли король тех, кто ходит

                row, col = self.coords[0]
                if not is_king_attacked:  # если не атакован
                    if not self.can_pawn_transform:  # проверка достигла ли пешка одной из грониц
                        for i in range(8):
                            for j in range(8):
                                try:
                                    if choice[switch] == dict_of_coords[row, col][0] \
                                            and not self.check_check(row, col, i, j):
                                        if dict_of_coords[(row, col)][:2] != dict_of_coords[(i, j)][:2]:
                                            if self.coords[0] != (i, j) and 'король' not in dict_of_coords[(i, j)]:
                                                if self.can_move(dict_of_coords[(row, col)],
                                                                 row, col, i, j, dict_of_coords):
                                                    if dict_of_coords[(i, j)] == '':
                                                        self.canvas.add(Rectangle(pos=(j * 80 + 80, (7 - i) * 80 + 80),
                                                                                  size=(20, 20),
                                                                                  source='icons/on_cell.png'))
                                                    else:
                                                        name = dict_of_coords[(i, j)][2:]
                                                        name = name.strip()
                                                        name = 'figures/on_fire/' + name + '.png'
                                                        self.canvas.add(Rectangle(pos=(j * 80 + 50, (7 - i) * 80 + 50),
                                                                                  size=(80, 80), source=name))
                                except:
                                    pass

                    else:  # пешка достигла одной из грониц 
                        color = dict_of_coords[(row, col)][:2]
                        self.dict_of_pawn_points[(row, col)] = touch.x, touch.y
                        self.can_pawn_transformation(color, row, col)
                        self.coords = []
                        return

                else:  # если аткован 
                    flag = True
                    for i in range(8):
                        for j in range(8):
                            if choice[switch] == dict_of_coords[row, col][0]:
                                if dict_of_coords[(row, col)][:2] != dict_of_coords[(i, j)][:2]:
                                    if self.coords[0] != (i, j) and 'король' not in dict_of_coords[(i, j)]:
                                        if self.can_move(dict_of_coords[(row, col)], row, col, i, j, dict_of_coords):
                                            if not self.check_check(row, col, i, j) and \
                                                    'король' not in dict_of_coords[(row, col)]:

                                                if dict_of_coords[(i, j)] == '':
                                                    self.canvas.add(Rectangle(pos=(j * 80 + 80, (7 - i) * 80 + 80),
                                                                              size=(20, 20),
                                                                              source='icons/on_cell.png'))
                                                    flag = False
                                                else:
                                                    name = dict_of_coords[(i, j)][2:]
                                                    name = name.strip()
                                                    name = 'figures/on_fire/' + name + '.png'
                                                    self.canvas.add(Rectangle(pos=(j * 80 + 50, (7 - i) * 80 + 50),
                                                                              size=(80, 80), source=name))
                                                    flag = False
                                            else:
                                                if 'король' in dict_of_coords[(row, col)] and \
                                                        not self.check_check(row, col, i, j):
                                                    color = dict_of_coords[(row, col)][0]
                                                    if (i, j) == self.attact_figure:
                                                        if dict_of_coords[(i, j)] == '':
                                                            self.canvas.add(Rectangle(pos=(j * 80 + 80,
                                                                                           (7 - i) * 80 + 80),
                                                                                      size=(20, 20),
                                                                                      source='icons/on_cell.png'))
                                                            flag = False
                                                        else:
                                                            name = dict_of_coords[(i, j)][2:]
                                                            name = name.strip()
                                                            name = 'figures/on_fire/' + name + '.png'
                                                            self.canvas.add(Rectangle(pos=(j * 80 + 50,
                                                                                           (7 - i) * 80 + 50),
                                                                                      size=(80, 80), source=name))
                                                            flag = False
                                                    else:
                                                        if dict_of_coords[(i, j)] == '' and not self.check_check(row, col, i, j):
                                                            if dict_of_coords[(i, j)] == '':
                                                                self.canvas.add(Rectangle(pos=(j * 80 + 80,
                                                                                           (7 - i) * 80 + 80),
                                                                                      size=(20, 20),
                                                                                      source='icons/on_cell.png'))
                                                            flag = False
                    if flag:
                        if self.white_king_attact:
                            color = 'б'
                        elif self.black_king_attact:
                            color = 'ч'
                        for i in range(8):
                            for j in range(8):
                                if dict_of_coords[(i, j)] != '':
                                    if dict_of_coords[(i, j)][0] == color:
                                        for i1 in range(8):
                                            for j1 in range(8):
                                                if dict_of_coords[(i1, j1)] != '':
                                                    if ('король' not in dict_of_coords[(i, j)] or
                                                        (i1, j1) == self.attact_figure) and \
                                                            dict_of_coords[(i, j)][0] != dict_of_coords[(i1, j1)][0]:

                                                        if self.can_move(dict_of_coords[(i, j)], i, j, i1, j1,
                                                                         dict_of_coords):

                                                            if not self.check_check(i, j, i1, j1):
                                                                self.coords = []
                                                                flag = False
                                                else:
                                                    if 'король' not in dict_of_coords[(i, j)]:
                                                        if not self.check_check(i, j, i1, j1):
                                                            self.coords = []
                                                            flag = False
                        if color == 'б':
                            color = 'ч'
                        else:
                            color = 'б'
                        if flag:
                            self.mat(color)
            else:
                for i in range(50, 691, 80):
                    for j in range(50, 691, 80):
                        if touch.y + 80 > i > touch.y and touch.x + 80 > j > touch.x:
                            row, col = 7 - (i - 80) // 80, (j - 80) // 80
                            if self.correct_coords(row, col):
                                self.coords.append([row, col])
                                break

                row, col = self.coords[0]
                row1, col1 = self.coords[1]
                if choice[switch] == 'б':
                    is_king_attacked = self.white_king_attact  # проверка атакован ли король тех, кто ходит
                else:
                    is_king_attacked = self.black_king_attact  # проверка атакован ли король тех, кто ходит

                if not is_king_attacked:  # если не атакован
                    if choice[switch] == dict_of_coords[(row, col)][0] \
                            and self.correct_coords(row, col) and self.correct_coords(row1, col1):

                        name_figure = dict_of_coords[(row, col)]

                        if dict_of_coords[(row, col)] != '' and not self.check_check(row, col, row1, col1):
                            if dict_of_coords[(row1, col1)] != '' and dict_of_coords[(row, col)][0] == \
                                    dict_of_coords[(row1, col1)][0]:
                                if 'ч.король' in dict_of_coords[(row, col)] or \
                                        'ч.король' in dict_of_coords[(row1, col1)]:
                                    flag = self.black_king_not_go
                                elif 'б.король' in dict_of_coords[(row, col)] \
                                        or 'б.король' in dict_of_coords[(row1, col1)]:
                                    flag = self.white_king_not_go

                                if flag:
                                    if 'б.король' in dict_of_coords[(row, col)] \
                                            or 'б.король' in dict_of_coords[(row1, col1)]:
                                        self.white_king_not_go = False
                                    elif 'ч.король' in dict_of_coords[(row, col)] \
                                            or 'ч.король' in dict_of_coords[(row1, col1)]:
                                        self.black_king_not_go = False

                                    self.regrowing(row, col, col1)
                                    if switch == 0:
                                        switch = 1
                                    else:
                                        switch = 0

                            elif dict_of_coords[(row1, col1)] == '' and self.can_move(name_figure, row, col, row1, col1,
                                                                                      dict_of_coords):
                                if 'ч.король' in dict_of_coords[(row, col)]:
                                    self.black_king_not_go = False
                                elif 'б.король' in dict_of_coords[(row, col)]:
                                    self.white_king_not_go = False
                                dict_of_coords[(row1, col1)], dict_of_coords[(row, col)] = \
                                    dict_of_coords[(row, col)], dict_of_coords[(row1, col1)]
                                if switch == 0:
                                    switch = 1
                                else:
                                    switch = 0
                                update_label()

                            elif dict_of_coords[(row1, col1)] != '' and self.can_move(name_figure, row, col, row1, col1,
                                                                                      dict_of_coords):
                                if 'ч.король' in dict_of_coords[(row, col)]:
                                    self.black_king_not_go = False
                                elif 'б.король' in dict_of_coords[(row, col)]:
                                    self.white_king_not_go = False
                                dict_of_coords[(row1, col1)] = dict_of_coords[(row, col)]
                                dict_of_coords[(row, col)] = ''
                                if switch == 0:
                                    switch = 1
                                else:
                                    switch = 0
                                update_label()

                else:  # если атакован
                    if choice[switch] == dict_of_coords[(row, col)][0]:
                        
                        if not self.check_check(row, col, row1, col1) and 'король' not in dict_of_coords[(row, col)]:
                            if dict_of_coords[(row1, col1)] == '' and self.can_move(dict_of_coords[(row, col)], row,
                                                                                    col, row1, col1, dict_of_coords):
                                color = dict_of_coords[(row, col)][0]
                                if color == 'б':
                                    self.white_king_attact = False
                                else:
                                    self.black_king_attact = False
                                dict_of_coords[(row, col)], dict_of_coords[(row1, col1)] = \
                                    dict_of_coords[(row1, col1)], dict_of_coords[(row, col)]
                                if switch == 0:
                                    switch = 1
                                else:
                                    switch = 0
                                update_label()

                            elif dict_of_coords[(row1, col1)] != '' and self.can_move(dict_of_coords[(row, col)], row,
                                                                                      col, row1, col1, dict_of_coords):
                                color = dict_of_coords[(row, col)][0]
                                if color == 'б':
                                    self.white_king_attact = False
                                else:
                                    self.black_king_attact = False
                                dict_of_coords[(row1, col1)] = dict_of_coords[(row, col)]
                                dict_of_coords[(row, col)] = ''
                                if switch == 0:
                                    switch = 1
                                else:
                                    switch = 0
                                update_label()

                        else:
                            if 'король' in dict_of_coords[(row, col)]:
                                color = dict_of_coords[(row, col)][0]
                                if dict_of_coords[(row1, col1)] == '' and not self.check_check(row, col, row1, col1):
                                    if self.can_move(dict_of_coords[(row, col)], row, col, row1, col1, dict_of_coords):
                                        color = dict_of_coords[(row, col)][0]
                                        if color == 'б':
                                            self.white_king_attact = False
                                        else:
                                            self.black_king_attact = False
                                        dict_of_coords[(row, col)], dict_of_coords[(row1, col1)] = \
                                            dict_of_coords[(row1, col1)], dict_of_coords[(row, col)]

                                        if switch == 0:
                                            switch = 1
                                        else:
                                            switch = 0
                                        update_label()

                                else:
                                    
                                    if self.can_move(dict_of_coords[(row, col)], row, col, row1, col1, dict_of_coords):
                                        if (row1, col1) == self.attact_figure:
                                            if not self.check_check(row, col, row1, col1):
                                                color = dict_of_coords[(row, col)][0]
                                                if color == 'б':
                                                    self.white_king_attact = False
                                                else:
                                                    self.black_king_attact = False
                                                dict_of_coords[(row1, col1)] = dict_of_coords[(row, col)]
                                                dict_of_coords[(row, col)] = ''
                                                if switch == 0:
                                                    switch = 1
                                                else:
                                                    switch = 0
                                                update_label()

                                            else:
                                                if self.white_king_attact:
                                                    color = 'б'
                                                elif self.black_king_attact:
                                                    color = 'ч'
                                                for i in range(8):
                                                    for j in range(8):
                                                        if dict_of_coords[(i, j)] != '':
                                                            if dict_of_coords[(i, j)][0] == color:
                                                                for i1 in range(8):
                                                                    for j1 in range(8):
                                                                        if dict_of_coords[(i1, j1)] != '':
                                                                            if ('король' not in dict_of_coords[
                                                                                (i, j)] or (
                                                                                        i1,
                                                                                        j1) == self.attact_figure) and \
                                                                                    dict_of_coords[(i, j)][0] != \
                                                                                    dict_of_coords[(i1, j1)][0]:
                                                                                if self.can_move(dict_of_coords[(i, j)],
                                                                                                 i, j, i1, j1,
                                                                                                 dict_of_coords):
                                                                                    if not self.check_check(i, j, i1,
                                                                                                            j1):
                                                                                        self.coords = []
                                                                                        return
                                                                        else:
                                                                            if 'король' not in dict_of_coords[(i, j)]:
                                                                                if not self.check_check(i, j, i1, j1):
                                                                                    self.coords = []
                                                                                    return

                self.create_canvas()
                self.coords = []
                self.checkmate(touch)

        except:
            self.create_canvas()
            self.coords = []

    def mat(self, color):
        self.is_mat = True
        if color == 'б':
            self.canvas.add(Rectangle(pos=(50, 50), size=(640, 640), source='canvas/white_win.png'))
        else:
            self.canvas.add(Rectangle(pos=(50, 50), size=(640, 640), source='canvas/black_win.png'))

    def regrowing(self, row, col, col1):  # фунцция рокировки
        if (('король' in dict_of_coords[(row, col)] and 'ладья' in dict_of_coords[(row, col1)]) or
                ('король' in dict_of_coords[(row, col1)] and 'ладья' in dict_of_coords[(row, col)])):
            if self.can_regrowing(row, col, col1):
                if col1 == 7:
                    dict_of_coords[(row, col)], dict_of_coords[(row, 5)] = dict_of_coords[(row, 5)], dict_of_coords[
                        (row, col)]
                    dict_of_coords[(row, col1)], dict_of_coords[(row, 4)] = dict_of_coords[(row, 4)], dict_of_coords[
                        (row, col1)]
                    update_label()

                elif col1 == 0:
                    dict_of_coords[(row, col)], dict_of_coords[(row, 1)] = dict_of_coords[(row, 1)], dict_of_coords[
                        (row, col)]
                    dict_of_coords[(row, col1)], dict_of_coords[(row, 2)] = dict_of_coords[(row, 2)], dict_of_coords[
                        (row, col1)]
                    update_label()

    def create_canvas(self):
        """
        Фунцция перерисовки поля
        """
        global list_of_flags
        self.canvas.clear()
        self.canvas.add(Rectangle(size=(740, 800), source='canvas/background.png'))
        self.canvas.add(Rectangle(pos=(50, 50), size=(640, 640), source='canvas/board.png'))
        flag = False
        for coordinate in dict_of_coords:
            row, col = coordinate
            if dict_of_coords[coordinate]:
                if (row == 0 or row == 7) and 'пешка' in dict_of_coords[coordinate]:
                    color = dict_of_coords[coordinate][:2]
                    flag = True
                    row1 = row
                    col1 = col
                if 'б.' in dict_of_coords[coordinate]:
                    text = 'белые'
                else:
                    text = 'черные'
                if 'король' not in dict_of_coords[coordinate]:
                    if text == 'белые':
                        text = 'figures/white' + '/' + dict_of_coords[coordinate][2:] + '.png'
                        self.canvas.add(Rectangle(pos=(col * 80 + 50, (7 - row) * 80 + 50), size=(80, 80), source=text))
                    else:
                        text = 'figures/blaсk' + '/' + dict_of_coords[coordinate][2:] + '.png'
                        self.canvas.add(Rectangle(pos=(col * 80 + 50, (7 - row) * 80 + 50), size=(80, 80), source=text))
                else:
                    if 'б.король' in dict_of_coords[coordinate]:
                        if not self.white_king_attact:
                            text = 'figures/white' + '/' + dict_of_coords[coordinate][2:] + '.png'
                            self.canvas.add(
                                Rectangle(pos=(col * 80 + 50, (7 - row) * 80 + 50), size=(80, 80), source=text))
                        else:
                            text = 'figures/on_fire' + '/' + dict_of_coords[coordinate][2:] + '.png'
                            self.canvas.add(
                                Rectangle(pos=(col * 80 + 50, (7 - row) * 80 + 50), size=(80, 80), source=text))
                    else:
                        if not self.black_king_attact:
                            text = 'figures/blaсk' + '/' + dict_of_coords[coordinate][2:] + '.png'
                            self.canvas.add(
                                Rectangle(pos=(col * 80 + 50, (7 - row) * 80 + 50), size=(80, 80), source=text))
                        else:
                            text = 'figures/on_fire' + '/' + dict_of_coords[coordinate][2:] + '.png'
                            self.canvas.add(
                                Rectangle(pos=(col * 80 + 50, (7 - row) * 80 + 50), size=(80, 80), source=text))
        if flag:
            self.can_pawn_transformation(color, row1, col1)
        list_of_flags = [self.is_mat, self.black_king_not_go, self.white_king_not_go, self.can_pawn_transform,
                         self.white_king_attact, self.black_king_attact]

    def correct_coords(self, row, col):
        """
        Фунцция проверка на коректные координаты
        """
        if 0 <= row <= 7 and 0 <= col <= 7:
            return True
        else:
            return False

    def can_move(self, name_of_figure, row, col, row1, col1, dict_of_coords):
        """
        Фунцция проверки того, может ли фигура сходить
        """
        if row == row1 and col == col1:
            return False

        if dict_of_coords[(row, col)] != '' and dict_of_coords[(row1, col1)] != '':
            if dict_of_coords[(row, col)][0] == dict_of_coords[(row1, col1)][0]:
                return False

        if 'пешка' in name_of_figure:
            if name_of_figure[0] == 'б':
                if col == col1 and row == row1 - 1 and dict_of_coords[row1, col1] == '':
                    return True
                if col == col1 and row == row1 - 2:
                    if dict_of_coords[row1 - 1, col1] == '' and dict_of_coords[row1, col1] == '':
                        if row == 1:
                            return True
                if abs(col - col1) == 1 and row == row1 - 1:
                    if dict_of_coords[(row1, col1)] != '':
                        return True
                return False

            else:
                if col == col1 and row == row1 + 1 and dict_of_coords[row1, col1] == '':
                    return True
                if col == col1 and row == row1 + 2:
                    if dict_of_coords[row1 + 1, col1] == '' and dict_of_coords[row1, col1] == '':
                        if row == 6:
                            return True
                if abs(col - col1) == 1 and row == row1 + 1:
                    if dict_of_coords[(row1, col1)] != '':
                        return True
                return False

        elif 'ладья' in name_of_figure:
            piece1 = dict_of_coords[(row1, col1)]

            if dict_of_coords[(row, col)] != '' and dict_of_coords[(row1, col1)] != '':
                if not (piece1 == '') and dict_of_coords[(row, col)][0] == dict_of_coords[(row1, col1)][0]:
                    return False
            else:
                if not (piece1 == ''):
                    return False

            if row == row1 or col == col1:
                step = 1 if (row1 >= row) else -1
                for r in range(row + step, row1, step):
                    if not (dict_of_coords[(r, col)] == ''):
                        return False
                step = 1 if (col1 >= col) else -1
                for c in range(col + step, col1, step):
                    if not (dict_of_coords[(row, c)] == ''):
                        return False
                return True

        elif 'конь' in name_of_figure:
            if dict_of_coords[(row1, col1)] != '':
                if abs(row - row1) * abs(col - col1) == 2 and dict_of_coords[(row, col)][0] != \
                        dict_of_coords[(row1, col1)][0]:
                    return True
            else:
                if abs(row - row1) * abs(col - col1) == 2:
                    return True
            return False

        elif 'слон' in name_of_figure:
            if not (0 <= row1 <= 7) or not (0 <= col1 <= 7):
                return False

            piece1 = dict_of_coords[(row1, col1)]
            if dict_of_coords[(row, col)] != '' and dict_of_coords[(row1, col1)] != '':
                if not (piece1 == '') and dict_of_coords[(row, col)][0] == dict_of_coords[(row1, col1)][0]:
                    return False
            else:
                if not (piece1 == ''):
                    return False

            if row - col == row1 - col1:
                step = 1 if (row1 >= row) else -1
                for r in range(row + step, row1, step):
                    c = col - row + r
                    if not (dict_of_coords[(r, c)] == ''):
                        return False
                return True

            if row + col == row1 + col1:
                step = 1 if (row1 >= row) else -1
                for r in range(row + step, row1, step):
                    c = row + col - r
                    if not (dict_of_coords[(r, c)] == ''):
                        return False
                return True

            return False

        elif 'ферзь' in name_of_figure:
            if row == row1 or col == col1:
                step = 1 if (row1 >= row) else -1
                for r in range(row + step, row1, step):
                    if not (dict_of_coords[(r, col)] == ''):
                        return False
                step = 1 if (col1 >= col) else -1
                for c in range(col + step, col1, step):
                    if not (dict_of_coords[(row, c)] == ''):
                        return False
                return True

            piece1 = dict_of_coords[(row1, col1)]
            if dict_of_coords[(row, col)] != '' and dict_of_coords[(row1, col1)] != '':
                if not (piece1 == '') and dict_of_coords[(row, col)][0] == dict_of_coords[(row1, col1)][0]:
                    return False
            else:
                if not (piece1 == ''):
                    return False

            if row - col == row1 - col1:
                step = 1 if (row1 >= row) else -1
                for r in range(row + step, row1, step):
                    c = col - row + r
                    if not (dict_of_coords[(r, c)] == ''):
                        return False
                return True

            if row + col == row1 + col1:
                step = 1 if (row1 >= row) else -1
                for r in range(row + step, row1, step):
                    c = row + col - r
                    if not (dict_of_coords[(r, c)] == ''):
                        return False
                return True

            return False

        elif 'король' in name_of_figure:
            if (abs(row - row1) == 1 and 0 <= abs(col - col1) <= 1 and
                    (dict_of_coords[(row1, col1)] == '' or
                     dict_of_coords[(row, col)][:2] != dict_of_coords[(row1, col1)][:2])):
                return True
            if (abs(row - row1) == 0 and abs(col - col1) == 1 and
                    (dict_of_coords[(row1, col1)] == '' or
                     dict_of_coords[(row, col)][:2] != dict_of_coords[(row1, col1)][:2])):
                return True
            return False

        return False

    def can_regrowing(self, row, col, col1):
        """
        Функция проверки можно ли сделать рокировку
        """
        min_col, max_col = min(col, col1), max(col, col1)
        for i in range(min_col + 1, max_col):
            if dict_of_coords[(row, i)] != '':
                return False
        return True

    def can_pawn_transformation(self, color, row, col):
        """
        Функция превращения пешки
        """
        global dict_of_coords

        if 'пешка' in dict_of_coords[(row, col)] and not self.can_pawn_transform:
            self.can_pawn_transform = True
            self.canvas.add(Rectangle(pos=(50, 50), size=(640, 640), source='canvas/castling.png'))
            self.coord_pawn_transformation = (row, col)

        elif self.can_pawn_transform:
            try:
                coordinate = self.coord_pawn_transformation
                row, col = self.dict_of_pawn_points[(row, col)]
                if 135 <= row <= 255 and 320 <= col <= 440:
                    text = 'слон'
                elif 210 <= row <= 330 and 160 <= col <= 280:
                    text = 'ферзь'
                elif 410 <= row <= 530 and 160 <= col <= 280:
                    text = 'конь'
                elif 490 <= row <= 610 and 320 <= col <= 440:
                    text = 'ладья'

                self.can_pawn_transform = False
                self.coord_pawn_transformation = ()
                dict_of_coords[coordinate] = dict_of_coords[coordinate][:2] + text
                self.create_canvas()

            except:
                pass

    def checkmate(self, touch):
        """
        Функция проверки на шах и мат
        """
        coords = []
        for i in range(50, 691, 80):
            for j in range(50, 691, 80):
                if touch.y + 80 > i > touch.y and touch.x + 80 > j > touch.x:
                    row, col = 7 - (i - 80) // 80, (j - 80) // 80
                    if self.correct_coords(row, col):
                        coords.append([row, col])
                        break

        row, col = coords[0]
        for i in range(8):
            for j in range(8):
                if 'король' in dict_of_coords[(i, j)]:
                    if dict_of_coords[(row, col)][:2] != dict_of_coords[(i, j)][:2]:
                        if self.can_move(dict_of_coords[(row, col)], row, col, i, j, dict_of_coords):
                            self.attact_figure = (row, col)
                            name = dict_of_coords[(i, j)]
                            if 'б' in name:
                                self.white_king_attact = True
                            else:
                                self.black_king_attact = True
                            name = name[2:]
                            name = name.strip()
                            name = 'figures/on_fire/' + name + '.png'
                            self.canvas.add(Rectangle(pos=(j * 80 + 50, (7 - i) * 80 + 50), size=(80, 80), source=name))

    def check_check(self, row, col, row1, col1):
        """
        Функция проверки можно ли так сходить, чтобы не было шаха
        """
        color = dict_of_coords[(row, col)][0]
        dict_of_coords_copy = dict_of_coords.copy()

        if dict_of_coords_copy[(row1, col1)] == '' and self.can_move(dict_of_coords_copy[(row, col)], row, col, row1,
                                                                     col1, dict_of_coords_copy):
            dict_of_coords_copy[(row, col)], dict_of_coords_copy[(row1, col1)] = dict_of_coords_copy[(row1, col1)], \
                                                                                 dict_of_coords_copy[(row, col)]

        elif dict_of_coords_copy[(row1, col1)] != '' and self.can_move(dict_of_coords_copy[(row, col)], row, col, row1,
                                                                       col1, dict_of_coords_copy):
            dict_of_coords_copy[(row1, col1)] = dict_of_coords_copy[(row, col)]
            dict_of_coords_copy[(row, col)] = ''

        for i in range(8):
            for j in range(8):
                if 'король' in dict_of_coords_copy[(i, j)]:
                    if color == dict_of_coords_copy[(i, j)][0]:
                        rows, cols = i, j
        try:
            for i in range(8):
                for j in range(8):
                    if dict_of_coords_copy[(rows, cols)][:2] != dict_of_coords_copy[(i, j)][:2]:
                        if self.can_move(dict_of_coords_copy[(i, j)], i, j, rows, cols, dict_of_coords_copy):
                            return True
            return False

        except:
            pass


def update_label():
    global switch
    global choice
    global label

    if choice[switch] == 'б':
        text = 'white'
    else:
        text = 'black'
    label.text = 'Move ' + text


class Restart(ButtonBehavior, Image):
    """
    Кнопка рестарта (я сделал под кнопку отдельный класс, чтобы поставить на фон изображение)
    """
    pass


class Save(ButtonBehavior, Image):
    """
    Кнопка сохраненя (я сделал под кнопку отдельный класс, чтобы поставить на фон изображение)
    """
    pass


class PlayGroundApp(App):
    def build(self):  # тут создаю непосредственно окно
        global choice
        global switch
        global label

        self.title = "CHESS"
        if choice[switch] == 'б':
            text = 'white'
        else:
            text = 'black'

        self.lbl = Label(pos=(100, 700), size=(540, 50), text='Move ' + text, font_size=26,
                         font_name="font/Montserrat-Bold.ttf")
        label = self.lbl
        self.button = [0 for _ in range(3)]
        self.button[0] = self.lbl
        self.button[1] = Restart(on_press=self.restart)
        self.button[2] = Save(on_press=self.save)

        bl = Widget()
        self.desk = BoardWidget()
        bl.add_widget(self.desk)
        bl.add_widget(self.button[0])
        bl.add_widget(self.button[1])
        bl.add_widget(self.button[2])

        return bl

    def restart(self, instance):
        global dict_of_coords
        global choice
        global switch
        global list_of_flags

        list_of_flags = [False, True, True, False, False, False]

        choice = ['б', 'ч']

        switch = 0

        dict_of_coords = {(0, 0): 'б.ладья', (0, 1): 'б.конь', (0, 2): 'б.слон', (0, 3): 'б.король',
                          (0, 4): 'б.ферзь', (0, 5): 'б.слон', (0, 6): 'б.конь', (0, 7): 'б.ладья',

                          (1, 0): 'б.пешка', (1, 1): 'б.пешка', (1, 2): 'б.пешка', (1, 3): 'б.пешка',
                          (1, 4): 'б.пешка', (1, 5): 'б.пешка', (1, 6): 'б.пешка', (1, 7): 'б.пешка',

                          (6, 0): 'ч.пешка', (6, 1): 'ч.пешка', (6, 2): 'ч.пешка', (6, 3): 'ч.пешка',
                          (6, 4): 'ч.пешка', (6, 5): 'ч.пешка', (6, 6): 'ч.пешка', (6, 7): 'ч.пешка',

                          (7, 0): 'ч.ладья', (7, 1): 'ч.конь', (7, 2): 'ч.слон', (7, 3): 'ч.король',
                          (7, 4): 'ч.ферзь', (7, 5): 'ч.слон', (7, 6): 'ч.конь', (7, 7): 'ч.ладья'}

        self.desk.coords = []
        self.desk.attact_figure = []
        self.desk.dict_of_pawn_points = {}
        self.desk.coord_pawn_transformation = ()
        self.desk.is_mat, self.desk.black_king_not_go, self.desk.white_king_not_go, self.desk.can_pawn_transform, self.desk.white_king_attact, self.desk.black_king_attact = list_of_flags

        for i in range(2, 6):
            for j in range(0, 8):
                dict_of_coords[(i, j)] = ''

        file = open(PATH + 'saves/dict_of_coords.txt', 'w')
        for coordinate in dict_of_coords:
            if dict_of_coords[coordinate] != '':
                file.write(str(coordinate[0]) + ';' + str(coordinate[1]) + ': ' + dict_of_coords[coordinate] + ', ')
            else:
                coordinate = str(coordinate[0]) + ';' + str(coordinate[1])
                file.write(coordinate + ': ' + ', ')
        file.close()

        file = open(PATH + 'saves/list_of_flags.txt', 'w')
        a = [str(elem) for elem in list_of_flags]
        file.write(','.join(a))
        file.close()

        if choice[switch] == 'ч':
            color_figure = 'black'
        else:
            color_figure = 'white'
        label.text = "Move " + color_figure


        self.desk.canvas.clear()
        self.desk.canvas.add(Rectangle(size=(740, 800), source='canvas/background.png'))
        self.desk.canvas.add(Rectangle(pos=(50, 50), size=(640, 640), source='canvas/board.png'))
        for coordinate in dict_of_coords:
            row, col = coordinate
            if dict_of_coords[coordinate]:
                if 'б.' in dict_of_coords[coordinate]:
                    text = 'белые'
                else:
                    text = 'черные'
                if text == 'белые':
                    text = 'figures/white/' + dict_of_coords[coordinate][2:] + '.png'
                    self.desk.canvas.add(Rectangle(pos=(col * 80 + 50, (7 - row) * 80 + 50), size=(80, 80), source=text))
                else:
                    text = 'figures/blaсk/' + dict_of_coords[coordinate][2:] + '.png'
                    self.desk.canvas.add(Rectangle(pos=(col * 80 + 50, (7 - row) * 80 + 50), size=(80, 80), source=text))

    def save(self, instance):
        global dict_of_coords
        global list_of_flags
        file = open(PATH + 'saves/dict_of_coords.txt', 'w')
        for coordinate in dict_of_coords:
            if dict_of_coords[coordinate] != '':
                file.write(str(coordinate[0]) + ';' + str(coordinate[1]) + ': ' + dict_of_coords[coordinate] + ', ')
            else:
                coordinate = str(coordinate[0]) + ';' + str(coordinate[1])
                file.write(coordinate + ': ' + ', ')
        file.write(str(switch))
        file.close()

        file = open(PATH + 'saves/list_of_flags.txt', 'w')
        a = [str(elem) for elem in list_of_flags]
        file.write(','.join(a))
        file.close()


if __name__ == '__main__':
    PlayGroundApp().run()