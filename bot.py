#!/usr/bin/env python
"""
bot.py - the main bot file
---
"""

import os
import logging

import telebot
from flask import Flask, request
from telebot.types import Update

import text
import util
from config import DEFAULT_DATA, SCHEME
from scripts.date import calendar_kboard, calendar_worker
from scripts.keyboard import direction_kboard, keyboard_worker
from scripts.aeroexpress import aeroexpress_kboard, aeroexpress_worker

__author__ = 'Anthony Byuraev'


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


@bot.message_handler(commands=['search'])
def start_search(message):
    procedure = util.loads(DEFAULT_DATA)
    bot.send_message(message.from_user.id, text.MSG_SEARCH,
                     reply_markup=direction_kboard(procedure))


@bot.message_handler(commands=['aeroexp'])
def aeroexpress_search(message):
    bot.send_message(message.from_user.id, text.MSG_AERO,
                     reply_markup=aeroexpress_kboard())


@bot.message_handler(commands=['scheme'])
def send_scheme(message):
    bot.send_document(message.from_user.id, SCHEME)


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
    keyboard_worker(bot, call)
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
