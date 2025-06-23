# handlers\start.py

from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from bot.states import AuthState
from bot.keyboards import main_menu_kb
from bot.security import SecurityManager

router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    if not SecurityManager.is_authorized_user(message.from_user.id):
        await message.answer("⚠️ Доступ запрещен!")
        return
    
    await state.set_state(AuthState.waiting_pin)
    await message.answer("🔐 Введите PIN-код:")

@router.message(AuthState.waiting_pin)
async def process_pin(message: Message, state: FSMContext):
    user_data = await state.get_data()
    attempts = user_data.get("pin_attempts", 0) + 1

    if SecurityManager.check_pin(message.text):
        await state.update_data(authenticated=True, pin_attempts=0)
        await state.set_state(None)
        await message.answer("✅ Доступ разрешен!", reply_markup=main_menu_kb())
    elif attempts >= 3:
        await message.answer("🚫 Превышено количество попыток! Бот заблокирован.")
        await state.clear()
    else:
        await state.update_data(pin_attempts=attempts)
        remaining = 3 - attempts
        await message.answer(f"❌ Неверный PIN! Осталось попыток: {remaining}")