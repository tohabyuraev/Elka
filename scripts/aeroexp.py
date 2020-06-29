'aeroexpress.py - special module for "aeroexp" command'

__author__ = 'Anthony Byuraev'

from telebot import TeleBot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from telebot.types import CallbackQuery

import utils


CALLS = (
    'AEROEXPRESS',
)


def aeroexpress_kboard() -> InlineKeyboardMarkup:

    keyboard = InlineKeyboardMarkup()

    callback = {
        'call': 'AEROEXPRESS', 'sfrom': '28604', 'sto': '35804', 'acq': '1'}
    key_sheremetyevo = InlineKeyboardButton(
        text='В аэропорт Шереметьево',
        callback_data=utils.dumps(callback)
    )
    keyboard.add(key_sheremetyevo)

    callback = {
        'call': 'AEROEXPRESS', 'sfrom': '83511', 'sto': '87511', 'acq': '1'}
    key_domodedovo = InlineKeyboardButton(
        text='В аэропорт Домодедово',
        callback_data=utils.dumps(callback)
    )
    keyboard.add(key_domodedovo)

    callback = {
        'call': 'AEROEXPRESS', 'sfrom': '16503', 'sto': '77103', 'acq': '1'}
    key_vnukovo = InlineKeyboardButton(
        text='В аэропорт Внуково',
        callback_data=utils.dumps(callback)
    )
    keyboard.add(key_vnukovo)

    callback = {
        'call': 'CANCEL'
    }
    remove_button = InlineKeyboardButton(
        text='Отмена',
        callback_data=utils.dumps(callback)
    )
    keyboard.add(remove_button)

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
        url=airport_url(root['sto'])
    )
    keyboard.add(airport_link_button)

    return keyboard


def schedule_url(root: dict) -> str:
    return (
        'https://www.tutu.ru/rasp.php?st1={}&st2={}'
        .format(root['sfrom'], root['sto'])
    )


def airport_url(station_code: str) -> str:
    if station_code == '35804':
        return 'https://www.svo.aero/ru/main'
    elif station_code == '87511':
        return 'https://www.dme.ru/'
    elif station_code == '77103':
        return 'http://www.vnukovo.ru/'


def aeroexpress_worker(bot: TeleBot, call: CallbackQuery):

    procedure = utils.loads(call.data)

    if procedure['call'] == 'AEROEXPRESS':
        if procedure['acq'] == '1':
            bot.answer_callback_query(call.id, 'Поиск начался')
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text='Держи расписание Aeroexpress\nи ссылку на сайт аэропорта',
            reply_markup=schedule_kboard(procedure)
        )
