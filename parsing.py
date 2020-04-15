"""
parsing.py - parsing web schedule data
---
"""

from datetime import datetime, timezone, timedelta

import requests
from bs4 import BeautifulSoup

__author__ = 'Anthony Byuraev'


def schedule_text(instructions: dict) -> str:
    ROWS = 3
    LINK = (
        'https://www.tutu.ru/rasp.php?st1={}&st2={}&print=yes'
        .format(instructions['dep'], instructions['des'])
    )
    content = requests.get(LINK).content
    soup = BeautifulSoup(content, features='html.parser')
    title = soup.title.text.split('.')[0] + '\n\n'

    TZ_MSK = timezone(timedelta(hours=3))
    time_now = str(datetime.now(TZ_MSK))[11:16]   # format: 'hh:mm'

    dep_time_root = soup.tbody('div',
                               attrs={'class': 'indication_gone_tooltip'})
    dep_time = [time.a.text for time in dep_time_root]
    buf = [time.a.text for time in dep_time_root if time.a.text >= time_now]
    index = dep_time.index(buf[0])

    des_time_root = soup.tbody('td', attrs={'style': 'white-space: normal;'})
    des_time = [time.a.text for time in des_time_root]

    # all stations
    st_root = soup.tbody('td', attrs={'style': 'overflow:hidden !important;'})
    st_from = [st.a.text for st in st_root[::2]]
    st_to = [st.a.text for st in st_root[1::2]]

    schedule = [
        (
            '{} до отправления\n'
            '{}\n'
            '{} - {}\n\n'
            .format(interval(time_now, dep_time[i]),
                    center_text(dep_time[i], des_time[i]),
                    st_from[i], st_to[i])
        )
        for i in range(index, index + ROWS)
    ]
    schedule.insert(0, title)
    return ''.join(schedule)


def interval(time_from, time_to) -> str:
    now_minutes = int(time_from[:2]) * 60 + int(time_from[-2:])
    dep_minutes = int(time_to[:2]) * 60 + int(time_to[-2:])
    hours = (dep_minutes - now_minutes) // 60
    minutes = (dep_minutes - now_minutes) % 60
    if hours:
        return f'{hours} ч {minutes} мин'
    else:
        return f'{minutes} мин'


def center_text(time_from, time_to):
    return f'{time_from} - {interval(time_from, time_to)} - {time_to}'
