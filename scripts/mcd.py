"""
mcd.py - script for 'mcd' command

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
from database import elka_db
from utils.parsing import schedule


CALLS = (
    'MCD_SEARCH',
    'MCD_DEPARTURE',
    'MCD_DESTINATION',
    'MCD_SCHEDULE',
)


def mcd_dir_kb(root: dict):
    """
    Builds direction keyboard with directions column and pages selection bar
    """
    callback = {
        'call': 'MCD_DEPARTURE',
        'acq': '1',
    }

    keyboard = InlineKeyboardMarkup()

    directions = elka_db.mcd.name_()
    directions_id = elka_db.mcd.id_()

    callback['dfrom'] = directions_id[0]
    mcd1_button = InlineKeyboardButton(
        text=directions[0],
        callback_data=utils.dumps(callback)
    )

    callback['dfrom'] = directions_id[1]
    mcd2_button = InlineKeyboardButton(
        text=directions[1],
        callback_data=utils.dumps(callback)
    )
    keyboard.add(mcd1_button)
    keyboard.add(mcd2_button)

    return keyboard


def station_kboard(root: dict, lines: int = 8):
    """
    Builds station keyboard with stations column and pages selection bar
    """
    cond_dep = root['call'] == 'MCD_DEPARTURE'
    cond_des = root['call'] == 'MCD_DESTINATION'

    if cond_dep:
        callback = {
            'call': 'MCD_DESTINATION',
            'dfrom': root.get('dfrom', '1'),
            'acq': '1',
        }
    elif cond_des:
        callback = {
            'call': 'MCD_SCHEDULE',
            'dfrom': root.get('dfrom', '1'),
            'sfrom': root.get('sfrom', '58708'),
            'acq': '1',
        }

    keyboard = InlineKeyboardMarkup()

    stations = elka_db.mcd_station.name_(root.get('dfrom', '1'))
    stations_id = elka_db.mcd_station.id_(root.get('dfrom', '1'))

    root['pages'] = ceil(len(stations) / lines)

    if root.get('page') == '':
        page = 0
    else:
        page = int(root.get('page', '0'))

    start = lines * page
    if lines * page + lines > len(stations):
        stop = len(stations)
    else:
        stop = lines * page + lines

    for i in range(start, stop):
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


def mcd_worker(bot: TeleBot, call: CallbackQuery) -> None:
    """
    Check for callback for this script
    """

    procedure = utils.loads(call.data)

    if procedure['call'] == 'MCD_SEARCH':
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=text.MSG_SEARCH,
            reply_markup=mcd_dir_kb(procedure)
        )
    elif procedure['call'] == 'MCD_DEPARTURE':
        if procedure['acq'] == '1':
            bot.answer_callback_query(call.id, 'Направление выбрано')
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text='Выбери станцию отправления:',
            reply_markup=station_kboard(procedure)
        )
    elif procedure['call'] == 'MCD_DESTINATION':
        if procedure['acq'] == '1':
            bot.answer_callback_query(call.id, 'Станция отправления выбрана')
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text='Выбери станцию назначения:',
            reply_markup=station_kboard(procedure)
        )
    elif procedure['call'] == 'MCD_SCHEDULE':
        if procedure['acq'] == '1':
            bot.answer_callback_query(call.id, 'Станция назначения выбрана')
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=schedule(procedure),
            reply_markup=schedule_kboard(procedure)
        )
