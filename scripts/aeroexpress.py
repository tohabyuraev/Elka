'aeroexpress.py - special module for "aeroexp" command'

from telebot import TeleBot
from telebot.types import (InlineKeyboardMarkup,
                           InlineKeyboardButton,
                           CallbackQuery)

import util

__author__ = 'Anthony Byuraev'


def aeroexpress_kboard() -> InlineKeyboardMarkup:

    keyboard = InlineKeyboardMarkup()

    callback = {
        'call': 'AEROEXPRESS', 'dep': '28604', 'des': '35804', 'acq': '1'}
    key_sheremetyevo = InlineKeyboardButton(
        text='В аэропорт Шереметьево',
        callback_data=util.dumps(callback)
    )
    keyboard.add(key_sheremetyevo)

    callback = {
        'call': 'AEROEXPRESS', 'dep': '83511', 'des': '87511', 'acq': '1'}
    key_domodedovo = InlineKeyboardButton(
        text='В аэропорт Домодедово',
        callback_data=util.dumps(callback)
    )
    keyboard.add(key_domodedovo)

    callback = {
        'call': 'AEROEXPRESS', 'dep': '16503', 'des': '77103', 'acq': '1'}
    key_vnukovo = InlineKeyboardButton(
        text='В аэропорт Внуково',
        callback_data=util.dumps(callback)
    )
    keyboard.add(key_vnukovo)

    return keyboard


def schedule_kboard(root: dict) -> InlineKeyboardMarkup:

    keyboard = InlineKeyboardMarkup()

    schedule_link_button = InlineKeyboardButton(
        text='Расписание поездов\nAeroexpress',
        url=schedule_url(root)
    )
    keyboard.add(schedule_link_button)

    airport_link_button = InlineKeyboardButton(
        text='Сайт аэропорта',
        url=airport_url(root['des'])
    )
    keyboard.add(airport_link_button)

    return keyboard


def schedule_url(root: dict) -> str:
    return (
        'https://www.tutu.ru/rasp.php?st1={}&st2={}'
        .format(root['dep'], root['des'])
    )


def airport_url(station_code: str) -> str:
    if station_code == '35804':
        return 'https://www.svo.aero/ru/main'
    elif station_code == '87511':
        return 'https://www.dme.ru/'
    elif station_code == '77103':
        return 'http://www.vnukovo.ru/'


def aeroexpress_worker(bot: TeleBot, call: CallbackQuery):

    procedure = util.loads(call.data)

    if procedure['call'] == 'AEROEXPRESS':
        if procedure['acq'] == '1':
            bot.answer_callback_query(call.id, 'Поиск начался')
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text='Держи расписание Aeroexpress\nи ссылку на сайт аэропорта',
            reply_markup=schedule_kboard(procedure)
        )
