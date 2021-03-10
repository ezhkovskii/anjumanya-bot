import logging

from aiogram import Bot, Dispatcher, executor, types
from local_settings import API_TOKEN
from query_database import create_db
import services


# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


# commands bot
@dp.message_handler(commands=["start", "help"])
async def send_welcome(message: types.Message):
    check_user
    await message.reply(services.start_msg)


@dp.message_handler()
async def echo(message: types.Message):
    # old style:
    # await bot.send_message(message.chat.id, message.text)

    await message.answer(message.text)



if __name__ == "__main__":
    create_db()
    executor.start_polling(dp, skip_updates=True)
