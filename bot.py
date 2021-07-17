__author__ = 'Anthony Byuraev'

import os

import typing
import logging
import asyncio

from aiogram import Bot, types
from aiogram.utils import executor
from aiogram.dispatcher import Dispatcher

import text
import util
import config
from scripts.mcd import mcd_direction_kboard, mcd_worker
from scripts.search import search_table, search_worker
# from scripts.date import calendar_kboard, calendar_worker
from scripts.aeroexp import aeroexp_kboard, aeroexp_worker


TOKEN = os.getenv('TOKEN')

WEBHOOK_HOST = os.getenv('HOST')
WEBHOOK_PATH = f'/webhook/bot/{TOKEN}'
WEBHOOK_URL = f'{WEBHOOK_HOST}{WEBHOOK_PATH}'

WEBAPP_HOST = '0.0.0.0'
WEBAPP_PORT = os.environ.get('PORT')


class Call(typing.NamedTuple):
    DELETE = 'DELETE'
    CANCEL = 'CANCEL'
    IGNORE = 'IGNORE'


bot = Bot(TOKEN)
dispatcher = Dispatcher(bot)
logging.basicConfig(level=logging.INFO)


async def on_startup(dispatcher):
    await bot.set_webhook(WEBHOOK_URL)
    await bot.set_my_commands(config.COMMANDS)


@dispatcher.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.answer(text.START)


@dispatcher.message_handler(commands=['help'])
async def send_help(message: types.Message):
    await message.answer(text.HELP)


@dispatcher.message_handler(commands=['search'])
async def start_search(message: types.Message):
    procedure = await util.loads(config.DEFAULT_SEARCH)
    markup = await search_table(procedure)
    await message.answer(text.SEARCH, reply_markup=markup)


@dispatcher.message_handler(commands=['mcd'])
async def start_mcd(message: types.Message):
    procedure = await util.loads(config.DEFAULT_MCD)
    markup = await mcd_direction_kboard(procedure)
    await message.answer(text.MCD, reply_markup=markup)


# @dispatcher.message_handler(commands=['calendar'])
# async def send_calendar(message: types.Message):
#     await message.answer('Выбери дату', reply_markup=calendar_kboard())


@dispatcher.message_handler(commands=['aeroexp'])
async def aeroexpress_search(message: types.Message):
    procedure = await util.loads(config.DEFAULT_AEROEXP)
    markup = await aeroexp_kboard(procedure)
    await message.answer(text.AEROEXP, reply_markup=markup)


@dispatcher.message_handler(commands=['scheme'])
async def send_scheme(message: types.Message):
    await message.answer_document(config.SCHEME)


@dispatcher.message_handler(content_types=types.ContentTypes.TEXT)
async def send_text_message(message: types.Message):
    if message.text.upper() == 'ПРИВЕТ':
        await message.answer(text.HELLO)
    else:
        await message.answer(message.text)


@dispatcher.callback_query_handler()
async def callback_worker(call: types.CallbackQuery) -> None:
    procedure = await util.loads(call.data)

    if procedure['call'] in (Call.DELETE, Call.CANCEL):
        await call.message.delete()
    elif procedure['call'] == Call.IGNORE:
        return None
    await mcd_worker(call)
    await search_worker(call)
    await aeroexp_worker(call)
    return None


if __name__ == '__main__':
    executor.start_webhook(dispatcher=dispatcher, webhook_path=WEBHOOK_PATH,
                           on_startup=on_startup, skip_updates=True,
                           host=WEBAPP_HOST, port=WEBAPP_PORT,
    )