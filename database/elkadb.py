__author__ = 'Anthony Byuraev'

import re
import sqlite3


DATABASE = 'database/elka.db'


class Table(object):
    def __init__(self, name: str):
        self.name = name

    def id_(self, directid=None):
        if directid is None:
            SELECT = f'SELECT id FROM {self.name}'
        else:
            SELECT = f'SELECT id FROM {self.name} WHERE directid = {directid}'

        with sqlite3.connect(DATABASE) as conn:
            ids = conn.execute(SELECT).fetchall()
        founded = re.findall(r'\d+', str(ids))
        return founded
    
    def name_(self, directid=None, id=None):
        if directid is None and id is None:
            SELECT = f'SELECT name FROM {self.name}'
        elif id is not None:
            SELECT = f'SELECT name FROM {self.name} WHERE id = {id}'
        elif directid is not None:
            SELECT = f'SELECT name FROM {self.name} WHERE directid = {directid}'

        with sqlite3.connect(DATABASE) as conn:
            names = conn.execute(SELECT).fetchall()
        sub_names = [re.sub(r'[(\'),]', '', str(name)) for name in names]
        return sub_names


class ElkaDB(object):
    def __init__(self):
        self.mcd = Table('mcd')
        self.station = Table('station')
        self.direction = Table('direction')
        self.mcd_station = Table('mcd_station')
