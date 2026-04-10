import sqlite3
import os

DB_PATH = os.path.join(os.getcwd(), "sentinelwild.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn
