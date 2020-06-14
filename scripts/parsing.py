'parsing.py - parsing web schedule data'

from datetime import datetime, timezone, timedelta

import requests
from bs4 import BeautifulSoup

import scripts.database as database

__author__ = 'Anthony Byuraev'


def schedule_text(root: dict, lines: int = 3) -> str:
    """
    Builds schedule text with  departure, arrival and travel time:

    Parameters:
    -----------
    root: dict
        Commands and info

    Returns:
    --------
    string: str
        Schedule text

    """

    LINK = (
        'https://www.tutu.ru/rasp.php?st1={}&st2={}&print=yes'
        .format(root['dep'], root['des'])
    )

    content = requests.get(LINK).content
    soup = BeautifulSoup(content, 'html.parser')

    TZ_MSK = timezone(timedelta(hours=3))   # UTC+3
    time_now = str(datetime.now(TZ_MSK))[11:16]   # format: 'hh:mm'

    deparure_time_array = soup.tbody(
        'div', attrs={'class': 'indication_gone_tooltip'})
    deparure_time = [time.a.text for time in deparure_time_array]
    buf = [time.a.text
           for time in deparure_time_array if time.a.text >= time_now]
    index = deparure_time.index(buf[0])

    destination_time_array = soup.tbody(
        'td', attrs={'style': 'white-space: normal;'})
    destination_time = [time.a.text for time in destination_time_array]

    # all stations
    st_array = soup.tbody('td', attrs={'style': 'overflow:hidden !important;'})
    st_from = [st.a.text for st in st_array[::2]]
    st_to = [st.a.text for st in st_array[1::2]]

    schedule = [
        (
            '{} до отправления\n'
            '{}\n'
            '{} - {}\n\n'
            .format(interval(time_now, deparure_time[i]),
                    center_text(deparure_time[i], destination_time[i]),
                    st_from[i], st_to[i])
        )
        for i in range(index, index + lines)
    ]
    schedule.insert(0, title(root))
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


def title(root: dict) -> str:
    station_from = database.station_name(root['dep'])
    station_to = database.station_name(root['des'])

    return (
        'Расписание от станции `{}` до станции `{}` со всеми изменениями\n\n'
        .format(station_from, station_to)
    )
