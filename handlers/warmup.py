# handlers/warmup.py
from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from bot.states import WarmupState
from bot.keyboards import warmup_methods_kb, back_to_main_kb, groups_list_kb
from bot.utils import load_dummy_data, get_group_by_id
from bot.blockchain import random_warmup, circular_warmup, mainchain_warmup

router = Router()

@router.callback_query(F.data == "warmup")
async def warmup_menu(callback: CallbackQuery, state: FSMContext):
    data = load_dummy_data()
    if not data.get("groups"):
        return await callback.message.edit_text("❌ Нет групп. Сначала создайте.", reply_markup=back_to_main_kb())
    await state.set_state(WarmupState.selecting_group)
    await callback.message.edit_text("🔁 Выберите группу:", reply_markup=groups_list_kb())

@router.callback_query(WarmupState.selecting_group, F.data.startswith("group_"))
async def select_group(callback: CallbackQuery, state: FSMContext):
    gid = callback.data.split("_",1)[1]
    grp = get_group_by_id(gid)
    if not grp:
        return await callback.answer("❌ Группа не найдена!", show_alert=True)
    await state.update_data(group_id=gid)
    await state.set_state(WarmupState.selecting_method)
    await callback.message.edit_text(f"🔁 Выберите метод для «{grp['name']}»:", reply_markup=warmup_methods_kb(gid))

@router.callback_query(WarmupState.selecting_method, F.data.startswith("method_"))
async def run_warmup(callback: CallbackQuery, state: FSMContext):
    _, method, gid = callback.data.split("_",2)
    cfg = await state.get_data()
    grp = get_group_by_id(gid)
    amount = 1.0  # фиксированная сумма прогрева в TRX
    if method == "random":
        random_warmup(gid, grp["main_percent"], amount)
    elif method == "circle":
        circular_warmup(gid, amount)
    elif method == "main":
        mainchain_warmup(gid, amount)
    await state.clear()
    await callback.message.edit_text("✅ Прогрев запущен!", reply_markup=back_to_main_kb())