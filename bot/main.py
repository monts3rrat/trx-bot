# bot\main.py

import asyncio
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from bot.config import config
from aiogram.client.default import DefaultBotProperties
from handlers import start, groups, warmup, transactions, stats, settings, common

async def main():
    bot = Bot(token=config.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    dp.include_routers(
        start.router,
        groups.router,
        warmup.router,
        transactions.router,
        stats.router,
        settings.router,
        common.router
    )

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())