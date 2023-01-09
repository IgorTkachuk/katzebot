import logging
from typing import List

from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

from unsplash.api import Api
from unsplash.auth import Auth

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config import load_config

config = load_config(".env")

auth = Auth(
    config.unsplash.client_id,
    config.unsplash.client_secret,
    config.unsplash.redirect_uri,
    config.unsplash.code
)

api = Api(auth)

logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.tgbot.token)
dp = Dispatcher(bot)

scheduler = AsyncIOScheduler()

chats: List[str] = []


async def init(a):
    print(a)
    # await bot.send_message(chat_id="772637843", text="Some text")


async def send_photo(chat_id: int):
    photo = api.photo.random(query="cat")
    photo_url = photo[0].urls.small

    await bot.send_photo(chat_id, photo_url)


@dp.message_handler(commands=['katze'])
async def send_katze(message: types.Message):
    print(f"---> {message.chat.id}")
    photo = api.photo.random(query="cat")
    photo_url = photo[0].urls.small

    print(photo_url)
    await message.answer_photo(photo=photo_url)


@dp.message_handler(commands=['scheduler'])
async def plan_scheduler(message: types.Message):
    chat_id = message.chat.id
    scheduler.add_job(send_photo, 'cron', args=(chat_id,), hour=10, minute=0, timezone="Europe/Kiev")
    scheduler.add_job(send_photo, 'cron', args=(chat_id,), hour=14, minute=0, timezone="Europe/Kiev")
    scheduler.add_job(send_photo, 'cron', args=(chat_id,), hour=18, minute=0, timezone="Europe/Kiev")
    scheduler.add_job(send_photo, 'cron', args=(chat_id,), hour=22, minute=0, timezone="Europe/Kiev")

    await message.answer("Scheduled at 10:00, 14:00, 18:00, 22:00")


if __name__ == '__main__':
    scheduler.start()
    executor.start_polling(dp, on_startup=init, skip_updates=True)
