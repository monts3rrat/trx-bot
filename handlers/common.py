# handlers/common.py
from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from bot.keyboards import main_menu_kb

router = Router()

@router.callback_query(F.data == "main_menu")
async def back_to_main(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Главное меню:", reply_markup=main_menu_kb())
    await state.clear()