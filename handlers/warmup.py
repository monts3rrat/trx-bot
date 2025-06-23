# handlers\warmup.py

from aiogram import Router, F
from aiogram.types import CallbackQuery
from bot.states import WarmupState
from bot.keyboards import (
    warmup_methods_kb, 
    back_to_main_kb,
    groups_list_kb
)
from bot.utils import load_dummy_data, get_group_by_id
from bot.security import SecurityManager
from aiogram.fsm.context import FSMContext

router = Router()

@router.callback_query(F.data == "warmup")
async def warmup_menu(callback: CallbackQuery, state: FSMContext):
    if not await SecurityManager.check_auth(callback.message, state):
        return
    
    data = load_dummy_data()
    if not data["groups"]:
        await callback.message.edit_text(
            "❌ Нет доступных групп. Сначала создайте группу.",
            reply_markup=back_to_main_kb()
        )
        return
    
    await callback.message.edit_text(
        "🔁 Выберите группу для прогрева:",
        reply_markup=groups_list_kb()
    )
    await state.set_state(WarmupState.selecting_group)

@router.callback_query(WarmupState.selecting_group, F.data.startswith("group_"))
async def select_group_for_warmup(callback: CallbackQuery, state: FSMContext):
    group_id = callback.data.split("_")[1]
    group = get_group_by_id(group_id)
    
    if not group:
        await callback.answer("❌ Группа не найдена!", show_alert=True)
        return
    
    await state.update_data(selected_group=group_id)
    await callback.message.edit_text(
        f"🔁 Выберите метод прогрева для группы: {group['name']}",
        reply_markup=warmup_methods_kb(group_id)
    )
    await state.set_state(WarmupState.selecting_method)

@router.callback_query(WarmupState.selecting_method, F.data.startswith("method_"))
async def select_warmup_method(callback: CallbackQuery, state: FSMContext):
    method = callback.data.split("_")[1]
    group_id = callback.data.split("_")[2]
    
    methods = {
        "random": "🎲 Рандомный",
        "circle": "🔄 Круговой",
        "main": "⭐ MAIN-цепочка"
    }
    
    # Обновляем метод в группе
    group = get_group_by_id(group_id)
    if group:
        group["method"] = method
        # Здесь должна быть функция обновления группы в хранилище
    
    await callback.message.edit_text(
        f"✅ Выбран метод: {methods.get(method, 'Неизвестный')}\n\n"
        "Настройки прогрева:",
        reply_markup=back_to_main_kb()
    )
    await state.clear()
    
    # Заглушка для запуска прогрева
    await callback.answer(f"🚀 Прогрев запущен по методу: {methods.get(method)}")