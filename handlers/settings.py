# handlers\settings.py

from aiogram import Router, F
from aiogram.types import CallbackQuery
from bot.states import SettingsState
from bot.keyboards import settings_menu_kb, night_mode_kb, back_to_main_kb
from bot.security import SecurityManager
from aiogram.fsm.context import FSMContext

router = Router()

@router.callback_query(F.data == "settings")
async def settings_menu(callback: CallbackQuery, state: FSMContext):
    if not await SecurityManager.check_auth(callback.message, state):
        return
    
    await callback.message.edit_text(
        "⚙️ Настройки бота:",
        reply_markup=settings_menu_kb()
    )
    await state.set_state(SettingsState.main_menu)

@router.callback_query(F.data == "night_mode")
async def night_mode_settings(callback: CallbackQuery):
    await callback.message.edit_text(
        "🌙 Настройки ночного режима:",
        reply_markup=night_mode_kb()
    )

@router.callback_query(F.data == "night_mode_on")
async def enable_night_mode(callback: CallbackQuery):
    # Заглушка для включения ночного режима
    await callback.answer("🌙 Ночной режим включен")
    await callback.message.edit_text(
        "🌙 Ночной режим включен",
        reply_markup=settings_menu_kb()
    )

@router.callback_query(F.data == "night_mode_off")
async def disable_night_mode(callback: CallbackQuery):
    # Заглушка для выключения ночного режима
    await callback.answer("☀️ Ночной режим выключен")
    await callback.message.edit_text(
        "☀️ Ночной режим выключен",
        reply_markup=settings_menu_kb()
    )

@router.callback_query(F.data == "security_settings")
async def security_settings(callback: CallbackQuery):
    # Заглушка для настроек безопасности
    await callback.answer("🔐 Настройки безопасности")
    await callback.message.edit_text(
        "🔐 Настройки безопасности:\n\n"
        "• PIN-код: установлен\n"
        "• Уведомления: включены\n"
        "• Автоблокировка: активна",
        reply_markup=settings_menu_kb()
    )