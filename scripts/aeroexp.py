"""
aeroexpress.py - special module for "aeroexp" command
"""

__author__ = 'Anthony Byuraev'

import typing
import logging

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import CallbackQuery, ChatActions

import util
from util import schedule, callback_builder
from scripts.search import schedule_kboard


class Call(typing.NamedTuple):
    SVODOWN = 'SVODOWN'
    DMEDOWN = 'DMEDOWN'
    VNODOWN = 'VNODOWN'
    SVOLINK = 'SVOLINK'
    DMELINK = 'DMELINK'
    VNOLINK = 'VNOLINK'
    AEROEXP = 'AEROEXP'
    CANCEL = 'CANCEL' # sys_command
    UPDATE = 'UPDATE' # skip to search_worker
    REVERSE = 'REVERSE' # skip to search_worker
    SCHEDULE = 'SCHEDULE' # skip to search_worker


class MarkupText(typing.NamedTuple):
    TO_AIRPORT = 'В аэропорт'
    FROM_AIRPORT = 'Из аэропорта'


callback_cancel = Call.CANCEL


async def aeroexp_kboard(root: typing.Dict[str, str]) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(row_width=2)
    callback_svo = await callback_builder(
        root, Call.SVODOWN, sfrom='28604', sto='35804'
    )
    key_sheremetyevo = InlineKeyboardButton(
        text='Аэропорт Шереметьево',
        callback_data=callback_svo
    )
    keyboard.add(key_sheremetyevo)
    if root['call'] == Call.SVODOWN:
        callback_to = await callback_builder(root, Call.SVOLINK)
        callback_from = await callback_builder(
            root, Call.SVOLINK, sfrom='35804', sto='28604'
        )
        keyboard.add(
            InlineKeyboardButton(MarkupText.TO_AIRPORT, callback_data=callback_to),
            InlineKeyboardButton(MarkupText.FROM_AIRPORT, callback_data=callback_from),
        )
    callback_dme = await callback_builder(
        root, Call.DMEDOWN, sfrom='83511', sto='87511'
    )
    key_domodedovo = InlineKeyboardButton(
        text='Аэропорт Домодедово',
        callback_data=callback_dme
    )
    keyboard.add(key_domodedovo)
    if root['call'] == Call.DMEDOWN:
        callback_to = await callback_builder(root, Call.DMELINK)
        callback_from = await callback_builder(
            root, Call.DMELINK, sfrom='87511', sto='83511'
        )
        keyboard.add(
            InlineKeyboardButton(MarkupText.TO_AIRPORT, callback_data=callback_to),
            InlineKeyboardButton(MarkupText.FROM_AIRPORT, callback_data=callback_from),
        )
    callback_vno = await callback_builder(
        root, Call.VNODOWN, sfrom='16503', sto='77103'
    )
    key_vnukovo = InlineKeyboardButton(
        text='Аэропорт Внуково',
        callback_data=callback_vno
    )
    keyboard.add(key_vnukovo)
    if root['call'] == Call.VNODOWN:
        callback_to = await callback_builder(root, Call.VNOLINK)
        callback_from = await callback_builder(
            root, Call.VNOLINK, sfrom='77103', sto='16503'
        )
        keyboard.add(
            InlineKeyboardButton(MarkupText.TO_AIRPORT, callback_data=callback_to),
            InlineKeyboardButton(MarkupText.FROM_AIRPORT, callback_data=callback_from),
        )
    keyboard.add(InlineKeyboardButton('Отмена', callback_data=callback_cancel))
    return keyboard


async def airport_kboard(root: typing.Dict[str, str]) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    if root['call'] == Call.SVOLINK:
        keyboard.add(
            InlineKeyboardButton(
                'Аэропорт Шереметьево',
                url='https://www.svo.aero/ru/main'
            )
        )
    elif root['call'] == Call.DMELINK:
        keyboard.add(
            InlineKeyboardButton(
                'Аэропорт Домодедово',
                url='https://www.dme.ru/'
            )
        )
    elif root['call'] == Call.VNOLINK:
        keyboard.add(
            InlineKeyboardButton(
                'Аэропорт Внуково',
                url='http://www.vnukovo.ru/'
            )
        )
    return keyboard


async def aeroexp_worker(call: CallbackQuery) -> None:
    procedure = await util.loads(call.data)

    if procedure['call'] == Call.AEROEXP:
        markup = await aeroexp_kboard(procedure)
        await call.message.edit_reply_markup(markup)
        return None
    
    elif procedure['call'] in (Call.SVODOWN, Call.DMEDOWN, Call.VNODOWN):
        markup = await aeroexp_kboard(procedure)
        await call.message.edit_reply_markup(markup)
        return None
    
    elif procedure['call'] in (Call.SVOLINK, Call.DMELINK, Call.VNOLINK):
        markup = await airport_kboard(procedure)
        await call.message.edit_reply_markup(markup)

        await ChatActions.typing()
        text = await schedule(procedure)
        markup = await schedule_kboard(procedure)
        await call.message.answer(text, reply_markup=markup)
        return None
