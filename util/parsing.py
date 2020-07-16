"""
parsing.py - parsing web schedule data
"""

__author__ = 'Anthony Byuraev'

import typing
import logging
from datetime import datetime

import aiohttp
from lxml import html

from data import conn


title = (
    'Расписание\n'
    'от станции "{departure}"\n'
    'до станции "{destination}"\n'
    'со всеми изменениями\n\n'
)
body = (
    '{before} до отправления\n'
    '{tfrom} - {rtime} - {tto}\n'
    '{rfrom} - {rto}\n\n'
)


async def schedule(root: typing.Dict[str, str],
                   lines: int = 3) -> str:
    """
    Builds schedule with departure, arrival and travel time
    """
    DEPARTURE = conn.execute(
        'SELECT name FROM station WHERE id = ?', (root['sfrom'],)
    ).fetchone()['name']
    DESTINATION = conn.execute(
        'SELECT name FROM station WHERE id = ?', (root['sto'],)
    ).fetchone()['name']

    URL_BASE = 'https://www.tutu.ru/rasp.php'
    URL_PATH = f"?st1={root['sfrom']}&st2={root['sto']}"
    URL = f'{URL_BASE}{URL_PATH}'

    content = await get_content(URL)
    data = html.fromstring(content)

    localtime = str(datetime.now())[11:16]
    now = f"{int(localtime.split(':')[0]) + 3}:{localtime.split(':')[1]}"

    tfrom_list = [
        item.text
        for item in data.find_class('g-link desktop__depTimeLink__1NA_N')
        # indication_gone_tooltip
    ]
    tto_list = [
        item.text
        for item in data.find_class('g-link desktop__arrTimeLink__2TJxM')
        # white-space: normal;
    ]
    root = [
        item.text
        for item in data.find_class('g-link desktop__routeLink__J643d')
        # overflow:hidden !important;
    ]
    rto_list = root[1::2]
    rfrom_list = root[::2]

    if tfrom_list.__len__() >= lines:
        find = [time for time in tfrom_list if time >= now][0]
        position = tfrom_list.index(find)

        tto_list = tto_list[position:position + lines]
        tfrom_list = tfrom_list[position:position + lines]
        rto_list = rto_list[position:position + lines]
        rfrom_list = rfrom_list[position:position + lines]
    else:
        pass

    schedule = title.format(
        departure=DEPARTURE,
        destination=DESTINATION,
    )

    for i, tfrom in enumerate(tfrom_list):
        schedule += body.format(
            before=interval(now, tfrom),
            tfrom=tfrom,
            rtime=interval(tfrom, tto_list[i]),
            tto=tto_list[i],
            rfrom=rfrom_list[i],
            rto=rto_list[i]
        )
    return schedule


def interval(start: str, stop: str) -> str:
    start_minutes = int(start.split(':')[0]) * 60 + int(start.split(':')[1])
    stop_minutes = int(stop.split(':')[0]) * 60 + int(stop.split(':')[1])
    hours = (stop_minutes - start_minutes) // 60
    minutes = (stop_minutes - start_minutes) % 60
    if hours:
        return f'{hours} ч {minutes} мин'
    else:
        return f'{minutes} мин'

    
async def get_content(url: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.content.read()
