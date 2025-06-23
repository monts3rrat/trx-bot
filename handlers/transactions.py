# handlers/transactions.py
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

from bot.blockchain import send_trx, send_usdt
from bot.utils import update_wallet_balances, record_transaction, get_group_by_id

router = Router()

@router.message(Command("collect_trx"))
async def collect_trx_cmd(message: Message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        return await message.answer("Используйте: /collect_trx <group_id>")
    gid = parts[1].strip()
    grp = get_group_by_id(gid)
    if not grp:
        return await message.answer("❌ Группа не найдена!")
    main = next(w for w in grp["wallets"] if w["is_main"])
    total = 0.0
    for w in grp["wallets"]:
        if not w["is_main"]:
            fee = send_trx(w["address"], w["private_key_enc"], main["address"], w["balance"])
            total += w["balance"] - fee
            record_transaction(gid, 0.0, fee)
    update_wallet_balances(gid)
    await message.answer(f"💸 TRX собрано: {total:.6f} TRX на MAIN.")

@router.message(Command("collect_usdt"))
async def collect_usdt_cmd(message: Message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        return await message.answer("Используйте: /collect_usdt <group_id>")
    gid = parts[1].strip()
    grp = get_group_by_id(gid)
    if not grp:
        return await message.answer("❌ Группа не найдена!")
    main = next(w for w in grp["wallets"] if w["is_main"])
    total = 0.0
    for w in grp["wallets"]:
        if not w["is_main"]:
            fee = send_usdt(w["address"], w["private_key_enc"], main["address"], w["balance"])
            total += w["balance"]
            record_transaction(gid, w["balance"], fee)
    update_wallet_balances(gid)
    await message.answer(f"💵 USDT собрано: {total:.6f} USDT на MAIN.")