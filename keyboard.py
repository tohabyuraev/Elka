"""
keyboard.py - inline keyboards
---
"""

import json

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

__author__ = 'Anthony Byuraev'


MAX_LINES = 7


def keyboard(instructions: dict) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(row_width=1)
    if instructions['call'] == 'search':
        column, row = direction_col_row(instructions)
    else:
        column, row = station_col_row(instructions)
    keyboard.add(*column)
    keyboard.row(*row)
    return keyboard


def direction_col_row(instructions: dict):
    data = db_data()
    button_list = [
        InlineKeyboardButton(
            text=data[direction]['name'],
            callback_data=callback(instructions, direction))
        for direction in data.keys()
    ]
    column = split_list(button_list)
    button_column = column[int(instructions['page'])]
    button_row = [
            InlineKeyboardButton(
                text=page_number_text(instructions, i),
                callback_data=select_callback(instructions, i)
            )
            for i in range(1, len(column) + 1)
        ]
    return button_column, button_row


def station_col_row(instructions: dict):
    data = db_data(instructions['dir'])
    button_list = [
        InlineKeyboardButton(
            text=data[station]['name'],
            callback_data=callback(instructions, data[station]['code']))
        for station in data.keys()
    ]
    column = split_list(button_list)
    button_column = column[int(instructions['page'])]
    button_row = [
            InlineKeyboardButton(
                text=page_number_text(instructions, i),
                callback_data=select_callback(instructions, i)
            )
            for i in range(1, len(column) + 1)
        ]
    return button_column, button_row


def callback(instructions: dict, value) -> str:
    out = instructions.copy()
    if out['call'] == 'search':
        out['call'] = 'departure'
        out['dir'] = value
        out['page'] = '0'
    elif out['call'] == 'departure':
        out['call'] = 'destination'
        out['dep'] = value
    elif out['call'] == 'destination':
        out['call'] = 'schedule'
        out['des'] = value
    return pack_data(out)


def select_callback(instructions: dict, page_number: int) -> str:
    out = instructions.copy()
    out['page'] = page_number - 1
    return pack_data(out)


def db_data(direction=None) -> dict:
    if direction:
        with open('db/stations.json') as file:
            data = json.load(file)
        return data[direction]
    else:
        with open('db/directions.json') as file:
            data = json.load(file)
        return data


def pack_data(data: dict) -> str:
    return '{call}:{dir}:{dep}:{des}:{page}'.format(**data)


def split_list(argument: list) -> list:
    return [argument[i:i + MAX_LINES]
            for i in range(0, len(argument), MAX_LINES)]


def page_number_text(instructions: dict, page_number: int) -> str:
    if int(instructions['page']) == page_number - 1:
        return f'· {page_number} ·'
    else:
        return f'{page_number}'


def schedule_kboard(instructions: dict) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    update_button = InlineKeyboardButton(
        text='Обновить расписание',
        callback_data=pack_data(instructions)
    )
    keyboard.add(update_button)
    schedule_link_button = InlineKeyboardButton(
        text='Расписание на tutu.ru',
        url=get_url(instructions)
    )
    keyboard.add(schedule_link_button)
    return keyboard


def get_url(instructions: dict):
    return (
        'https://www.tutu.ru/rasp.php?st1={}&st2={}'
        .format(instructions['dep'], instructions['des'])
    )
