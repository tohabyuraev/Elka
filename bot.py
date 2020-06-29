#!/usr/bin/env python

__author__ = 'Anthony Byuraev'

import os
import logging

import telebot
from flask import Flask, request
from telebot.types import Update

import text
import utils
from config import DEFAULT_ONE, DEFAULT_DIFF, SCHEME
from scripts.one import one_dir_kb, one_worker
from scripts.diff import diff_dir_kb, diff_worker
from scripts.date import calendar_kboard, calendar_worker
from scripts.aeroexp import aeroexpress_kboard, aeroexpress_worker



WEBHOOK_HOST = str(os.getenv('HOST'))
WEBHOOK_PORT = int(os.environ.get('PORT', '8443'))
WEBHOOK_LISTEN = '0.0.0.0'

TOKEN = os.getenv('TOKEN')

server = Flask(__name__)

bot = telebot.TeleBot(TOKEN)

logger = telebot.logger
telebot.logger.setLevel(logging.INFO)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.from_user.id, text.MSG_START)


@bot.message_handler(commands=['help'])
def send_help(message):
    bot.send_message(message.from_user.id, text.MSG_HELP)


@bot.message_handler(commands=['scheme'])
def send_scheme(message):
    bot.send_document(message.from_user.id, SCHEME)


@bot.message_handler(commands=['one'])
def start_search_one(message):
    procedure = utils.loads(DEFAULT_ONE)
    bot.send_message(message.from_user.id, text.MSG_SEARCH,
                     reply_markup=one_dir_kb(procedure))


@bot.message_handler(commands=['diff'])
def start_search_diff(message):
    procedure = utils.loads(DEFAULT_DIFF)
    bot.send_message(message.from_user.id, text.MSG_SEARCH,
                     reply_markup=diff_dir_kb(procedure))


@bot.message_handler(commands=['aeroexp'])
def aeroexpress_search(message):
    bot.send_message(message.from_user.id, text.MSG_AERO,
                     reply_markup=aeroexpress_kboard())


@bot.message_handler(commands=['calendar'])
def send_calendar(message):
    bot.send_message(message.from_user.id, 'Выбери дату',
                     reply_markup=calendar_kboard())


@bot.message_handler(content_types=['text'])
def send_text_message(message):
    if message.text.upper() == 'ПРИВЕТ':
        bot.send_message(message.from_user.id, text.MSG_HELLO)
    else:
        bot.send_message(message.from_user.id, message.text)


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    procedure = utils.loads(call.data)
    if procedure['call'] in ('DELETE', 'CANCEL'):
        bot.delete_message(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id
        )
    one_worker(bot, call)
    diff_worker(bot, call)
    aeroexpress_worker(bot, call)
    calendar_worker(bot, call)


@server.route('/' + TOKEN, methods=['POST'])
def get_updates():
    bot.process_new_updates(
        [Update.de_json(request.stream.read().decode("utf-8"))]
    )
    return '!', 200


bot.remove_webhook()
bot.set_webhook(url=WEBHOOK_HOST + TOKEN)

if __name__ == "__main__":
    server.run(host=WEBHOOK_LISTEN, port=WEBHOOK_PORT)
