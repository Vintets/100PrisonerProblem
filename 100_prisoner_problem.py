#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Задача о 100 заключённых
https://www.youtube.com/watch?v=wWQ9YdreY9c

/*******************************************************
 * Copyright 2022 Vintets <programmer@vintets.ru> - All Rights Reserved
 *
 * Unauthorized copying of this file, via any medium is strictly prohibited
 * Proprietary and confidential
 * Written by Vintets <programmer@vintets.ru>, July 2022
 *
 * This file is part of 100PrisonerProblem project.
 * 100PrisonerProblem can not be copied and/or distributed without the express
 * permission of Vintets
*******************************************************/

# for python 3.9.7 and over
"""

__version_info__ = ('0', '2', '1')
__version__ = '.'.join(__version_info__)


import os
import sys
import time
from pathlib import Path  # noqa: F401
import shutil
from dataclasses import dataclass
from abc import ABC, abstractmethod
from random import shuffle, seed, choice
from pprint import pprint  # noqa: F401
# from typing import Optional
import configs.config as cfg
import accessory.colorprint as cp
import accessory.clear_console as cc
import accessory.authorship as auth_sh
# import accessory.errors as err
# import accessory.utils as utils


WIDTH_CONSOL = shutil.get_terminal_size().columns


@dataclass
class Prisoner:
    id: int


@dataclass
class Box:
    id: int
    number_on_paper: int
    opened: bool = False


class Strategy(ABC):
    name = None

    @abstractmethod
    def next_box(self, prisoner, closed_boxes):
        pass


class StrategyRandom(Strategy):
    name = 'Random (Случайный выбор)'

    def next_box(self, prisoner, closed_boxes):
        return choice(closed_boxes)


class StrategyChainLength(Strategy):
    name = 'ChainLength (перевод вероятности к длине цепочек)'

    def next_box(self, prisoner, closed_boxes):
        pass


class Room:
    def __init__(self, boxes, strategy):
        self.boxes = boxes
        self.strategy = strategy

    def close_all_boxes(self):
        for box in self.boxes:
            box.opened = False

    def get_count_open_boxes(self):
        return sum(1 for box in self.boxes if box.opened)

    def get_line_box_data(self, row, property):
        indent = ' ' * cfg.INDENT_HORIZONTAL
        line_data = []
        for col in range(10):
            el = row * 10 + col
            box = self.boxes[el]
            # data = box.id if property == 'id' else box.number_on_paper
            if property == 'id':
                data = box.id
                color_text = cfg.COLOR_NUM_BOX
            else:
                data = box.number_on_paper
                color_text = cfg.COLOR_NUM_PAPER
                if box.opened:
                    color_text = cfg.COLOR_OPEN_BOX
            line_data.append(f'{indent}│ ^{color_text}_{data:^3}^20_ │')
        return ''.join(line_data)

    def __str__(self):
        '''┌─────┐
           │ 100 │
           ├─────┤
           │ 100 │
           └─────┘'''

        s_up = (' ' * cfg.INDENT_HORIZONTAL + '┌─────┐') * 10
        s_md = (' ' * cfg.INDENT_HORIZONTAL + '├─────┤') * 10
        s_dn = (' ' * cfg.INDENT_HORIZONTAL + '└─────┘') * 10
        graph = []
        for row in range(10):
            graph.append(s_up)
            graph.append(self.get_line_box_data(row, property='id'))
            graph.append(s_md)
            graph.append(self.get_line_box_data(row, property='number_on_paper'))
            graph.append(s_dn)
            for i in range(cfg.INDENT_VERTICAL):
                graph.append('')
        cp.cprint('\n'.join(graph))

        return f'Открытых коробок: {self.get_count_open_boxes()}'

    def get_closed_boxes(self):
        return [box for box in self.boxes if not box.opened]

    def open_box(self, box):
        box.opened = True
        return box.number_on_paper

    def prisoner_go(self, prisoner):
        result = False
        if cfg.LOG_LEVEL > 2:
            print(f'\nЗаключённый {prisoner.id}')
        for i in range(int(cfg.NUMBER_OF_PRISONERS / 2)):
            next_box = self.strategy.next_box(prisoner, closed_boxes=self.get_closed_boxes())
            number_on_paper = self.open_box(next_box)
            if cfg.LOG_LEVEL > 3:
                print(f'{next_box}  {number_on_paper = }')
            if number_on_paper == prisoner.id:
                result = True
                if cfg.LOG_LEVEL > 2:
                    print(f'Открытых коробок: {self.get_count_open_boxes()}')
                break
        else:
            if cfg.LOG_LEVEL > 1 and cfg.LOG_LEVEL != 5:
                print(f'\nЗаключённый {prisoner.id}')
                print(self)

        if cfg.LOG_LEVEL > 4:
            print(self)
        return result


def get_strategy():
    strategy = None
    if cfg.METHOD == 1:
        strategy = StrategyRandom()
    elif cfg.METHOD == 2:
        strategy = StrategyChainLength()
    else:
        raise ValueError('Неправильно задан номер стратегии.')
    cp.cprint(f'20Выбрана стратегия ^14_{strategy.name}')
    return strategy


def init_prisoners():
    return list([Prisoner(id=i) for i in range(1, cfg.NUMBER_OF_PRISONERS + 1)])


def init_boxes():
    numbers = list(range(1, cfg.NUMBER_OF_PRISONERS + 1))
    shuffle(numbers)
    return list([Box(id=i, number_on_paper=numbers[i-1]) for i in range(1, cfg.NUMBER_OF_PRISONERS + 1)])


def log_result(iteration, result, success_prisoners):
    if cfg.LOG_LEVEL < 1:
        return
    text_base = f'20Итерация ^15_{iteration + 1:>4}^20_, удачных заключённых ^14_{success_prisoners:>3}, '
    if result:
        cp.cprint(f'{text_base}^2_успех, заключённые на свободе')
    else:
        cp.cprint(f'{text_base}^4_неудача, заключённые казнены')


def log_total_result(total_success, total_fail):
    print('=' * WIDTH_CONSOL)
    cp.cprint(f'20Всего итераций ^15_{cfg.NUMBER_OF_ITERATIONS}')
    cp.cprint(f'20Успешно ^2_{total_success:>4}  ({(total_success / cfg.NUMBER_OF_ITERATIONS):.2%})')
    cp.cprint(f'20Провал  ^4_{total_fail:>4}  ({(total_fail / cfg.NUMBER_OF_ITERATIONS):.2%})')


def one_action_in_prison(prisoners, room):
    result = False
    success_prisoners = 0
    for prisoner in prisoners:
        if not room.prisoner_go(prisoner):
            break
        success_prisoners += 1
        room.close_all_boxes()
    else:
        result = True
    return result, success_prisoners


def iterations(prisoners, strategy):
    total_success = 0
    total_fail = 0
    for iteration in range(cfg.NUMBER_OF_ITERATIONS):
        room = Room(boxes=init_boxes(), strategy=strategy)
        result, success_prisoners = one_action_in_prison(prisoners, room)
        log_result(iteration, result, success_prisoners)
        if result:
            total_success += 1
        else:
            total_fail += 1
    return total_success, total_fail


def main() -> None:
    seed(1)
    prisoners = init_prisoners()
    # pprint(prisoners)
    strategy = get_strategy()
    total_success, total_fail = iterations(prisoners, strategy)
    log_total_result(total_success, total_fail)


if __name__ == '__main__':
    _width = 120
    _hight = 50
    os.system('color 71')
    # os.system('mode con cols=%d lines=%d' % (_width, _hight))

    cc.clear_consol()

    __author__ = 'master by Vint'
    __title__ = '--- 100PrisonerProblem ---'
    __copyright__ = 'Copyright 2022 (c)  bitbucket.org/Vintets'
    auth_sh.authorship(__author__, __title__, __version__, __copyright__)  # width=_width

    main()

    sys.exit(0)
