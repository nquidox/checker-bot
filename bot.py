import os
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command, CommandObject


import db_worker
import anime_checker
from settings import checker_interval, DB


TOKEN = os.getenv("TOKEN")
bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()


@dp.message(CommandStart())
async def start_handler(msg: Message) -> None:
    try:
        await msg.answer("Welcome to anime checker bot!")
        await db_worker.new_user(msg.from_user.id,
                                 msg.from_user.username,
                                 msg.from_user.first_name,
                                 msg.from_user.last_name)
    except TypeError:
        await msg.answer("Nice try!")


@dp.message(Command("list_anime"))
async def list_anime(msg: Message) -> None:
    checklist = await anime_checker.list_anime(msg.from_user.id)

    if not checklist:
        await msg.answer("Checklist is empty.")

    else:
        message_text = ""
        for i in range(0, len(checklist)):
            message_text += f"{checklist[i][0]} | {checklist[i][1]}\n"
        await msg.answer(f"Anime checklist: \n{message_text}")


@dp.message(Command("add_anime"))
async def add_anime(msg: Message, command: CommandObject):
    title = command.args
    status = await anime_checker.add_anime(title, msg.from_user.id)
    await msg.answer(status)


@dp.message(Command("del_anime"))
async def del_anime(msg: Message, command: CommandObject):
    args = command.args
    status = await anime_checker.del_anime(args, msg.from_user.id)
    await msg.answer(status)


async def check_anime() -> None:
    while True:
        new_anime_list = await anime_checker.get_new_anime()
        for i in range(0, len(new_anime_list)):
            await bot.send_message(chat_id=new_anime_list[i][0],
                                   text=f"New episode: {new_anime_list[i][1]}")

        await asyncio.sleep(60*checker_interval)


async def main() -> None:
    if not os.path.exists(DB):
        await db_worker.init_db()
        await anime_checker.init_tables()

    await asyncio.sleep(3)
    await dp.start_polling(bot)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    task = loop.create_task(check_anime())
    loop.run_until_complete(main())
