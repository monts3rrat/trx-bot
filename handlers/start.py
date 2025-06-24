# handlers/start.py
from aiogram import Router
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
        await state.set_state(AuthState.waiting_pin)
        await message.answer("🔐 Введите PIN‑код:")
    else:
        await message.answer("✅ Вы уже авторизованы", reply_markup=main_menu_kb())

@router.message(AuthState.waiting_pin)
async def process_pin(message: Message, state: FSMContext):
    user_data = await state.get_data()
    attempts = user_data.get("pin_attempts", 0) + 1

    if SecurityManager.check_pin(message.text):
        SecurityManager.authorize_user(message.from_user.id)
        await state.clear()
        await message.answer("✅ Доступ разрешён", reply_markup=main_menu_kb())
    elif attempts >= 3:
        await message.answer("🚫 Блокировка! Превышено число попыток.")
        await state.clear()
    else:
        await state.update_data(pin_attempts=attempts)
        await message.answer(f"❌ Неверный PIN. Осталось {SecurityManager.MAX_PIN_ATTEMPTS - attempts} попыток.")