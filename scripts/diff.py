"""
diff.py - script for 'diff' command

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
    'DIRECTION_FROM',
    'STATION_FROM',
    'DIRECTION_TO',
    'STATION_TO',
    'DIFF_SCHEDULE',
)


def diff_dir_kb(root: dict, lines: int = 5):
    """
    Builds direction keyboard with directions column and pages selection bar
    """
    cond_dir_from = root['call'] == 'DIRECTION_FROM'
    cond_dir_to = root['call'] == 'DIRECTION_TO'

    if cond_dir_from:
        callback = {
            'call': 'STATION_FROM',
            'acq': '1',
        }
    elif cond_dir_to:
        callback = {
            'call': 'STATION_TO',
            'sfrom': root.get('sfrom', '58708'),
            'acq': '1',
        }

    keyboard = InlineKeyboardMarkup()

    directions = elka_db.direction.name_()
    directions_id = elka_db.direction.id_()

    root['pages'] = ceil(len(directions) / lines)  # not legal

    if root.get('page') == '':
        page = 0
    else:
        page = int(root.get('page', '0'))

    for i in range(lines * page, lines * page + lines):

        if cond_dir_from:
            callback['dfrom'] = directions_id[i]
        elif cond_dir_to:
            callback['dto'] = directions_id[i]

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
    cond_st_from = root['call'] == 'STATION_FROM'
    cond_st_to = root['call'] == 'STATION_TO'

    if cond_st_from:
        callback = {
            'call': 'DIRECTION_TO',
            'dfrom': root.get('dfrom', '1'),
            'acq': '1',
        }
    elif cond_st_to:
        callback = {
            'call': 'DIFF_SCHEDULE',
            'dfrom': root.get('dfrom', '1'),
            'sfrom': root.get('sfrom', '58708'),
            'dto': root.get('dto', '1'),
            'acq': '1',
        }

    keyboard = InlineKeyboardMarkup()

    if cond_st_from:
        stations = elka_db.station.name_(root.get('dfrom', '1'))
        stations_id = elka_db.station.id_(root.get('dfrom', '1'))
    elif cond_st_to:
        stations = elka_db.station.name_(root.get('dto', '1'))
        stations_id = elka_db.station.id_(root.get('dto', '1'))

    root['pages'] = ceil(len(stations) / lines)

    if root.get('page') == '':
        page = 0
    else:
        page = int(root.get('page', '0'))

    for i in range(lines * page, lines * page + lines):

        if cond_st_from:
            callback['sfrom'] = stations_id[i]
        elif cond_st_to:
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


def diff_worker(bot: TeleBot, call: CallbackQuery) -> None:
    """
    Check for callback for this script
    """

    procedure = utils.loads(call.data)

    if procedure['call'] == 'DIRECTION_FROM':
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=text.MSG_SEARCH,
            reply_markup=diff_dir_kb(procedure)
        )
    elif procedure['call'] == 'STATION_FROM':
        if procedure['acq'] == '1':
            bot.answer_callback_query(call.id, 'Направление выбрано')
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text='Выбери станцию отправления:',
            reply_markup=station_kboard(procedure)
        )
    elif procedure['call'] == 'DIRECTION_TO':
        if procedure['acq'] == '1':
            bot.answer_callback_query(call.id, 'Станция отправления выбрана')
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=text.MSG_SEARCH,
            reply_markup=diff_dir_kb(procedure)
        )
    elif procedure['call'] == 'STATION_TO':
        if procedure['acq'] == '1':
            bot.answer_callback_query(call.id, 'Направление выбрано')
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text='Выбери станцию отправления:',
            reply_markup=station_kboard(procedure)
        )
    elif procedure['call'] == 'DIFF_SCHEDULE':
        if procedure['acq'] == '1':
            bot.answer_callback_query(call.id, 'Станция назначения выбрана')
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=schedule(procedure),
            reply_markup=schedule_kboard(procedure)
        )
