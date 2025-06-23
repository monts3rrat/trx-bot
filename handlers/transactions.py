# handlers\transactions.py

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.filters import Command

router = Router()

@router.message(Command("collect_usdt"))
async def collect_usdt_cmd(message: Message):
    # Заглушка для сбора USDT
    await message.answer("💵 Сбор USDT в процессе...")

@router.message(Command("collect_trx"))
async def collect_trx_cmd(message: Message):
    # Заглушка для сбора TRX
    await message.answer("💸 Сбор TRX в процессе...")

@router.callback_query(F.data == "collect_all")
async def collect_all_trx(callback: CallbackQuery):
    # Заглушка для сбора всех TRX
    await callback.answer("🔄 Сбор всех TRX запущен...")