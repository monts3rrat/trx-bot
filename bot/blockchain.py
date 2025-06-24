# bot/blockchain.py
import logging
import random
import asyncio
from tronpy import Tron
from tronpy.keys import PrivateKey

from bot.config import config
from bot.security import SecurityManager
from bot.utils import (
    record_transaction,
    get_group_id_by_address,
    update_wallet_balances,
    get_group_by_id,
    check_and_increment_daily
)

logger = logging.getLogger(__name__)
tron = Tron(network=config.TRON_NETWORK)

def send_trx(from_addr: str, priv_key_enc: str, to_addr: str, amount_trx: float) -> float:
    try:
        priv = PrivateKey(bytes.fromhex(SecurityManager.decrypt_data(priv_key_enc)))
        balance = float(tron.get_account_balance(from_addr)) / 1_000_000
        sun_amount = int(amount_trx * 1_000_000)
        if sun_amount <= 0 or balance < amount_trx:
            logger.warning(
                "⚠️ Пропускаем отправку %.6f TRX с %s (баланс=%.6f)",
                amount_trx, from_addr, balance
            )
            return 0.0

        logger.info("↗ Отправляем %.6f TRX с %s → %s", amount_trx, from_addr, to_addr)
        txn = tron.trx.transfer(from_addr, to_addr, sun_amount).build().inspect().sign(priv)
        res = txn.broadcast().wait()

        receipt = res.get("receipt", {}) or {}
        fee = (receipt.get("energy_fee", 0) + receipt.get("net_fee", 0)) / 1_000_000
        logger.info("✅ TRX TX выполнена, комиссия=%.6f TRX", fee)

        grp_id = get_group_id_by_address(from_addr)
        if grp_id:
            record_transaction(grp_id, 0.0, fee)
            update_wallet_balances(grp_id)
        else:
            logger.error("❌ Не нашли группу для адреса %s", from_addr)
        return fee

    except Exception as e:
        logger.error("🔥 Ошибка send_trx: %s", e, exc_info=True)
        return 0.0

def send_usdt(from_addr: str, priv_key_enc: str, to_addr: str, amount_usdt: float) -> float:
    try:
        priv = PrivateKey(bytes.fromhex(SecurityManager.decrypt_data(priv_key_enc)))
        contract = tron.get_contract(config.USDT_CONTRACT_ADDRESS)
        sun_amount = int(amount_usdt * 1_000_000)
        if sun_amount <= 0:
            logger.warning("⚠️ Пропускаем TX USDT %.6f", amount_usdt)
            return 0.0

        logger.info("↗ Отправляем %.6f USDT с %s → %s", amount_usdt, from_addr, to_addr)
        txn = (
            contract.functions.transfer(to_addr, sun_amount)
            .with_owner(from_addr)
            .build()
            .sign(priv)
        )
        res = txn.broadcast().wait()

        receipt = res.get("receipt", {}) or {}
        fee = (receipt.get("energy_fee", 0) + receipt.get("net_fee", 0)) / 1_000_000
        logger.info("✅ USDT TX выполнена, комиссия=%.6f TRX", fee)

        grp_id = get_group_id_by_address(from_addr)
        if grp_id:
            record_transaction(grp_id, amount_usdt, fee)
            update_wallet_balances(grp_id)
        else:
            logger.error("❌ Не нашли группу для адреса %s", from_addr)
        return fee

    except Exception as e:
        logger.error("🔥 Ошибка send_usdt: %s", e, exc_info=True)
        return 0.0


def random_warmup(group_id: str):
    grp = get_group_by_id(group_id)
    wallets = grp["wallets"]
    logger.info("🚀 Запуск Random warmup для %s", group_id)
    for w in wallets:
        if w["balance"] <= 0:
            continue
        # Всегда отсылаем полный баланс
        target = random.choice([x for x in wallets if x["address"] != w["address"]])
        sun_amount = int(w["balance"] * 1_000_000) or 1
        send_trx(w["address"], w["private_key_enc"], target["address"], sun_amount / 1_000_000)
    update_wallet_balances(group_id)


def circular_warmup(group_id: str):
    wallets = get_group_by_id(group_id)["wallets"]
    logger.info("🚀 Запуск Circular warmup для %s", group_id)
    for i in range(len(wallets)):
        frm = wallets[i]
        to = wallets[(i + 1) % len(wallets)]
        amount = frm["balance"] if random.choice([True, False]) else frm["balance"] / 2
        if amount <= 0:
            continue
        send_trx(frm["address"], frm["private_key_enc"], to["address"], amount)
    update_wallet_balances(group_id)

def mainchain_warmup(group_id: str):
    wallets = get_group_by_id(group_id)["wallets"]
    main = next(w for w in wallets if w["is_main"])
    others = [w for w in wallets if not w["is_main"]]
    seq = [main] + others + [main]
    logger.info("🚀 Запуск Main-chain warmup для %s", group_id)
    for i in range(len(seq) - 1):
        frm, to = seq[i], seq[i + 1]
        amount = frm["balance"] if random.choice([True, False]) else frm["balance"] / 2
        if amount <= 0:
            continue
        send_trx(frm["address"], frm["private_key_enc"], to["address"], amount)
    update_wallet_balances(group_id)


async def trx_only_warmup(group_id: str):
    grp = get_group_by_id(group_id)
    logger.info("🔧 TRX-only warmup для %s", group_id)
    # проверяем дневной лимит по количеству TX
    if not check_and_increment_daily(group_id):
        logger.warning("❌ Дневной лимит исчерпан для %s", group_id)
        return
    wallets = grp["wallets"]
    main = next(w for w in wallets if w["is_main"])
    for w in wallets:
        if w["is_main"] or w["balance"] <= 0:
            continue
        amount = w["balance"]
        fee = send_trx(w["address"], w["private_key_enc"], main["address"], amount)
        record_transaction(group_id, 0.0, fee)
        update_wallet_balances(group_id)
        # ждём случайный интервал между транзакциями (минуты → секунды)
        interval_min = grp["trx_interval_min"] * 60
        interval_max = grp["trx_interval_max"] * 60
        wait_sec = random.uniform(interval_min, interval_max)
        logger.info("⏱ Ждём %.1f сек перед следующей транзакцией", wait_sec)
        await asyncio.sleep(wait_sec)