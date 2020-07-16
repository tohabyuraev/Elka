__author__ = 'Anthony Byuraev'

import typing


def url(root: typing.Dict[str, str]) -> str:
    """
    Return web page URL with train schedule
    """
    return f"https://www.tutu.ru/rasp.php?st1={root['sfrom']}&st2={root['sto']}"
