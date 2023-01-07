import logging

from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

from unsplash.api import Api
from unsplash.auth import Auth

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


async def init(a):
    print(a)
    await bot.send_message(chat_id="772637843", text="Some text")

@dp.message_handler(commands=['catze'])
async def send_katze(message: types.Message):
    print("--->")
    photo = api.photo.random(query="cat")
    photo_url = photo[0].urls.small

    print(photo_url)
    await message.answer_photo(photo=photo_url)

if __name__ == '__main__':
    executor.start_polling(dp, on_startup=init, skip_updates=True)
