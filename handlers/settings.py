# handlers/settings.py
from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from bot.states import SettingsState
from bot.keyboards import settings_menu_kb, night_mode_kb, back_to_main_kb

router = Router()

@router.callback_query(F.data == "settings")
async def settings_menu(callback: CallbackQuery, state: FSMContext):
    await state.set_state(SettingsState.main_menu)
    await callback.message.edit_text("⚙️ Настройки:", reply_markup=settings_menu_kb())

@router.callback_query(F.data == "night_mode")
async def night_mode(callback: CallbackQuery):
    await callback.message.edit_text("🌙 Ночной режим:", reply_markup=night_mode_kb())

@router.callback_query(F.data == "night_mode_on")
async def nm_on(callback: CallbackQuery):
    await callback.answer("🌙 Включён")
    await callback.message.edit_text("🌙 Режим ON", reply_markup=settings_menu_kb())

@router.callback_query(F.data == "night_mode_off")
async def nm_off(callback: CallbackQuery):
    await callback.answer("☀️ Выключен")
    await callback.message.edit_text("☀️ Режим OFF", reply_markup=settings_menu_kb())