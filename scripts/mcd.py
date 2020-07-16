"""
mcd.py - script for 'mcd' command
"""

__author__ = 'Anthony Byuraev'

import typing
import logging
from math import ceil

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import CallbackQuery, ChatActions

import util
from data import conn
from text import MSG_MCD, MSG_SEARCH
from util import schedule, callback_builder
from scripts.search import schedule_kboard, get_selection_bar


class Call(typing.NamedTuple):
    DIR = 'DIR'
    TABLE = 'TABLE'
    MSTTO = 'MSTTO'
    MSTFROM = 'MSTFROM'
    CANCEL = 'CANCEL' # sys_command
    IGNORE = 'IGNORE' # sys_command
    DELETE = 'DELETE' # sys_command
    UPDATE = 'UPDATE' # skip to search_worker
    REVERSE = 'REVERSE' # skip to search_worker
    SCHEDULE = 'SCHEDULE' # skip to search_worker


class MarkupText(typing.NamedTuple):
    STTO = 'Станция назначения'
    STFROM = 'Станция отправления'
    MSTTO = 'Выбери станцию назначения'
    MSTFROM = 'Выбери станцию отправления'


callback_cancel = Call.CANCEL
callback_ignore = Call.IGNORE
callback_delete = Call.DELETE


async def mcd_table(root: typing.Dict[str, str]) -> InlineKeyboardMarkup:
    """
    Builds mcd search table keyboard
    """
    keyboard = InlineKeyboardMarkup(row_width=2)
    callback_to = await callback_builder(root, Call.MSTTO)
    callback_from = await callback_builder(root, Call.MSTFROM)
    callback_schedule = await callback_builder(root, Call.SCHEDULE)

    sto_field_is_completed = root.get('sto') not in (None, '')
    sfrom_field_is_completed = root.get('sfrom') not in (None, '')

    if sto_field_is_completed:
        station_to = conn.execute(
            'SELECT name FROM station WHERE id = ?', (root['sto'],)
        ).fetchone()['name']
    else:
        station_to = ' '
    if sfrom_field_is_completed:
        station_from = conn.execute(
            'SELECT name FROM station WHERE id = ?', (root['sfrom'],)
        ).fetchone()['name']
    else:
        station_from = ' '

    direction = conn.execute(
        'SELECT name FROM direction WHERE id = ?', (root['dir'],)
    ).fetchone()['name']
    callback_dir = await callback_builder(root, Call.DIR)
    keyboard.add(InlineKeyboardButton(direction, callback_data=callback_dir))

    keyboard.add(
        InlineKeyboardButton(MarkupText.STFROM, callback_data=callback_ignore),
        InlineKeyboardButton(MarkupText.STTO, callback_data=callback_ignore),
        InlineKeyboardButton(station_from, callback_data=callback_from),
        InlineKeyboardButton(station_to, callback_data=callback_to),
    )
    if sfrom_field_is_completed and sto_field_is_completed:
        keyboard.add(
            InlineKeyboardButton(
                'Показать расписание', callback_data=callback_schedule
            )
        )
    keyboard.add(InlineKeyboardButton('Отмена', callback_data=callback_cancel))
    return keyboard


async def mcd_direction_kboard(root: typing.Dict[str, str]) -> InlineKeyboardMarkup:
    """
    Builds direction keyboard with directions column
    """
    keyboard = InlineKeyboardMarkup(row_width=2)
    id_list = [
        item['id']
        for item in conn.execute('SELECT id FROM direction WHERE id > 10').fetchall()
    ]
    name_list = [
        item['name']
        for item in conn.execute('SELECT name FROM direction WHERE id > 10').fetchall()
    ]
    callback_list = [
        await callback_builder(root, Call.TABLE, dir=id, sfrom='', sto='', page=0)
        for id in id_list
    ]
    buttons = [
        InlineKeyboardButton(name, callback_data=callback)
        for name, callback in zip(name_list, callback_list)
    ]
    keyboard.add(*buttons)
    keyboard.add(InlineKeyboardButton('Отмена', callback_data=callback_cancel))
    return keyboard


async def mcd_station_kboard(root: typing.Dict[str, str],
                             lines: int = 14) -> InlineKeyboardMarkup:
    """
    Builds station keyboard with stations column and pages selection bar
    """
    keyboard = InlineKeyboardMarkup(row_width=2)
    id_list = [
        item['id']
        for item in conn.execute(
            'SELECT id FROM station WHERE mcdid = ?', (root['dir'],)
        ).fetchall()
    ]
    name_list = [
        item['name']
        for item in conn.execute(
            'SELECT name FROM station WHERE mcdid = ?', (root['dir'],)
        ).fetchall()
    ]
    if root['call'] == Call.MSTFROM:
        callback_list = [
            await callback_builder(root, Call.TABLE, sfrom=id)
            for id in id_list
        ]
    elif root['call'] == Call.MSTTO:
        callback_list = [
            await callback_builder(root, Call.TABLE, sto=id)
            for id in id_list
        ]
    buttons = [
        InlineKeyboardButton(name, callback_data=callback)
        for name, callback in zip(name_list, callback_list)
    ]

    pages = ceil(id_list.__len__() / lines)
    if root.get('page') in (None, ''):
        page = 0
    else:
        page = int(root['page'])
    selection_bar = await get_selection_bar(root, page, pages)

    keyboard.add(*buttons[page * lines : page * lines + lines])
    keyboard.row(*selection_bar)
    keyboard.add(InlineKeyboardButton('Отмена', callback_data=callback_cancel))
    return keyboard


async def mcd_worker(call: CallbackQuery) -> None:
    """
    Check for callback for this script
    """
    procedure = await util.loads(call.data)

    if procedure['call'] == Call.DIR:
        text = MSG_MCD
        markup = await mcd_direction_kboard(procedure)
        await call.message.edit_text(text, reply_markup=markup)
        return None
    
    elif procedure['call'] == Call.TABLE:
        text = MSG_SEARCH
        markup = await mcd_table(procedure)
        await call.message.edit_text(text, reply_markup=markup)
        return None

    elif procedure['call'] == Call.MSTFROM:
        text = MarkupText.MSTFROM
        markup = await mcd_station_kboard(procedure)
        await call.message.edit_text(text, reply_markup=markup)
        return None

    elif procedure['call'] == Call.MSTTO:
        text = MarkupText.MSTTO
        markup = await mcd_station_kboard(procedure)
        await call.message.edit_text(text, reply_markup=markup)
        return None
