"""
aeroexpress.py - Special module for 'aeroexp' comand
---
"""

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from keyboard import get_url

__author__ = 'Anthony Byuraev'


def aeroexpress_kboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    key_sheremetyevo = InlineKeyboardButton(
        text='В аэропорт Шереметьево',
        callback_data='aeroexpress:Aeroexpress:28604:35804::'
    )
    keyboard.add(key_sheremetyevo)
    key_domodedovo = InlineKeyboardButton(
        text='В аэропорт Домодедово',
        callback_data='aeroexpress:Aeroexpress:83511:87511::'
    )
    keyboard.add(key_domodedovo)
    key_vnukovo = InlineKeyboardButton(
        text='В аэропорт Внуково',
        callback_data='aeroexpress:Aeroexpress:16503:77103::'
    )
    keyboard.add(key_vnukovo)
    return keyboard


def aeroexpress_schedule_kboard(instructions: dict) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    schedule_link_button = InlineKeyboardButton(
        text='Расписание поездов\nAeroexpress',
        url=get_url(instructions)
    )
    keyboard.add(schedule_link_button)
    special_info_button = InlineKeyboardButton(
        text='Сайт аэропорта',
        url=airport_url(instructions['des'])
    )
    keyboard.add(special_info_button)
    return keyboard


def airport_url(station_code: str) -> str:
    if station_code == '35804':
        return 'https://www.svo.aero/ru/main'
    elif station_code == '87511':
        return 'https://www.dme.ru/'
    elif station_code == '77103':
        return 'http://www.vnukovo.ru/'
