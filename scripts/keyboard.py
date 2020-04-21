"""
keyboard.py - inline keyboards
---
"""

import json

from telebot import TeleBot
from telebot.types import (InlineKeyboardMarkup, InlineKeyboardButton,
                           CallbackQuery)

import text
from config import DIRECTION_DB, STATION_DB
from scripts.parsing import schedule_text

__author__ = 'Anthony Byuraev'

__all__ = ['keyboard', 'keyboard_worker']


KEY_LIST = ('call', 'dir', 'dep', 'des', 'page', 'date')
CALLS = ('SEARCH', 'DEPARTURE', 'DESTINATION', 'SCHEDULE')

MAX_LINES = 7


def keyboard(instructions: dict) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(row_width=1)
    if instructions['call'] == 'SEARCH':
        column, row = direction_kb(instructions)
    else:
        column, row = station_kb(instructions)
    keyboard.add(*column)
    keyboard.row(*row)
    return keyboard


def direction_kb(instructions: dict) -> (list, list):
    directions = db_data()
    button_list = [
        InlineKeyboardButton(
            directions[direction]['name'],
            callback_data=callback(instructions, direction))
        for direction in directions
    ]
    column = split_list(button_list)
    button_column = column[int(instructions['page'])]
    button_row = [
            InlineKeyboardButton(
                select_numbers(instructions, i),
                callback_data=select_callback(instructions, i)
            )
            for i in range(1, len(column) + 1)
        ]
    return button_column, button_row


def station_kb(instructions: dict) -> (list, list):
    stations = db_data(instructions['dir'])
    button_list = [
        InlineKeyboardButton(
            stations[station]['name'],
            callback_data=callback(instructions, stations[station]['code']))
        for station in stations
    ]
    column = split_list(button_list)
    button_column = column[int(instructions['page'])]
    button_row = [
            InlineKeyboardButton(
                select_numbers(instructions, i),
                callback_data=select_callback(instructions, i)
            )
            for i in range(1, len(column) + 1)
        ]
    return button_column, button_row


def callback(instructions: dict, value) -> str:
    out = instructions.copy()
    value = str(value)
    if instructions['call'] == 'SEARCH':
        out['call'] = 'DEPARTURE'
        out['dir'] = value
        out['page'] = '0'
    elif instructions['call'] == 'DEPARTURE':
        out['call'] = 'DESTINATION'
        out['dep'] = value
    elif instructions['call'] == 'DESTINATION':
        out['call'] = 'SCHEDULE'
        out['des'] = value
    return pack_data(out)


def select_callback(instructions: dict, page_number: int) -> str:
    out = instructions.copy()
    out['page'] = str(page_number - 1)
    return pack_data(out)


def db_data(direction: str = None) -> dict:
    """
    Load data from data base
    """

    if direction is not None:
        with open(STATION_DB) as db:
            data = json.load(db)
        return data[direction]
    else:
        with open(DIRECTION_DB) as db:
            data = json.load(db)
        return data


def pack_data(data: dict) -> str:
    """
    Pack values to string with sep = ':' from instructions dict
    """

    callback = [value for value in data.values()]
    return ':'.join(callback)


def split_list(argument: list) -> list:
    return [argument[i:i + MAX_LINES]
            for i in range(0, len(argument), MAX_LINES)]


def select_numbers(instructions: dict, page_number: int) -> str:
    if int(instructions['page']) == page_number - 1:
        return f'· {page_number} ·'
    else:
        return f'{page_number}'


def schedule_kboard(instructions: dict) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    update_button = InlineKeyboardButton(
        'Обновить расписание',
        callback_data=pack_data(instructions)
    )
    keyboard.add(update_button)
    reversed_button = InlineKeyboardButton(
        'В обратном направлении',
        callback_data=reversed_root(instructions)
    )
    keyboard.add(reversed_button)
    schedule_link_button = InlineKeyboardButton(
        'Расписание на tutu.ru',
        url=get_url(instructions)
    )
    keyboard.add(schedule_link_button)
    return keyboard


def get_url(instructions: dict) -> str:
    """
    Return web page URL with train schedule

    Powered by tutu.ru
    """
    return (
        'https://www.tutu.ru/rasp.php?st1={}&st2={}'
        .format(instructions['dep'], instructions['des'])
    )


def reversed_root(instructions: dict) -> str:
    out = instructions.copy()
    out['dep'], out['des'] = out['des'], out['dep']
    return pack_data(out)


def keyboard_worker(bot: TeleBot, call: CallbackQuery) -> None:
    """
    Check for callback for this script
    """

    procedure = unpack_data(call.data)

    if procedure['call'] == 'SEARCH':
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=text.MSG_SEARCH,
            reply_markup=keyboard(procedure)
        )
    elif procedure['call'] == 'DEPARTURE':
        bot.answer_callback_query(call.id, 'Направление выбрано')
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text='Выбери станцию отправления:',
            reply_markup=keyboard(procedure)
        )
    elif procedure['call'] == 'DESTINATION':
        bot.answer_callback_query(call.id, 'Станция отправления выбрана')
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text='Выбери станцию назначения:',
            reply_markup=keyboard(procedure)
        )
    elif procedure['call'] == 'SCHEDULE' and procedure['date'] == 'None':
        bot.answer_callback_query(call.id, 'Станция назначения выбрана')
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=schedule_text(procedure),
            reply_markup=schedule_kboard(procedure)
        )
    elif procedure['call'] == 'SCHEDULE' and procedure['date'] != 'None':
        bot.answer_callback_query(call.id, 'Станция назначения выбрана')
        bot.delete_message(
            chat_id=call.message.chat.id, message_id=call.message.message_id
        )
        URL = (
            'https://www.tutu.ru/rasp.php?st1={}&st2={}&date={}'
            .format(procedure['dep'], procedure['des'],
                    procedure['date'])
        )
        date_keyboard = InlineKeyboardMarkup()
        date_keyboard.add(
            InlineKeyboardButton(
                'Расписание на tutu.ru',
                url=URL
            )
        )
        bot.send_message(
            chat_id=call.message.chat.id,
            text='Держи расписание!',
            reply_markup=date_keyboard
        )


def unpack_data(data: str) -> dict:
    return dict(zip(KEY_LIST, data.split(':')))
