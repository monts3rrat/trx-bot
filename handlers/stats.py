from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.filters import Command

from bot.utils import load_dummy_data, get_group_by_id
from bot.keyboards import back_to_main_kb

router = Router()

@router.callback_query(F.data == "stats")
async def stats_menu(callback: CallbackQuery):
    """Общая статистика бота."""
    stats = load_dummy_data().get("statistics", {})
    text = (
        "📊 Общая статистика:\n\n"
        f"• Всего транзакций: {stats.get('total_transactions', 0)}\n"
        f"• USDT собрано: {stats.get('total_usdt', 0.0):.6f}\n"
        f"• TRX потрачено: {stats.get('total_trx', 0.0):.6f}\n"
        f"• Групп: {len(load_dummy_data().get('groups', []))}"
    )
    await callback.message.edit_text(text, reply_markup=back_to_main_kb())

@router.message(Command("total_stats"))
async def total_stats_cmd(message: Message):
    """Общая статистика по команде."""
    stats = load_dummy_data().get("statistics", {})
    text = (
        "📊 Общая статистика:\n"
        f"Транзакций: {stats.get('total_transactions', 0)}\n"
        f"USDT: {stats.get('total_usdt', 0.0):.6f}\n"
        f"TRX: {stats.get('total_trx', 0.0):.6f}"
    )
    await message.answer(text)

@router.callback_query(F.data.startswith("stats_"))
async def group_stats(callback: CallbackQuery):
    """Локальная статистика группы."""
    gid = callback.data.split("_", 1)[1]
    grp = get_group_by_id(gid)
    if not grp:
        return await callback.answer("❌ Группа не найдена!", show_alert=True)
    gstats = grp.get("statistics", {})
    text = (
        f"📊 Статистика группы «{grp['name']}» ({gid}):\n\n"
        f"• Всего транзакций: {gstats.get('total_transactions', 0)}\n"
        f"• USDT собрано: {gstats.get('total_usdt', 0.0):.6f}\n"
        f"• TRX потрачено: {gstats.get('total_trx', 0.0):.6f}\n"
        f"• Плюсовые TX: {gstats.get('positive_tx', 0)}\n"
        f"• Минусовые TX: {gstats.get('negative_tx', 0)}"
    )
    await callback.message.edit_text(text, reply_markup=back_to_main_kb())