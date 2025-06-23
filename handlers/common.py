# handlers\common.py

from aiogram import Router, F
from aiogram.types import CallbackQuery
from bot.keyboards import main_menu_kb
from bot.security import SecurityManager
from aiogram.fsm.context import FSMContext
import json
from pathlib import Path

router = Router()

@router.callback_query(F.data == "main_menu")
async def back_to_main_menu(callback: CallbackQuery, state: FSMContext):
    if not await SecurityManager.check_auth(callback.message, state):
        return
    
    await callback.message.edit_text(
        "Главное меню:",
        reply_markup=main_menu_kb()
    )
    await state.clear()


async def get_group_by_id(group_id: str) -> bool:
    DATA_PATH = Path(__file__).parent.parent / "data" / "dummy_data.json"

    try:
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"Ошибка при загрузке данных: {e}")
        return False

    for group in data.get("groups", []):
        if group.get("id") == group_id:
            return True
    return False
