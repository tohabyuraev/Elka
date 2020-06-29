'util.py - provides help utilities'

from config import KEYS


def dumps(root: dict) -> str:
    "Pack values to string with sep = ':' from dict"

    return ':'.join([str(root.get(key, '')) for key in KEYS])


def loads(string: str) -> dict:
    "Unpack values to dict with sep = ':' from srting"

    return dict(zip(KEYS, string.split(':')))
