# handlers/stats.py
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.filters import Command

from bot.utils import load_dummy_data, get_group_by_id
from bot.keyboards import back_to_main_kb

router = Router()

@router.callback_query(F.data == "stats")
async def stats_menu(callback: CallbackQuery):
    data = load_dummy_data().get("statistics", {})
    text = (
        "📊 Общая статистика:\n\n"
        f"• Транзакций: {data.get('total_transactions',0)}\n"
        f"• USDT собрано: {data.get('total_usdt',0):.6f}\n"
        f"• TRX потрачено: {data.get('total_trx',0):.6f}"
    )
    await callback.message.edit_text(text, reply_markup=back_to_main_kb())

@router.message(Command("total_stats"))
async def total_stats_cmd(message: Message):
    data = load_dummy_data().get("statistics", {})
    text = (
        "📊 Общая статистика:\n"
        f"Транзакций: {data.get('total_transactions',0)}\n"
        f"USDT: {data.get('total_usdt',0):.6f}\n"
        f"TRX: {data.get('total_trx',0):.6f}"
    )
    await message.answer(text)

@router.callback_query(F.data.startswith("stats_"))
async def group_stats(callback: CallbackQuery):
    gid = callback.data.split("_",1)[1]
    grp = get_group_by_id(gid)
    if not grp:
        return await callback.answer("❌ Группа не найдена!", show_alert=True)
    # Здесь можно расширить сбор групповой статистики
    await callback.message.edit_text(
        f"📊 Статистика «{grp['name']}»:\n"
        f"• Кошельков: {len(grp['wallets'])}\n"
        f"• Последний метод: {grp['method']}",
        reply_markup=back_to_main_kb()
    )