import os
import asyncpg
from typing import List, Union


async def get_connection():
    return await asyncpg.connect(os.getenv("DATABASE_URL"))


async def create_table() -> Union[int, Exception]:
    try:
        conn = await get_connection()
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS users_data (
                id SERIAL PRIMARY KEY,
                tg_user_id BIGINT UNIQUE NOT NULL,
                phone_number BIGINT,
                has_premium INTEGER DEFAULT 0
            )
        """)
        await conn.close()
        return 200
    except Exception as e:
        return e


async def insert_data(tg_user_id: int, phone_number: int) -> Union[int, Exception]:
    try:
        conn = await get_connection()
        await conn.execute("""
            INSERT INTO users_data (tg_user_id, phone_number)
            VALUES ($1, $2)
            ON CONFLICT (tg_user_id) DO NOTHING
        """, tg_user_id, phone_number)
        await conn.close()
        return 200
    except Exception as e:
        return e


async def data_updater(tg_user_id: int, phone_number: int) -> Union[int, Exception]:
    try:
        conn = await get_connection()
        await conn.execute("""
            UPDATE users_data
            SET has_premium = 1
            WHERE tg_user_id = $1 AND phone_number = $2
        """, tg_user_id, phone_number)
        await conn.close()
        return 200
    except Exception as e:
        return e


async def get_users_id() -> Union[List[int], Exception]:
    try:
        conn = await get_connection()
        rows = await conn.fetch("SELECT tg_user_id FROM users_data")
        await conn.close()
        return [row["tg_user_id"] for row in rows]
    except Exception as e:
        return e


async def remove_user_id(user_id: int) -> Union[int, Exception]:
    try:
        conn = await get_connection()
        await conn.execute("DELETE FROM users_data WHERE tg_user_id = $1", user_id)
        await conn.close()
        return 200
    except Exception as e:
        return e