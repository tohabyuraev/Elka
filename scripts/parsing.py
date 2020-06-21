'parsing.py - parsing web schedule data'

from datetime import datetime, timezone, timedelta

import requests
from lxml import html

from .database import station_name

__author__ = 'Anthony Byuraev'


title = (
    'Расписание от станции {0} до станции {1} со всеми изменениями\n\n'
)
body = (
    '{before} до отправления\n'
    '{time_from} - {root_time} - {time_to}\n'
    '{root_from} - {root_to}\n\n'
)


def schedule(root: dict, lines: int = 3) -> str:
    """
    Builds schedule with departure, arrival and travel time
    """
    DEPARTURE = station_name(root['dep'])
    DESTINATION = station_name(root['des'])

    URL_BASE = 'https://www.tutu.ru/rasp.php'
    URL_PATH = '?st1={}&st2={}'.format(root['dep'], root['des'])
    URL = URL_BASE + URL_PATH

    content = requests.get(URL).content
    data = html.fromstring(content)

    TZ_MSK = timezone(timedelta(hours=3))   # UTC+3
    now = str(datetime.now(TZ_MSK))[11:16]   # format: 'hh:mm'

    time_from = [
        item.text
        for item in data.find_class('g-link desktop__depTimeLink__1NA_N')
        # indication_gone_tooltip
    ]
    time_to = [
        item.text
        for item in data.find_class('g-link desktop__arrTimeLink__2TJxM')
        # white-space: normal;
    ]
    root = [
        item.text
        for item in data.find_class('g-link desktop__routeLink__J643d')
        # overflow:hidden !important;
    ]
    root_from = root[::2]
    root_to = root[1::2]

    if len(time_from) >= lines:
        find = [time for time in time_from if time >= now][0]
        position = time_from.index(find)

        time_from = time_from[position:position + lines]
        time_to = time_to[position:position + lines]
        root_from = root_from[position:position + lines]
        root_to = root_to[position:position + lines]
    else:
        pass

    schedule = title.format(DEPARTURE, DESTINATION)

    for i, time_from in enumerate(time_from):
        schedule += body.format(
            before=interval(now, time_from),
            time_from=time_from,
            root_time=interval(time_from, time_to[i]),
            time_to=time_to[i],
            root_from=root_from[i],
            root_to=root_to[i]
        )
    return schedule


def interval(start: str, stop: str) -> str:
    now_minutes = int(start[:2]) * 60 + int(start[-2:])
    dep_minutes = int(stop[:2]) * 60 + int(stop[-2:])
    hours = (dep_minutes - now_minutes) // 60
    minutes = (dep_minutes - now_minutes) % 60
    if hours:
        return f'{hours} ч {minutes} мин'
    else:
        return f'{minutes} мин'
