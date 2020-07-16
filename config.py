"""
config.py - set bot configuration
"""

__author__ = 'Anthony Byuraev'

from aiogram.types import BotCommand


KEYS = ('call', 'dir', 'sfrom', 'sto', 'page', 'date')

DEFAULT_MCD = 'DIR'
DEFAULT_SEARCH = 'SEARCH'
DEFAULT_AEROEXP = 'AEROEXP'

SCHEME = 'BQACAgQAAxkDAAIGNF8QlXZ76NGg0nZ7cggTkt_Ny4lPAAI5AgACZU-MUFKldvsvF0dIGgQ'

COMMANDS = [
    BotCommand('help', 'подробнее о командах'),
    BotCommand('search', 'расписание электричек'),
    BotCommand('mcd', 'расписание поездов МЦД'),
    BotCommand('aeroexp', 'расписание Aeroexpress'),
    BotCommand('scheme', 'схема пригородного сообщения'),
]
