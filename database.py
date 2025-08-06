import sqlite3
from sqlite3 import Error


def create_table():
    con = sqlite3.connect("users_data.db")
    try:
        cur = con.cursor()
        cur.execute("""CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tg_user_id INTEGER UNIQUE NOT NULL,
        phone_number INTEGER,
        has_premium INTEGER DEFAULT 0
        )""")
        con.commit()
        con.close()
        return 200
    except Error as e:
        return e


def insert_data(tg_user_id, phone_number):
    con = sqlite3.connect("users_data.db")
    cursor = con.cursor()

    try:
        cursor.execute("INSERT INTO users (tg_user_id, phone_number) VALUES (?, ?)", (tg_user_id, phone_number))

        con.commit()
        con.close()
        return 200
    except Error:
        return Error


def data_updater(tg_user_id, phone_number):
    con = sqlite3.connect("user_data.db")
    cursor = con.cursor()

    try:
        cursor.execute(f"""UPDATE users SET has_premium = 1 WHERE tg_user_id = {tg_user_id} AND phone_number = {phone_number} """)
        con.commit()
        con.close()
        return 200
    except Error:
        return Error


def get_users_id() -> list[int]:
    con = sqlite3.connect("users_data.db")
    cursor = con.cursor()

    try:
        cursor.execute(f"""SELECT tg_user_id FROM users""")
        return [row[0] for row in cursor.fetchall()]
    except Error:
        return Error


def remove_user_id(user_id: int):
    with sqlite3.connect("users_data.db") as con:
        cur = con.cursor()
        cur.execute("""DELETE FROM users WHERE tg_user_id = ?""", (user_id,))
        con.commit()