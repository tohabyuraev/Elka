'keyboard.py - inline keyboards'

from math import ceil

from telebot import TeleBot
from telebot.types import (InlineKeyboardMarkup,
                           InlineKeyboardButton,
                           CallbackQuery)

import text
import util
import scripts.database as database
from .parsing import schedule

__author__ = 'Anthony Byuraev'


def direction_kboard(root: dict, lines: int = 5):
    """
    Builds direction keyboard with directions column and pages selection bar:
        direction1
        direction2
        ...
        1 2 ...
    """

    callback = {'call': 'DEPARTURE', 'acq': '1'}
    callback['date'] = root.get('date', '')

    keyboard = InlineKeyboardMarkup()

    directions = database.get_directions_names()
    directions_id = database.get_directions_ids()

    root['pages'] = ceil(len(directions) / lines)  # not legal
    page = int(root.get('page', '0'))

    for i in range(lines * page, lines * page + lines):

        callback['dir'] = directions_id[i]

        keyboard.add(
            InlineKeyboardButton(
                directions[i], callback_data=util.dumps(callback)
            )
        )

    bar = select_bar(root)
    keyboard.row(*bar)

    return keyboard


def station_kboard(root: dict, lines: int = 8):
    """
    Builds station keyboard with stations column and pages selection bar:
        station1
        station2
        ...
        1 2 ...
    """

    if root['call'] == 'DEPARTURE':
        callback = {
            'call': 'DESTINATION',
            'dir': root.get('dir', '1'),
            'date': root.get('date', ''),
            'acq': '1'
        }
    elif root['call'] == 'DESTINATION':
        callback = {
            'call': 'SCHEDULE',
            'dir': root.get('dir', '1'),
            'dep': root.get('dep', '58708'),
            'date': root.get('date', ''),
            'acq': '1'
        }

    keyboard = InlineKeyboardMarkup()

    stations = database.get_stations_names(root.get('dir', '1'))
    stations_id = database.get_stations_ids(root.get('dir', '1'))

    root['pages'] = ceil(len(stations) / lines)

    if root.get('page') == '':
        page = 0
    else:
        page = int(root.get('page', '0'))

    for i in range(lines * page, lines * page + lines):

        if root['call'] == 'DEPARTURE':
            callback['dep'] = stations_id[i]
        elif root['call'] == 'DESTINATION':
            callback['des'] = stations_id[i]

        keyboard.add(
            InlineKeyboardButton(
                stations[i], callback_data=util.dumps(callback)
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
                f'· {i + 1} ·', callback_data=util.dumps(callback)
            )
            bar.append(button)
        else:
            callback = root.copy()
            callback['page'] = i
            callback['acq'] = '0'
            button = InlineKeyboardButton(
                f'{i + 1}', callback_data=util.dumps(callback)
            )
            bar.append(button)

    return bar


def schedule_kboard(root: dict) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    update_button = InlineKeyboardButton(
        'Обновить расписание',
        callback_data=util.dumps(root)
    )
    keyboard.add(update_button)
    reversed_button = InlineKeyboardButton(
        'В обратном направлении',
        callback_data=util.dumps(reversed_root(root))
    )
    keyboard.add(reversed_button)
    schedule_link_button = InlineKeyboardButton(
        'Расписание на tutu.ru',
        url=get_url(root)
    )
    keyboard.add(schedule_link_button)
    return keyboard


def get_url(root: dict) -> str:
    """
    Return web page URL with train schedule
    """
    return (
        'https://www.tutu.ru/rasp.php?st1={}&st2={}'
        .format(root['dep'], root['des'])
    )


def reversed_root(root: dict) -> dict:
    rev_root = root.copy()
    rev_root['dep'], rev_root['des'] = root['des'], root['dep']
    return rev_root


def keyboard_worker(bot: TeleBot, call: CallbackQuery) -> None:
    """
    Check for callback for this script
    """

    procedure = util.loads(call.data)

    if procedure['call'] == 'SEARCH':
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=text.MSG_SEARCH,
            reply_markup=direction_kboard(procedure)
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
