# bot/main.py
import sys
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties

from bot.config import config
from handlers import start, common, groups, warmup, transactions, stats, settings

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)-5s %(name)s: %(message)s"
    )
    logger = logging.getLogger()            
    logger.setLevel(logging.INFO)            

    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    storage = MemoryStorage()
    bot = Bot(token=config.BOT_TOKEN,
              default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=storage)

    dp.include_routers(
        start.router,
        common.router,
        groups.router,
        warmup.router,
        transactions.router,
        stats.router,
        settings.router,
    )

    logger.info("🤖 Бот запущен")
    asyncio.run(dp.start_polling(bot))