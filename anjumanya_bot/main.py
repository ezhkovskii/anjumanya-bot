import logging
import asyncio

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from settings.local_settings import API_TOKEN
from handlers import register_handlers


logger = logging.getLogger(__name__)


async def set_commands(bot: Bot):
    commands = [
        types.BotCommand(command="/help", description="инструкция"),
        types.BotCommand(command="/input", description="ввести данные тренировочки"),
        types.BotCommand(command="/cancel", description="отмена ввода данных"),
        #types.BotCommand(command="/send_to_chat", description="отправить последнюю тренировочку в чат"),
        types.BotCommand(command="/get_data", description="вывести данные по тренировочке")
    ]
    await bot.set_my_commands(commands)


async def main():
    # Настройка логирования в stdout
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    logger.error("Starting bot")

    # Объявление и инициализация объектов бота и диспетчера
    bot = Bot(token=API_TOKEN)
    dp = Dispatcher(bot, storage=MemoryStorage())

    # Регистрация хэндлеров
    register_handlers(dp)

    # Установка команд бота
    await set_commands(bot)

    # Запуск поллинга
    #await dp.skip_updates()  # пропуск накопившихся апдейтов (необязательно)
    await dp.start_polling()


if __name__ == "__main__":
    asyncio.run(main())
