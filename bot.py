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
from config import DEFAULT_DATA, KEY_LIST
from keyboard import keyboard, schedule_kboard
from aeroexpress import aeroexpress_kboard, aeroexpress_schedule_kboard

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
    bot.send_message(
        message.from_user.id,
        text=text.MSG_AERO,
        reply_markup=aeroexpress_kboard()
    )


@bot.message_handler(content_types=['text'])
def send_text_message(message):
    if message.text.upper() == 'ПРИВЕТ':
        bot.send_message(message.from_user.id, text.MSG_HELLO)
    else:
        bot.send_message(message.from_user.id, message.text)


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    procedure = unpack_data(call.data)
    if procedure['call'] == 'search':
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=text.MSG_SEARCH,
            reply_markup=keyboard(procedure)
        )
    elif procedure['call'] == 'departure':
        bot.answer_callback_query(call.id, 'Направление выбрано')
        departure_keyboard = keyboard(procedure)
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text='Выбери станцию отправления:',
            reply_markup=departure_keyboard
        )
    elif procedure['call'] == 'destination':
        bot.answer_callback_query(call.id, 'Станция отправления выбрана')
        destination_keyboard = keyboard(procedure)
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text='Выбери станцию назначения:',
            reply_markup=destination_keyboard
        )
    elif procedure['call'] == 'schedule':
        bot.answer_callback_query(call.id, 'Станция назначения выбрана')
        schedule_keyboard = schedule_kboard(procedure)
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text='Держи расписание! Доброго пути)',
            reply_markup=schedule_keyboard
        )
    elif procedure['call'] == 'aeroexpress':
        bot.answer_callback_query(call.id, 'Направление выбрано')
        schedule_keyboard = aeroexpress_schedule_kboard(procedure)
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text='Держи расписание Aeroexpress\nи ссылку на сайт аэропорта',
            reply_markup=schedule_keyboard
        )


def unpack_data(callback: str) -> dict:
    instructions = dict(zip(KEY_LIST, callback.split(':')))
    return instructions


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
