# handlers/groups.py
import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from bot.states import GroupState, LimitState
from bot.keyboards import (
    groups_menu_kb, back_to_main_kb, groups_list_kb,
    group_actions_kb, ready_kb
)
from bot.utils import (
    load_dummy_data, add_group, get_group_by_id,
    get_next_group_id, update_wallet_balances,
    update_group, record_transaction, save_dummy_data
)
from bot.blockchain import send_trx, send_usdt
from tronpy.exceptions import ValidationError, UnknownError
from bot.security import SecurityManager

router = Router()
logger = logging.getLogger(__name__)

@router.callback_query(F.data == "groups")
async def cmd_groups(callback: CallbackQuery):
    await callback.message.edit_text("📁 Управление группами:", reply_markup=groups_menu_kb())

@router.callback_query(F.data == "create_group")
async def start_create(callback: CallbackQuery, state: FSMContext):
    await state.set_state(GroupState.creating_name)
    await callback.message.edit_text("Введите название группы:", reply_markup=back_to_main_kb())

@router.message(GroupState.creating_name)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(GroupState.creating_wallets)
    await message.answer(
        "📥 Отправьте все кошельки (каждый с новой строки):\n"
        "<code>address private_key_hex</code>\n"
        "Когда готово — нажмите ✅ Готово",
        reply_markup=ready_kb()
    )


@router.message(GroupState.creating_wallets)
async def process_wallets(message: Message, state: FSMContext):
    lines = [l.strip() for l in message.text.splitlines() if l.strip()]
    wallets = []
    for l in lines:
        parts = l.split(maxsplit=1)
        if len(parts) != 2:
            continue
        addr, pk = parts
        enc = SecurityManager.encrypt_data(pk)
        wallets.append({"address": addr, "private_key_enc": enc, "is_main": False, "balance": 0.0})
    if wallets:
        wallets[0]["is_main"] = True
    await state.update_data(wallets=wallets)
    await message.answer(f"✅ Добавлено {len(wallets)} кошельков. Нажмите ✅ Готово.", reply_markup=ready_kb())


