import feedparser
from settings import RSS_LINK, DB_REQ_LIMIT
from db_worker import db_worker


async def get_from_rss() -> list:
    feed = feedparser.parse(RSS_LINK)
    req_list = []
    filtered_list = []

    for i in range(0, len(feed.entries)):
        title = feed.entries[i]["title"]
        req_list.append(title)

    for e in req_list:
        if not e.find("1080") == -1:
            filtered_list.append(e)

    return filtered_list


async def init_tables() -> None:
    await db_worker("init", '''CREATE TABLE IF NOT EXISTS anime_published(
        "id" INTEGER,
        "title" TEXT NOT NULL,
        PRIMARY KEY ("id" AUTOINCREMENT)
        )''')

    await db_worker("init", '''CREATE TABLE IF NOT EXISTS anime_checklist(
    "id" INTEGER,
    "title" TEXT NOT NULL,
    "user_id" INTEGER NOT NULL,
    PRIMARY KEY ("id" AUTOINCREMENT)
    )''')


async def get_from_db() -> list:
    db_list = await db_worker("fa", '''SELECT title FROM anime_published LIMIT ?''', (DB_REQ_LIMIT, ))
    return [x[0] for x in db_list]


async def get_new_anime() -> list:
    rss_list = await get_from_rss()
    published_list = await get_from_db()
    check_list = await db_worker("fa", '''SELECT * FROM anime_checklist''')

    new_anime_list = []

    for entry in rss_list:
        if entry not in published_list:
            for j in range(0, len(check_list)):
                if entry.lower().find(check_list[j][1]) != -1:
                    new_anime_list.append((check_list[j][2], entry))

            await db_worker("ins", '''INSERT INTO anime_published(title) VALUES (?)''', (entry, ))
    return new_anime_list


async def list_anime(user_id: int) -> list:
    return await db_worker("fa", '''SELECT id, title FROM anime_checklist WHERE user_id = ?''', (user_id,))


async def add_anime(title: str, user_id: int) -> str:
    if not title:
        return "Provide a title name to add."

    exists = [x[1] for x in await list_anime(user_id)]

    if title in exists:
        return "This title is already in checklist."

    else:
        await db_worker("ins", '''INSERT INTO anime_checklist (title, user_id) VALUES (?, ?)''', (title, user_id))
        return "Title added."


async def del_anime(args: str, user_id: int) -> str:
    if not args:
        return "Provide either id or title name to delete."

    try:
        title = int(args)
    except ValueError:
        title = args

    checklist = await list_anime(user_id)

    for i in range(0, len(checklist)):
        if isinstance(title, str):
            checklist = [x[1].lower() for x in checklist]
            if title.lower() in checklist:
                await db_worker("del", '''DELETE FROM anime_checklist WHERE title = ?''', (title,))
                return "Deleted from check list."

            else:
                return "Matches not found."

        elif isinstance(title, int):
            checklist = [x[0] for x in checklist]
            if title in checklist:
                await db_worker("del", '''DELETE FROM anime_checklist WHERE id = ?''', (title,))
                return "Deleted from check list."

            else:
                return "Matches not found."


if __name__ == '__main__':
    print("Not intended to run on its own.")
