#!/usr/bin/env python
"""
bot.py - the main bot file
---
"""

import os

import telebot
import logging
from flask import Flask, request
from telebot.types import Update

import text
from config import DEFAULT_DATA, SCHEME
from scripts.date import calendar_kboard, calendar_worker
from scripts.keyboard import keyboard, keyboard_worker, unpack_data
from scripts.aeroexpress import aeroexpress_kboard, aeroexpress_worker

__author__ = 'Anthony Byuraev'


WEBHOOK_HOST = os.getenv('HOST')
WEBHOOK_LISTEN = '0.0.0.0'

TOKEN = os.getenv('TOKEN')

bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.from_user.id, text.MSG_START)


@bot.message_handler(commands=['help'])
def send_help(message):
    bot.send_message(message.from_user.id, text.MSG_HELP)


@bot.message_handler(commands=['search'])
def start_search(message):
    procedure = unpack_data(DEFAULT_DATA)
    bot.send_message(message.from_user.id, text.MSG_SEARCH,
                     reply_markup=keyboard(procedure))


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


if "HEROKU" in list(os.environ.keys()):
    logger = telebot.logger
    telebot.logger.setLevel(logging.INFO)
    server = Flask(__name__)

    @server.route("/" + TOKEN, methods=['POST'])
    def getMessage():
        bot.process_new_updates(
            [Update.de_json(request.stream.read().decode("utf-8"))]
        )
        return "!", 200

    @server.route("/")
    def webhook():
        bot.remove_webhook()
        bot.set_webhook(url=WEBHOOK_HOST + TOKEN)
        return "?", 200
    server.run(host=WEBHOOK_LISTEN, port=os.environ.get('PORT', 5000))
else:
    bot.remove_webhook()
    bot.polling(none_stop=True)