@router.callback_query(F.data == "wallets_ready", GroupState.creating_wallets)
async def finish_group(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    name = data["name"]
    wallets = data["wallets"]
    if len(wallets) < 3:
        return await callback.answer("Нужно минимум 3 кошелька!", show_alert=True)
    gid = get_next_group_id()
    add_group({
        "id": gid, "name": name, "wallets": wallets,
        "status": "active", "method": "random", "main_percent": 30,
        "daily_trx_limit": 10, "trx_interval_min": 1, "trx_interval_max": 2
    })
    await state.clear()
    await callback.message.answer(f"✅ Группа «{name}» создана ({gid})", reply_markup=back_to_main_kb())


@router.callback_query(F.data == "groups_list")
async def list_groups(callback: CallbackQuery):
    if not load_dummy_data().get("groups"):
        return await callback.message.edit_text("Список групп пуст.", reply_markup=back_to_main_kb())
    await callback.message.edit_text("📋 Список групп:", reply_markup=groups_list_kb())


@router.callback_query(F.data.startswith("group_"))
async def show_group(callback: CallbackQuery):
    gid = callback.data.split("_", 1)[1]
    update_wallet_balances(gid)
    grp = get_group_by_id(gid)
    main = next(w for w in grp["wallets"] if w["is_main"])
    text = (
        f"📁 {grp['name']} ({gid})\n"
        f"🔧 Метод: {grp['method']}\n"
        f"🟢 Статус: {grp['status']}\n"
        f"💰 Main‑баланс: {main['balance']:.6f} TRX\n"
        f"⚙️ TRX-only лимит: {grp['daily_trx_limit']} TX/день\n"
        f"⏱ Интервал: {grp['trx_interval_min']}–{grp['trx_interval_max']} мин\n"
        f"🎲 % MAIN (random): {grp['main_percent']}%"
    )
    await callback.message.edit_text(text, reply_markup=group_actions_kb(gid, grp["status"]))


@router.callback_query(F.data.startswith("limit_"))
async def change_limit(callback: CallbackQuery, state: FSMContext):
    gid = callback.data.split("_",1)[1]
    await state.update_data(limit_group=gid)
    await state.set_state(LimitState.waiting_limit)
    await callback.message.edit_text(
        "✏️ Введите новые параметры TRX-only прогрева (в минутах):\n"
        "<code>daily_limit interval_min interval_max main_percent</code>\n"
        "Пример: <code>15 1 2 40</code>",
        reply_markup=back_to_main_kb()
    )


@router.message(LimitState.waiting_limit)
async def process_limit(message: Message, state: FSMContext):
    parts = message.text.split()
    if len(parts) != 4:
        return await message.answer("❌ Ошибка формата. Введите 4 целых числа через пробел.")
    try:
        dl, imin, imax, mp = map(int, parts)
    except ValueError:
        return await message.answer("❌ Неверные данные. Все четыре должны быть целыми числами.")
    data = await state.get_data()
    gid = data["limit_group"]
    update_group(gid, {
        "daily_trx_limit": dl,
        "trx_interval_min": imin,
        "trx_interval_max": imax,
        "main_percent": mp
    })
    await state.clear()
    await message.answer(
        f"✅ Лимиты обновлены для {gid}:\n"
        f"TX/day={dl}, interval={imin}-{imax} мин, main%={mp}",
        reply_markup=back_to_main_kb()
    )


@router.callback_query(F.data.startswith("pause_"))
async def group_pause(callback: CallbackQuery):
    gid = callback.data.split("_",1)[1]
    update_group(gid, {"status": "paused"})
    await callback.answer("⏸️ Группа приостановлена")
    grp = get_group_by_id(gid)
    await callback.message.edit_text(
        f"📁 {grp['name']} (paused)", reply_markup=group_actions_kb(gid, "paused")
    )


@router.callback_query(F.data.startswith("resume_"))
async def group_resume(callback: CallbackQuery):
    gid = callback.data.split("_",1)[1]
    update_group(gid, {"status": "active"})
    await callback.answer("▶️ Группа возобновлена")
    grp = get_group_by_id(gid)
    main = next(w for w in grp["wallets"] if w["is_main"])
    await callback.message.edit_text(
        f"📁 {grp['name']} ({gid})\n💰 Main‑баланс: {main['balance']:.6f} TRX",
        reply_markup=group_actions_kb(gid, "active")
    )


@router.callback_query(F.data.startswith("collect_trx_"))
async def collect_trx(callback: CallbackQuery):
    gid = callback.data.split("_",2)[2]
    grp = get_group_by_id(gid)
    main = next(w for w in grp["wallets"] if w["is_main"])
    total = 0.0
    await callback.answer("💸 Собираем TRX...", show_alert=False)
    wallets = update_wallet_balances(gid)
    for w in wallets:
        if w["is_main"] or w["balance"] <= 0:
            continue
        bal = w["balance"]
        fee = send_trx(w["address"], w["private_key_enc"], main["address"], bal)
        collected = bal - fee
        if collected <= 0:
            logger.warning(
                "⚠️ Пропускаем сбор с %s: комиссия=%.6f TRX ≥ баланс=%.6f TRX",
                w["address"], fee, bal
            )
            continue
        total += collected
        record_transaction(gid, 0.0, fee)
    update_wallet_balances(gid)
    await callback.message.edit_text(
        f"💸 TRX собрано: {total:.6f} TRX на MAIN ({main['address']})",
        reply_markup=group_actions_kb(gid, grp["status"])
    )


@router.callback_query(F.data.startswith("collect_usdt_"))
async def collect_usdt(callback: CallbackQuery):
    gid = callback.data.split("_", 2)[2]
    grp = get_group_by_id(gid)
    main = next(w for w in grp["wallets"] if w["is_main"])
    total = 0.0
    await callback.answer("💵 Сбор USDT...", show_alert=False)
    for w in grp["wallets"]:
        if not w["is_main"] and w["balance"] > 0:
            fee = send_usdt(w["address"], w["private_key_enc"], main["address"], w["balance"])
            total += w["balance"]
            record_transaction(gid, w["balance"], fee)
    update_wallet_balances(gid)
    await callback.message.edit_text(
        f"💵 USDT собрано: {total:.6f} на MAIN",
        reply_markup=group_actions_kb(gid, grp["status"])
    )


@router.callback_query(F.data.startswith("topup_"))
async def topup_group(callback: CallbackQuery):
    """
    Равномерно распределяет общий баланс всех кошельков группы
    (включая MAIN) так, чтобы в итоге у каждого было поровну.
    """
    gid = callback.data.split("_", 1)[1]
    grp = get_group_by_id(gid)
    if not grp:
        return await callback.answer("❌ Группа не найдена!", show_alert=True)

    # 1) Подтягиваем актуальные балансы всех кошельков
    wallets = update_wallet_balances(gid)
    main = next(w for w in wallets if w["is_main"])
    targets = wallets  # все кошельки, в т.ч. main

    count = len(targets)
    if count == 0:
        return await callback.answer("❌ Нет кошельков в группе.", show_alert=True)

    # 2) Вычисляем итоговую равную долю (target) как среднее всех балансов
    total_all = sum(w["balance"] for w in targets)
    target = round(total_all / count, 6)
    if target <= 0:
        return await callback.answer("❌ Недостаточно TRX для распределения.", show_alert=True)

    await callback.answer(
        f"💳 Распределяем {total_all:.6f} TRX на {count} кошельков по {target:.6f} TRX...",
        show_alert=False
    )

    # 3) Отправляем недостающую часть каждому, кроме MAIN (на MAIN останется target)
    for w in targets:
        if w["is_main"]:
            continue
        diff = round(target - w["balance"], 6)
        if diff <= 0:
            logger.info("🟡 У %s уже ≥ %s TRX (текущий %.6f), пропускаем", w["address"], target, w["balance"])
            continue
        try:
            fee = send_trx(main["address"], main["private_key_enc"], w["address"], diff)
            record_transaction(gid, 0.0, fee)
        except ValidationError as e:
            logger.warning("⚠️ Не удалось пополнить %s: %s", w["address"], e)
        except UnknownError as e:
            msg, code = e.args
            if code == "BANDWITH_ERROR":
                logger.warning("⚠️ Недостаточно Bandwidth у %s, пропускаем", main["address"])
            else:
                logger.error("🔥 Ошибка пополнения: %s", e, exc_info=True)

    # 4) Сохраняем и показываем результат
    update_wallet_balances(gid)
    await callback.message.edit_text(
        f"✅ Пополнение завершено: теперь у каждого {target:.6f} TRX",
        reply_markup=group_actions_kb(gid, grp["status"])
    )