'date.py - Inline keyboard for travel date selection'

import calendar
from datetime import datetime, timedelta

from telebot import TeleBot
from telebot.types import (InlineKeyboardButton,
                           InlineKeyboardMarkup,
                           CallbackQuery)

import text
from .keyboard import direction_kboard

__author__ = 'Anthony Byuraev'


MONTHS_ENG = (
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December"
)
MONTHS = (
    'Январь',
    'Февраль',
    'Март',
    'Апрель',
    'Май',
    'Июнь',
    'Июль',
    'Август',
    'Сентябрь',
    'Октябрь',
    'Ноябрь',
    'Декабрь'
)

DAYS_ENG = ("Su", "Mo", "Tu", "We", "Th", "Fr", "Sa")
DAYS = ("Вс", "Пн", "Вт", "Ср", "Чт", "Пт", "Сб")

KEY_LIST = ('call', 'year', 'month', 'day')
CALLS = (
    'IGNORE', 'MONTHS', 'MONTH', 'DAY',
    'PREVIOUS-MONTH', 'NEXT-MONTH', 'CANCEL'
)


def calendar_kboard(year: int = None, month: int = None):

    now = datetime.utcnow()
    if year is None:
        year = now.year
    if month is None:
        month = now.month

    data_ignore = callback("IGNORE", year, month)
    data_months = callback("MONTHS", year, month)

    keyboard = InlineKeyboardMarkup(row_width=7)
    keyboard.add(
        InlineKeyboardButton(
            MONTHS[month - 1] + " " + str(year), callback_data=data_months
        )
    )
    keyboard.add(
        *[InlineKeyboardButton(day, callback_data=data_ignore) for day in DAYS]
    )

    for week in calendar.monthcalendar(year, month):
        row = list()
        for day in week:
            if day == 0:
                row.append(
                    InlineKeyboardButton(" ", callback_data=data_ignore))
            elif (
                f"{now.day}.{now.month}.{now.year}"
                == f"{day}.{month}.{year}"
            ):
                row.append(
                    InlineKeyboardButton(
                        f"({day})",
                        callback_data=callback("DAY", year, month, day))
                )
            else:
                row.append(
                    InlineKeyboardButton(
                        str(day),
                        callback_data=callback("DAY", year, month, day),
                    )
                )
        keyboard.add(*row)

    keyboard.add(
        InlineKeyboardButton(
            "<", callback_data=callback("PREVIOUS-MONTH", year, month)
        ),
        InlineKeyboardButton(
            "Отмена", callback_data=callback("CANCEL", year, month)
        ),
        InlineKeyboardButton(
            ">", callback_data=callback("NEXT-MONTH", year, month)
        ),
    )

    return keyboard


def create_months_calendar(year: int = None):
    """
    Creates a calendar with month selection

    Parameters:
    -----------
    year: int

    Returns:
    --------
    keyboard: InlineKeyboardMarkup

    """

    if year is None:
        year = datetime.now().year

    keyboard = InlineKeyboardMarkup()

    for i, month in enumerate(zip(MONTHS[0::2], MONTHS[1::2])):
        keyboard.add(
            InlineKeyboardButton(
                month[0],
                callback_data=callback("MONTH", year, i + 1)
            ),
            InlineKeyboardButton(
                month[1],
                callback_data=callback("MONTH", year, (i + 1) * 2),
            ),
        )

    return keyboard


def calendar_worker(bot: TeleBot, call: CallbackQuery):
    """
    Creates a new calendar if the forward or backward button is pressed
    """

    procedure = unpack_data(call.data)

    if procedure['call'] in CALLS:
        year = procedure.get('year', '2020')
        month = procedure.get('month', '1')
        day = procedure.get('day', '1')
        current = datetime(int(year), int(month), 1)

    if procedure['call'] == "IGNORE":
        bot.answer_callback_query(callback_query_id=call.id)
        return False, None
    elif procedure['call'] == "DAY":
        date = f'{day}.{month}.{year}'
        callback_data = callback('SEARCH', 'DIR', 'DEP', 'DES', '0', '0', date)
        procedure = unpack_kb_data(callback_data)
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=text.MSG_SEARCH,
            reply_markup=direction_kboard(procedure)
        )
    elif procedure['call'] == "PREVIOUS-MONTH":
        preview_month = current - timedelta(days=1)
        bot.edit_message_text(
            text=call.message.text,
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=calendar_kboard(
                year=int(preview_month.year),
                month=int(preview_month.month)
            ),
        )
        return None
    elif procedure['call'] == "NEXT-MONTH":
        next_month = current + timedelta(days=31)
        bot.edit_message_text(
            text=call.message.text,
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=calendar_kboard(
                year=int(next_month.year),
                month=int(next_month.month)
            ),
        )
        return None
    elif procedure['call'] == "MONTHS":
        bot.edit_message_text(
            text=call.message.text,
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=create_months_calendar(year=current.year),
        )
        return None
    elif procedure['call'] == "MONTH":
        bot.edit_message_text(
            text=call.message.text,
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=calendar_kboard(year=int(year), month=int(month)),
        )
        return None
    elif procedure['call'] == "CANCEL":
        bot.delete_message(
            chat_id=call.message.chat.id, message_id=call.message.message_id
        )
        return "CANCEL", None


def callback(*args) -> str:
    arguments = map(str, args)
    callback_data = ':'.join(arguments)
    return callback_data


def unpack_data(data: str) -> dict:
    return dict(zip(KEY_LIST, data.split(':')))


def unpack_kb_data(data: str) -> dict:
    KEY_LIST_KB = ('call', 'dir', 'dep', 'des', 'page', 'pages', 'date')
    return dict(zip(KEY_LIST_KB, data.split(':')))
