__author__ = 'Anthony Byuraev'

import re
import sqlite3

from config import DATABASE


def get_directions_names() -> [str, ...]:
    conn = sqlite3.connect(DATABASE)

    SELECT_NAMES = ('SELECT name FROM direction')

    data = conn.execute(SELECT_NAMES).fetchall()

    names = [re.sub(r'[(\'),]', '', str(name)) for name in data]

    conn.close()
    return names


def get_directions_ids() -> [str, ...]:
    conn = sqlite3.connect(DATABASE)

    SELECT_ID = ('SELECT id FROM direction')

    data = conn.execute(SELECT_ID).fetchall()

    ids = re.findall(r'\d+', str(data))

    conn.close()
    return ids


def get_stations_names(direction_id: str = None) -> [str, ...]:

    if direction_id is None:
        direction_id = '1'

    conn = sqlite3.connect(DATABASE)

    SELECT_NAMES = ('SELECT name FROM station WHERE directid = ?')

    data = conn.execute(SELECT_NAMES, direction_id).fetchall()

    names = [re.sub(r'[(\'),]', '', str(name)) for name in data]

    conn.close()
    return names


def get_stations_ids(direction_id: str = None) -> [str, ...]:

    if direction_id is None:
        direction_id = '1'

    conn = sqlite3.connect(DATABASE)

    SELECT_ID = ('SELECT id FROM station WHERE directid = ?')

    data = conn.execute(SELECT_ID, direction_id).fetchall()

    ids = re.findall(r'\d+', str(data))

    conn.close()
    return ids


def station_name(station_id: str = None) -> str:

    if station_id is None:
        station_id = '58708'

    conn = sqlite3.connect(DATABASE)

    SELECT_NAME = ('SELECT name FROM station WHERE id = ?')

    data = conn.execute(SELECT_NAME, (station_id,)).fetchone()
    name = re.sub(r'[(\'),]', '', str(data))

    conn.close()
    return name
