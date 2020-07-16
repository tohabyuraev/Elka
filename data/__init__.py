__author__ = 'Anthony Byuraev'

import sqlite3


conn = sqlite3.connect('data/elka.db')
conn.row_factory = sqlite3.Row
