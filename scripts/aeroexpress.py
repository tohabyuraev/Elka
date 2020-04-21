"""
aeroexpress.py - special module for 'aeroexp' comand
---
"""

from telebot import TeleBot
from telebot.types import (InlineKeyboardMarkup, InlineKeyboardButton,
                           CallbackQuery)

__author__ = 'Anthony Byuraev'


KEY_LIST = ('call', 'dir', 'dep', 'des', 'page')
CALLS = ('AEROEXPRESS')


def aeroexpress_kboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    key_sheremetyevo = InlineKeyboardButton(
        text='В аэропорт Шереметьево',
        callback_data='AEROEXPRESS:Aeroexpress:28604:35804:'
    )
    keyboard.add(key_sheremetyevo)
    key_domodedovo = InlineKeyboardButton(
        text='В аэропорт Домодедово',
        callback_data='AEROEXPRESS:Aeroexpress:83511:87511:'
    )
    keyboard.add(key_domodedovo)
    key_vnukovo = InlineKeyboardButton(
        text='В аэропорт Внуково',
        callback_data='AEROEXPRESS:Aeroexpress:16503:77103:'
    )
    keyboard.add(key_vnukovo)
    return keyboard


def schedule_kboard(instructions: dict) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    schedule_link_button = InlineKeyboardButton(
        text='Расписание поездов\nAeroexpress',
        url=get_url(instructions)
    )
    keyboard.add(schedule_link_button)
    airport_link_button = InlineKeyboardButton(
        text='Сайт аэропорта',
        url=airport_url(instructions['des'])
    )
    keyboard.add(airport_link_button)
    return keyboard


def get_url(instructions: dict) -> str:
    return (
        'https://www.tutu.ru/rasp.php?st1={}&st2={}'
        .format(instructions['dep'], instructions['des'])
    )


def airport_url(station_code: str) -> str:
    if station_code == '35804':
        return 'https://www.svo.aero/ru/main'
    elif station_code == '87511':
        return 'https://www.dme.ru/'
    elif station_code == '77103':
        return 'http://www.vnukovo.ru/'


def aeroexpress_worker(bot: TeleBot, call: CallbackQuery) -> None:

    procedure = unpack_data(call.data)

    if procedure['call'] == 'AEROEXPRESS':
        bot.answer_callback_query(call.id, 'Направление выбрано')
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text='Держи расписание Aeroexpress\nи ссылку на сайт аэропорта',
            reply_markup=schedule_kboard(procedure)
        )


def unpack_data(data: str) -> dict:
    return dict(zip(KEY_LIST, data.split(':')))
