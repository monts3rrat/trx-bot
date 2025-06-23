# handlers\groups.py

import re
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from bot.states import GroupState
from bot.keyboards import (
    groups_menu_kb, 
    group_actions_kb, 
    back_to_main_kb, 
    main_menu_kb,
    ready_kb,
    groups_list_kb,
    back_to_groups_kb
)
from bot.utils import (
    load_dummy_data, 
    save_dummy_data, 
    get_group_by_id,
    get_next_group_id,
    add_group
)
from bot.security import SecurityManager

router = Router()

@router.callback_query(F.data == "groups")
async def groups_menu(callback: CallbackQuery, state: FSMContext):
    if not await SecurityManager.check_auth(callback.message, state):
        return
    await callback.message.edit_text("📁 Управление группами:", reply_markup=groups_menu_kb())

@router.callback_query(F.data == "create_group")
async def create_group_start(callback: CallbackQuery, state: FSMContext):
    if not await SecurityManager.check_auth(callback.message, state):
        return
    await state.set_state(GroupState.creating_name)
    await callback.message.edit_text(
        "Введите название группы:",
        reply_markup=back_to_main_kb()
    )

@router.message(GroupState.creating_name)
async def process_group_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text, wallets=[])
    await state.set_state(GroupState.creating_wallets)
    await message.answer(
        "Введите MAIN кошелек в формате:\n<адрес> <приватный ключ>\nПример: TRXAddress123 privateKey456",
        reply_markup=ready_kb()
    )

@router.message(GroupState.creating_wallets)
async def process_wallet_entry(message: Message, state: FSMContext):
    data = await state.get_data()
    wallets = data.get("wallets", [])
    
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("❌ Неверный формат. Введите адрес и приватный ключ через пробел.")
        return
    
    address, private_key = parts
    address = address.strip()
    private_key = private_key.strip()
    
    encrypted_key = SecurityManager.encrypt_data(private_key)
    
    is_main = len(wallets) == 0
    
    wallet_data = {
        "address": address,
        "private_key_enc": encrypted_key,
        "is_main": is_main,
        "balance": 100.0 if is_main else 50.0
    }
    
    wallets.append(wallet_data)
    await state.update_data(wallets=wallets)
    
    count = len(wallets)
    if count >= 6:
        await finish_group_creation(message, state)
    else:
        next_action = "Введите следующий кошелек" if count < 5 else "Максимум 6 кошельков. Нажмите 'Готово'"
        await message.answer(
            f"✅ Кошелек добавлен. Всего: {count}/6\n{next_action}",
            reply_markup=ready_kb()
        )

@router.callback_query(F.data == "wallets_ready", GroupState.creating_wallets)
async def process_wallets_ready(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    wallets = data.get("wallets", [])
    
    if len(wallets) < 3:
        await callback.answer("❌ Должно быть не менее 3 кошельков!", show_alert=True)
        return
    
    await finish_group_creation(callback.message, state)
    await callback.answer()

async def finish_group_creation(message: Message, state: FSMContext):
    data = await state.get_data()
    group_name = data["name"]
    wallets = data["wallets"]
    
    group_id = get_next_group_id()
    new_group = {
        "id": group_id,
        "name": group_name,
        "wallets": wallets,
        "status": "active",
        "method": "random",
        "main_percent": 30
    }
    
    add_group(new_group)
    await state.clear()
    await message.answer(
        f"✅ Группа '{group_name}' создана!\nID: {group_id}\nКошельков: {len(wallets)}",
        reply_markup=main_menu_kb()
    )

@router.callback_query(F.data == "groups_list")
async def groups_list(callback: CallbackQuery):
    data = load_dummy_data()
    if not data["groups"]:
        await callback.message.edit_text("Список групп пуст.", reply_markup=back_to_groups_kb())
        return
    
    await callback.message.edit_text("📋 Список групп:", reply_markup=groups_list_kb())

@router.callback_query(F.data.startswith("group_"))
async def group_detail(callback: CallbackQuery):
    group_id = callback.data.split("_")[1]
    group = get_group_by_id(group_id)
    
    if not group:
        await callback.answer("❌ Группа не найдена!", show_alert=True)
        return
    
    # Находим основной кошелек
    main_wallet = next((w for w in group["wallets"] if w["is_main"]), None)
    main_balance = main_wallet["balance"] if main_wallet else 0
    
    text = (
        f"📁 Группа: {group['name']}\n"
        f"🆔 ID: {group['id']}\n"
        f"🔧 Метод прогрева: {group['method']}\n"
        f"🟢 Статус: {group['status']}\n"
        f"💼 Кошельков: {len(group['wallets'])}\n"
        f"💰 Баланс MAIN: {main_balance} TRX"
    )
    
    await callback.message.edit_text(text, reply_markup=group_actions_kb(group_id))

@router.callback_query(F.data.startswith("pause_"))
async def group_pause(callback: CallbackQuery):
    group_id = callback.data.split("_")[1]
    # Заглушка для реальной паузы
    await callback.answer(f"⏯️ Группа {group_id} приостановлена")

@router.callback_query(F.data.startswith("resume_"))
async def group_resume(callback: CallbackQuery):
    group_id = callback.data.split("_")[1]
    # Заглушка для возобновления
    await callback.answer(f"▶️ Группа {group_id} возобновлена")

@router.callback_query(F.data.startswith("collect_trx_"))
async def collect_trx(callback: CallbackQuery):
    group_id = callback.data.split("_")[2]
    # Заглушка для сбора TRX
    await callback.answer("💸 Сбор TRX запущен...")