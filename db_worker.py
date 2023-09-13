import aiosqlite
import time
from settings import DB


async def db_worker(opr: str, sql: str, values: tuple = None):
    db = await aiosqlite.connect(DB)

    match opr:
        case "init":
            await db.execute(sql, values)

        case "fo":
            cursor = await db.execute(sql, values)
            row = await cursor.fetchone()
            await cursor.close()
            return row[0]

        case "fa":
            cursor = await db.execute(sql, values)
            rows = await cursor.fetchall()
            await cursor.close()
            return rows

        case "ins" | "del":
            cursor = await db.execute(sql, values)
            await db.commit()
            await cursor.close()

    await db.close()


async def init_db() -> None:
    await db_worker("init", '''CREATE TABLE IF NOT EXISTS users(
    "id" INTEGER,
    "user_id" INTEGER NOT NULL UNIQUE,
    "username" TEXT,
    "first_name" TEXT,
    "last_name" TEXT,
    "join_date_secs" REAL NOT NULL,
    "join_date_full" TEXT,
    PRIMARY KEY ("id" AUTOINCREMENT)
    )''')


async def new_user(user_id: int, username: str, first_name: str, last_name: str) -> None:
    t = time.time()
    sql = '''INSERT INTO users(user_id, username, first_name, last_name, join_date_secs, join_date_full) 
    VALUES(?, ?, ?, ?, ?, ?)'''
    values = (user_id, username, first_name, last_name, t, time.ctime(t))
    await db_worker("ins", sql, values)


if __name__ == '__main__':
    print("Not intended to run on its own.")
