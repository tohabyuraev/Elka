"""
util.py - provides help utilities
"""

__author__ = 'Anthony Byuraev'

import typing

from config import KEYS


async def dumps(root: typing.Dict[str, str]) -> str:
    "Pack values to string with sep = ':' from dict"
    return ':'.join([str(root.get(key, '')) for key in KEYS])


async def loads(string: str) -> typing.Dict[str, str]:
    "Unpack values to dict with sep = ':' from srting"
    return dict(zip(KEYS, string.split(':')))


async def callback_builder(root: typing.Dict[str, str], call: str, **kwargs) -> str:
    callback = root.copy()
    callback['call'] = call
    if kwargs.get('dir') is None:
        pass
    else:
        callback['dir'] = kwargs['dir']
    if kwargs.get('sfrom') is None:
        pass
    else:
        callback['sfrom'] = kwargs['sfrom']
    if kwargs.get('sto') is None:
        pass
    else:
        callback['sto'] = kwargs['sto']
    callback['date'] = kwargs.get('date')
    if kwargs.get('page') is None:
        pass
    else:
        callback['page'] = kwargs['page']
    return await dumps(callback)
