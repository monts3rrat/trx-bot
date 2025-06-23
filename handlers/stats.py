# handlers\stats.py

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.filters import Command
from bot.utils import load_dummy_data
from bot.keyboards import back_to_main_kb
from bot.security import SecurityManager
from handlers.common import get_group_by_id
router = Router()

@router.callback_query(F.data == "stats")
async def stats_menu(callback: CallbackQuery):
    data = load_dummy_data()
    stats = data["statistics"]
    
    text = (
        "📊 Общая статистика:\n\n"
        f"• Транзакций: {stats['total_transactions']}\n"
        f"• USDT: {stats['total_usdt']:.2f}\n"
        f"• TRX: {stats['total_trx']:.2f}\n"
        f"• Групп: {len(data['groups'])}"
    )
    
    await callback.message.edit_text(text, reply_markup=back_to_main_kb())

@router.message(Command("total_stats"))
async def total_stats_cmd(message: Message):
    data = load_dummy_data()
    stats = data["statistics"]
    
    text = (
        "📊 Общая статистика:\n\n"
        f"• Транзакций: {stats['total_transactions']}\n"
        f"• USDT: {stats['total_usdt']:.2f}\n"
        f"• TRX: {stats['total_trx']:.2f}"
    )
    
    await message.answer(text)

@router.callback_query(F.data.startswith("stats_"))
async def group_stats(callback: CallbackQuery):
    group_id = callback.data.split("_")[1]
    group = get_group_by_id(group_id)
    
    if not group:
        await callback.answer("❌ Группа не найдена!", show_alert=True)
        return
    
    text = (
        f"📊 Статистика группы: {group['name']}\n\n"
        f"• Транзакций: 42\n"
        f"• USDT: 1250.75\n"
        f"• TRX: 15.20\n"
        f"• Активность: высокая"
    )
    
    await callback.message.edit_text(text, reply_markup=back_to_main_kb())
    