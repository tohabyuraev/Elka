__author__ = 'Anthony Byuraev'

import typing
import random
import logging
from enum import Enum
from math import ceil

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import CallbackQuery, ChatActions

import util
from data import conn
from util import schedule, callback_builder


class Call(typing.NamedTuple):
    STTO = 'STTO'
    DIRTO = 'DIRTO'
    STFROM = 'STFROM'
    SEARCH = 'SEARCH'
    DIRFROM = 'DIRFROM'
    IGNORE = 'IGNORE' # sys_command
    CANCEL = 'CANCEL' # sys_command
    DELETE = 'DELETE' # sys_command
    UPDATE = 'UPDATE'
    REVERSE = 'REVERSE'
    SCHEDULE = 'SCHEDULE'


class MarkupText(typing.NamedTuple):
    STTO = 'Станция назначения'
    STFROM = 'Станция отправления'


callback_cancel = Call.CANCEL
callback_ignore = Call.IGNORE
callback_delete = Call.DELETE


async def search_table(root: typing.Dict[str, str]) -> InlineKeyboardMarkup:
    """
    Builds search table keyboard
    """
    keyboard = InlineKeyboardMarkup(row_width=2)
    callback_to = await callback_builder(root, Call.DIRTO)
    callback_from = await callback_builder(root, Call.DIRFROM)
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


async def direction_kboard(root: typing.Dict[str, str]) -> InlineKeyboardMarkup:
    """
    Builds direction keyboard with two direction columns
    """
    keyboard = InlineKeyboardMarkup(row_width=2)
    if root['call'] == Call.DIRFROM:
        call = Call.STFROM
    elif root['call'] == Call.DIRTO:
        call = Call.STTO

    id_list = [
        item['id']
        for item in conn.execute('SELECT id FROM direction WHERE id < 11').fetchall()
    ]
    name_list = [
        item['name']
        for item in conn.execute('SELECT name FROM direction WHERE id < 11').fetchall()
    ]
    callback_list = [
        await callback_builder(root, call, dir=id, page=0)
        for id in id_list
    ]
    buttons = [
        InlineKeyboardButton(name, callback_data=callback)
        for name, callback in zip(name_list, callback_list)
    ]
    keyboard.add(*buttons)
    keyboard.add(InlineKeyboardButton('Отмена', callback_data=callback_cancel))
    return keyboard


async def station_kboard(root: typing.Dict[str, str],
                         lines: int = 14) -> InlineKeyboardMarkup:
    """
    Builds station keyboard with stations column and pages selection bar
    """
    keyboard = InlineKeyboardMarkup(row_width=2)
    direction = conn.execute(
        'SELECT name FROM direction WHERE id = ?', (root['dir'],)
    ).fetchone()['name']
    if root['call'] == Call.STFROM:
        callback_dir = await callback_builder(root, Call.DIRFROM)
    elif root['call'] == Call.STTO:
        callback_dir = await callback_builder(root, Call.DIRTO)
    keyboard.add(InlineKeyboardButton(direction, callback_data=callback_dir))

    id_list = [
        item['id']
        for item in conn.execute(
            'SELECT id FROM station WHERE dirid = ?', (root['dir'],)
        ).fetchall()
    ]
    name_list = [
        item['name']
        for item in conn.execute(
            'SELECT name FROM station WHERE dirid = ?', (root['dir'],)
        ).fetchall()
    ]
    if root['call'] == Call.STFROM:
        callback_list = [
            await callback_builder(root, Call.SEARCH, sfrom=id)
            for id in id_list
        ]
    elif root['call'] == Call.STTO:
        callback_list = [
            await callback_builder(root, Call.SEARCH, sto=id)
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


async def get_selection_bar(root: typing.Dict[str, str],
                            page: int,
                            pages: int) -> typing.List[InlineKeyboardButton]:
    name_list = [
        await is_current_page(iter_page, page)
        for iter_page in range(pages)
    ]
    callback_list = [
        await callback_builder(root, root['call'], page=iter_page)
        for iter_page in range(pages)
    ]
    buttons = [
        InlineKeyboardButton(name, callback_data=callback)
        for name, callback in zip(name_list, callback_list)
    ]
    return buttons


async def is_current_page(iter_page, root_page):
    if root_page == iter_page:
        return f'· {iter_page + 1} ·'
    else:
        return f'{iter_page + 1}'


async def schedule_kboard(root: typing.Dict[str, str]) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(row_width=2)
    callback_update = await callback_builder(
        root, Call.UPDATE,
        dir=random.randint(1, 10)
    )
    update_button = InlineKeyboardButton(
        'Обновить',
        callback_data=callback_update
    )
    callback_reverse = await callback_builder(
        root, Call.REVERSE,
        sfrom=root['sto'], sto=root['sfrom']
    )
    reversed_button = InlineKeyboardButton(
        'В обратном направлении',
        callback_data=callback_reverse
    )
    remove_button = InlineKeyboardButton(
        'Удалить',
        callback_data=callback_delete
    )
    keyboard.add(reversed_button)
    keyboard.add(update_button, remove_button)
    return keyboard


async def search_worker(call: CallbackQuery) -> None:
    """
    Check for callback for this script
    """
    procedure = await util.loads(call.data)

    if procedure['call'] == Call.SEARCH:
        markup = await search_table(procedure)
        await call.message.edit_reply_markup(markup)
        return None

    elif procedure['call'] in (Call.DIRFROM, Call.DIRTO):
        markup = await direction_kboard(procedure)
        await call.message.edit_reply_markup(markup)
        return None

    elif procedure['call'] in (Call.STFROM, Call.STTO):
        markup = await station_kboard(procedure)
        await call.message.edit_reply_markup(markup)
        return None

    elif procedure['call'] == Call.SCHEDULE:
        await ChatActions.typing()
        text = await schedule(procedure)
        markup = await schedule_kboard(procedure)
        await call.message.answer(text, reply_markup=markup)
        return None

    elif procedure['call'] in (Call.UPDATE, Call.REVERSE):
        await ChatActions.typing()
        text = await schedule(procedure)
        markup = await schedule_kboard(procedure)
        await call.message.edit_text(text, reply_markup=markup)
        return None
