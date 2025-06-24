# handlers/warmup.py
import asyncio
import logging
import random
from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from bot.states import WarmupState
from bot.keyboards import warmup_methods_kb, back_to_main_kb, groups_list_kb
from bot.utils import load_dummy_data, get_group_by_id
from bot.blockchain import random_warmup, circular_warmup, mainchain_warmup, trx_only_warmup

router = Router()
logger = logging.getLogger(__name__)


@router.callback_query(F.data == "warmup")
async def warmup_menu(callback: CallbackQuery, state: FSMContext):
    if not load_dummy_data().get("groups"):
        return await callback.message.edit_text("❌ Нет групп.", reply_markup=back_to_main_kb())
    await state.set_state(WarmupState.selecting_group)
    await callback.message.edit_text("🔁 Выберите группу:", reply_markup=groups_list_kb())


@router.callback_query(F.data.startswith("warmup_"))
async def warmup_from_group(callback: CallbackQuery, state: FSMContext):
    gid = callback.data.split("_",1)[1]
    grp = get_group_by_id(gid)
    if not grp or grp["status"] == "paused":
        return await callback.answer("❌ Нельзя прогревать!", show_alert=True)
    await state.set_state(WarmupState.selecting_method)
    await state.update_data(group_id=gid)
    await callback.message.edit_text(
        f"🔁 Метод прогрева для «{grp['name']}» ({gid}):",
        reply_markup=warmup_methods_kb(gid)
    )

@router.callback_query(WarmupState.selecting_method, F.data.startswith("method_"))
async def run_warmup(callback: CallbackQuery, state: FSMContext):
    _, method, gid = callback.data.split("_",2)
    grp = get_group_by_id(gid)
    await state.clear()
    await callback.message.answer(f"🚀 Запускаем {method}-прогрев для {grp['name']}...")
    logger.info("Запущен %s-прогрев для %s", method, gid)
    if method == "random":
        random_warmup(gid)
    elif method == "circle":
        circular_warmup(gid)
    elif method == "main":
        mainchain_warmup(gid)
    elif method == "trx":
        await trx_only_warmup(gid)
    await callback.message.edit_text("✅ Прогрев завершён!", reply_markup=back_to_main_kb())



@router.callback_query(WarmupState.selecting_group, F.data.startswith("group_"))
async def select_group(callback: CallbackQuery, state: FSMContext):
    """
    Обработка выбора группы из общего меню прогрева (warmup → выбор group_<id>).
    """
    gid = callback.data.split("_", 1)[1]
    grp = get_group_by_id(gid)
    if not grp:
        return await callback.answer("❌ Группа не найдена!", show_alert=True)
    if grp["status"] == "paused":
        return await callback.answer("❌ Группа на паузе!", show_alert=True)

    await state.set_state(WarmupState.selecting_method)
    await state.update_data(group_id=gid)
    await callback.message.edit_text(
        f"🔁 Метод прогрева для «{grp['name']}» ({gid}):",
        reply_markup=warmup_methods_kb(gid)
    )
