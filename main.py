import json
import logging
from typing import List
from types import SimpleNamespace

from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

from unsplash.api import Api
from unsplash.auth import Auth

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.redis import RedisJobStore

from redis import Redis

from config import load_config

import requests

config = load_config(".env")

auth = Auth(
    config.unsplash.client_id,
    config.unsplash.client_secret,
    config.unsplash.redirect_uri,
    config.unsplash.code
)

api = Api(auth)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

r = Redis(host="redis")

bot = Bot(token=config.tgbot.token)
dp = Dispatcher(bot)

job_stores = {
    "default": RedisJobStore(
        jobs_key="dispatched_trips_jobs", run_times_key="dispatched_trips_running",
        host="redis", port=6379
    )
}

scheduler = AsyncIOScheduler(jobstores=job_stores)

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
    chat_id = message.chat.id

    while True:
        photo = api.photo.random(query="cat")
        photo_id = photo[0].id

        if not r.sismember(str(chat_id) + "_showed_katzes", photo_id):
            break

        logger.info(f"Image {photo_id} is showed earlier. Skipped!")

    r.sadd(str(chat_id) + "_showed_katzes", photo_id)
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


@dp.message_handler(commands=['configuration'])
async def get_configuration(message: types.Message):
    result = "Photo distribution planed at:\n"
    jobs_count = 0

    jobs = scheduler.get_jobs()
    for job in jobs:
        if job.args[0] == message.chat.id:
            jobs_count += 1
            next_run_time = job.next_run_time.strftime("%d.%m.%Y %H:%M")
            result += next_run_time + "\n"

    if jobs_count == 0:
        await message.answer("No distribution planed")
    else:
        await message.answer(result)


@dp.message_handler(commands=["quote"])
async def quote(message: types.Message):
    category = 'happiness'
    api_url = 'https://api.api-ninjas.com/v1/quotes?category={}'.format(category)
    response = requests.get(api_url, headers={'X-Api-Key': config.apininjas.key})
    if response.status_code == requests.codes.ok:
        data = json.loads(response.text)
        text = data[0].get('quote')
        author = data[0].get('author')
        await message.answer(f"{text}\n\n{author}")
    else:
        logger.error("Error:" + str(response.status_code) + response.text)


if __name__ == '__main__':
    try:
        scheduler.start()
        executor.start_polling(dp, on_startup=init, skip_updates=True)
    except (KeyboardInterrupt, SystemExit):
        logger.error("Bot stopped!")
