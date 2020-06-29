"""
one.py - script for 'one' command

Direction keyboard example:
first  direction
second direction
................
page1      page2

Station keyboard example:
first  station
second station
..............
page1....page7
"""

__author__ = 'Anthony Byuraev'

from math import ceil

from telebot import TeleBot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from telebot.types import CallbackQuery

import text
import utils
from database import database
from utils.parsing import schedule


CALLS = (
    'SEARCH',
    'DEPARTURE',
    'DESTINATION',
    'SCHEDULE',
)


def one_dir_kb(root: dict, lines: int = 5):
    """
    Builds direction keyboard with directions column and pages selection bar
    """

    callback = {
        'call': 'DEPARTURE',
        'acq': '1',
    }
    callback['date'] = root.get('date', '')

    keyboard = InlineKeyboardMarkup()

    directions = database.get_directions_names()
    directions_id = database.get_directions_ids()

    root['pages'] = ceil(len(directions) / lines)  # not legal
    page = int(root.get('page', '0'))

    for i in range(lines * page, lines * page + lines):

        callback['dfrom'] = directions_id[i]

        keyboard.add(
            InlineKeyboardButton(
                directions[i], callback_data=utils.dumps(callback)
            )
        )

    bar = select_bar(root)
    keyboard.row(*bar)

    return keyboard


def station_kboard(root: dict, lines: int = 8):
    """
    Builds station keyboard with stations column and pages selection bar
    """
    cond_dep = root['call'] == 'DEPARTURE'
    cond_des = root['call'] == 'DESTINATION'

    if cond_dep:
        callback = {
            'call': 'DESTINATION',
            'dfrom': root.get('dfrom', '1'),
            'date': root.get('date', ''),
            'acq': '1',
        }
    elif cond_des:
        callback = {
            'call': 'SCHEDULE',
            'dfrom': root.get('dfrom', '1'),
            'sfrom': root.get('sfrom', '58708'),
            'date': root.get('date', ''),
            'acq': '1',
        }

    keyboard = InlineKeyboardMarkup()

    stations = database.get_stations_names(root.get('dfrom', '1'))
    stations_id = database.get_stations_ids(root.get('dfrom', '1'))

    root['pages'] = ceil(len(stations) / lines)

    if root.get('page') == '':
        page = 0
    else:
        page = int(root.get('page', '0'))

    for i in range(lines * page, lines * page + lines):

        if cond_dep:
            callback['sfrom'] = stations_id[i]
        elif cond_des:
            callback['sto'] = stations_id[i]

        keyboard.add(
            InlineKeyboardButton(
                stations[i], callback_data=utils.dumps(callback)
            )
        )

    bar = select_bar(root)
    keyboard.row(*bar)

    return keyboard


def select_bar(root: dict) -> [InlineKeyboardButton, ...]:
    pages = int(root.get('pages', '1'))
    if root.get('page') == '':
        page = 0
    else:
        page = int(root.get('page', '0'))

    bar = []

    for i in range(pages):
        if page == i:
            callback = root.copy()
            callback['page'] = i
            callback['acq'] = '0'
            button = InlineKeyboardButton(
                f'· {i + 1} ·', callback_data=utils.dumps(callback)
            )
            bar.append(button)
        else:
            callback = root.copy()
            callback['page'] = i
            callback['acq'] = '0'
            button = InlineKeyboardButton(
                f'{i + 1}', callback_data=utils.dumps(callback)
            )
            bar.append(button)

    return bar


def schedule_kboard(root: dict) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    update_button = InlineKeyboardButton(
        'Обновить расписание',
        callback_data=utils.dumps(root)
    )
    keyboard.add(update_button)
    reversed_button = InlineKeyboardButton(
        'В обратном направлении',
        callback_data=utils.dumps(reversed_root(root))
    )
    keyboard.add(reversed_button)
    remove_button = InlineKeyboardButton(
        'Удалить расписание',
        callback_data=utils.dumps({'call': 'DELETE'})
    )
    keyboard.add(remove_button)
    return keyboard


def get_url(root: dict) -> str:
    """
    Return web page URL with train schedule
    """
    return (
        'https://www.tutu.ru/rasp.php?st1={}&st2={}'
        .format(root['sfrom'], root['sto'])
    )


def reversed_root(root: dict) -> dict:
    rev_root = root.copy()
    rev_root['sfrom'], rev_root['sto'] = root['sto'], root['sfrom']
    return rev_root


def one_worker(bot: TeleBot, call: CallbackQuery) -> None:
    """
    Check for callback for this script
    """

    procedure = utils.loads(call.data)

    if procedure['call'] == 'SEARCH':
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=text.MSG_SEARCH,
            reply_markup=one_dir_kb(procedure)
        )
    elif procedure['call'] == 'DEPARTURE':
        if procedure['acq'] == '1':
            bot.answer_callback_query(call.id, 'Направление выбрано')
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text='Выбери станцию отправления:',
            reply_markup=station_kboard(procedure)
        )
    elif procedure['call'] == 'DESTINATION':
        if procedure['acq'] == '1':
            bot.answer_callback_query(call.id, 'Станция отправления выбрана')
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text='Выбери станцию назначения:',
            reply_markup=station_kboard(procedure)
        )
    elif procedure['call'] == 'SCHEDULE' and procedure['date'] == '':
        if procedure['acq'] == '1':
            bot.answer_callback_query(call.id, 'Станция назначения выбрана')
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=schedule(procedure),
            reply_markup=schedule_kboard(procedure)
        )
    elif procedure['call'] == 'SCHEDULE' and procedure['date'] != '':
        if procedure['acq'] == '1':
            bot.answer_callback_query(call.id, 'Станция назначения выбрана')
        bot.delete_message(
            chat_id=call.message.chat.id, message_id=call.message.message_id
        )
        URL = (
            'https://www.tutu.ru/rasp.php?st1={}&st2={}&date={}'
            .format(procedure['sfrom'], procedure['sto'],
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
