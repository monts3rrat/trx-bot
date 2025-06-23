# handlers/groups.py
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from bot.states import GroupState
from bot.keyboards import (
    groups_menu_kb,
    back_to_main_kb,
    groups_list_kb,
    group_actions_kb,
    ready_kb
)
from bot.utils import (
    load_dummy_data,
    add_group,
    get_group_by_id,
    get_next_group_id,
    update_wallet_balances
)
from bot.security import SecurityManager

router = Router()


@router.callback_query(F.data == "groups")
async def cmd_groups(callback: CallbackQuery):
    await callback.message.edit_text("📁 Управление группами:", reply_markup=groups_menu_kb())


@router.callback_query(F.data == "create_group")
async def start_create(callback: CallbackQuery, state: FSMContext):
    await state.set_state(GroupState.creating_name)
    await callback.message.edit_text("Введите название группы:", reply_markup=back_to_main_kb())


@router.message(GroupState.creating_name)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text, wallets=[])
    await state.set_state(GroupState.creating_wallets)
    await message.answer(
        "Введите кошелёк в формате: адрес приватный_ключ_hex\n"
        "Например:\nTRXAddress123 abcdef0123456789...",
        reply_markup=ready_kb()
    )


@router.message(GroupState.creating_wallets)
async def process_wallet(message: Message, state: FSMContext):
    data = await state.get_data()
    wallets = data["wallets"]

    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        return await message.answer("❌ Формат: адрес и приватный ключ через пробел.")

    addr, pk = parts
    enc = SecurityManager.encrypt_data(pk)
    wallets.append({
        "address": addr,
        "private_key_enc": enc,
        "is_main": len(wallets) == 0,
        "balance": 0.0
    })
    await state.update_data(wallets=wallets)

    if len(wallets) >= 6:
        return await finish_group(message, state)

    count = len(wallets)
    hint = "Добавьте ещё кошелёк" if count < 3 else "Добавьте ещё кошелёк или нажмите Готово"
    await message.answer(f"✅ Добавлено: {count}/6. {hint}", reply_markup=ready_kb())


@router.callback_query(F.data == "wallets_ready", GroupState.creating_wallets)
async def finish_group(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    name = data["name"]
    wallets = data["wallets"]
    if len(wallets) < 3:
        return await callback.answer("Нужно минимум 3 кошелька!", show_alert=True)

    gid = get_next_group_id()
    add_group({
        "id": gid,
        "name": name,
        "wallets": wallets,
        "status": "active",
        "method": "random",
        "main_percent": 30
    })
    await state.clear()
    await callback.message.answer(f"✅ Группа «{name}» создана ({gid})", reply_markup=back_to_main_kb())


@router.callback_query(F.data == "groups_list")
async def list_groups(callback: CallbackQuery):
    data = load_dummy_data()
    if not data.get("groups"):
        return await callback.message.edit_text("Список групп пуст.", reply_markup=back_to_main_kb())
    await callback.message.edit_text("📋 Список групп:", reply_markup=groups_list_kb())


@router.callback_query(F.data.startswith("group_"))
async def show_group(callback: CallbackQuery):
    gid = callback.data.split("_", 1)[1]
    update_wallet_balances(gid)
    grp = get_group_by_id(gid)
    if not grp:
        return await callback.answer("❌ Группа не найдена!", show_alert=True)

    main = next(w for w in grp["wallets"] if w["is_main"])
    text = (
        f"📁 {grp['name']} ({grp['id']})\n"
        f"🔧 Метод: {grp['method']}\n"
        f"🟢 Статус: {grp['status']}\n"
        f"💼 Всего кошельков: {len(grp['wallets'])}\n"
        f"💰 Main‑баланс: {main['balance']:.6f} TRX"
    )
    await callback.message.edit_text(text, reply_markup=group_actions_kb(gid))


@router.callback_query(F.data.startswith("pause_"))
async def group_pause(callback: CallbackQuery):
    gid = callback.data.split("_", 1)[1]
    await callback.answer(f"⏸️ Группа {gid} приостановлена")


@router.callback_query(F.data.startswith("resume_"))
async def group_resume(callback: CallbackQuery):
    gid = callback.data.split("_", 1)[1]
    await callback.answer(f"▶️ Группа {gid} возобновлена")


@router.callback_query(F.data.startswith("collect_trx_"))
async def collect_trx(callback: CallbackQuery):
    gid = callback.data.split("_", 2)[2]
    await callback.answer(f"💸 Сбор TRX для группы {gid} запущен...")


@router.callback_query(F.data.startswith("collect_usdt_"))
async def collect_usdt(callback: CallbackQuery):
    gid = callback.data.split("_", 2)[2]
    await callback.answer(f"💵 Сбор USDT для группы {gid} запущен...")


@router.callback_query(F.data.startswith("delete_"))
async def delete_group(callback: CallbackQuery):
    gid = callback.data.split("_", 1)[1]
    # TODO: реализовать удаление группы из JSON
    await callback.answer(f"❌ Группа {gid} удалена!")
    await callback.message.edit_text("📋 Список групп:", reply_markup=groups_list_kb())