# bot/blockchain.py
import logging
import random
import asyncio
import time

from tronpy import Tron
from tronpy.providers import HTTPProvider
from tronpy.keys import PrivateKey
from tronpy.exceptions import ValidationError, UnknownError

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

_provider = HTTPProvider(
    endpoint_uri="https://api.trongrid.io",
    api_key=config.TRONGRID_API_KEY
)
tron = Tron(network=config.TRON_NETWORK, provider=_provider)



def send_trx(from_addr: str, priv_key_enc: str, to_addr: str, amount_trx: float) -> float:
    try:
        priv = PrivateKey(bytes.fromhex(SecurityManager.decrypt_data(priv_key_enc)))
    
        time.sleep(1.5)

        acct = tron.get_account(from_addr)
        balance = acct.get("balance", 0) / 1_000_000
        
        MIN_MARGIN_TRX = 0.4
        if balance <= MIN_MARGIN_TRX:
            logger.warning("⚠️ Баланс %.6f TRX слишком мал для отправки с %s", balance, from_addr)
            return 0.0
        
        send_amt = min(amount_trx, balance - MIN_MARGIN_TRX)
        
        sun_amount = int(send_amt * 1_000_000)
        if sun_amount <= 0:
            logger.warning("⚠️ Недостаточный баланс после маржи %.6f TRX для %s", send_amt, from_addr)
            return 0.0
        
        logger.info("↗ Отправляем %.6f TRX: %s → %s", send_amt, from_addr, to_addr)
        
        txn = tron.trx.transfer(from_addr, to_addr, sun_amount)
        built_txn = txn.build()
        signed_txn = built_txn.sign(priv)
        broadcasted_txn = signed_txn.broadcast().wait()
        
        receipt = broadcasted_txn.get("receipt", {}) or {}
        
        fee = (receipt.get("energy_fee", 0) + receipt.get("net_fee", 0)) / 1_000_000
        logger.info("✅ TRX успешно отправлен, комиссия = %.6f TRX", fee)
        
        gid = get_group_id_by_address(from_addr)
        if gid:
            record_transaction(gid, 0.0, fee)
            update_wallet_balances(gid)
            
        return fee

    except ValidationError as e:
        logger.warning("⚠️ ValidationError (недостаточный баланс): %s → %s: %s", from_addr, to_addr, e)
        return 0.0

    except UnknownError as e:
        msg, code = e.args
        if code == "BANDWITH_ERROR":
            logger.warning("⚠️ Недостаточно Bandwidth для операции (%s)", from_addr)
        else:
            logger.error("🔥 Ошибка транзакции: %s", e, exc_info=True)
        return 0.0

    except Exception as e:
        logger.error("🔥 Необработанная ошибка в send_trx: %s", e, exc_info=True)
        return 0.0


def send_usdt(from_addr: str, priv_key_enc: str, to_addr: str, amount_usdt: float) -> float:
    """
    Отправка USDT (TRC20) с аналогичной обработкой ошибок.
    """
    try:
        priv = PrivateKey(bytes.fromhex(SecurityManager.decrypt_data(priv_key_enc)))
        contract = tron.get_contract(config.USDT_CONTRACT_ADDRESS)
        sun_amount = int(amount_usdt * 1_000_000)
        if sun_amount <= 0:
            logger.warning("⚠️ Пропускаем %.6f USDT", amount_usdt)
            return 0.0

        logger.info("↗ Отправляем %.6f USDT: %s → %s", amount_usdt, from_addr, to_addr)
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

        gid = get_group_id_by_address(from_addr)
        if gid:
            record_transaction(gid, amount_usdt, fee)
            update_wallet_balances(gid)
        return fee

    except Exception as e:
        logger.error("🔥 Ошибка send_usdt: %s", e, exc_info=True)
        return 0.0


async def trx_only_warmup(group_id: str):
    grp = get_group_by_id(group_id)
    logger.info("🔧 TRX-only warmup для %s", group_id)
    if not check_and_increment_daily(group_id):
        logger.warning("❌ Дневной лимит исчерпан для %s", group_id)
        return

    wallets = grp["wallets"]
    main = next(w for w in wallets if w["is_main"])
    for w in wallets:
        if w["is_main"] or w["balance"] <= 0:
            continue
        fee = send_trx(w["address"], w["private_key_enc"], main["address"], w["balance"])
        record_transaction(group_id, 0.0, fee)
        update_wallet_balances(group_id)
        await asyncio.sleep(random.uniform(grp["trx_interval_min"] * 60, grp["trx_interval_max"] * 60))


def random_warmup(group_id: str):
    """
    🎲 Random warmup:
    Берём свежие балансы, каждому не-main кошельку шлём всю сумму (или 1 sun),
    пропуская ошибки, затем единоразово обновляем балансы.
    """
    logger.info("🚀 Запуск Random warmup для %s", group_id)
    wallets = update_wallet_balances(group_id)
    for w in wallets:
        if w["is_main"] or w["balance"] <= 0:
            continue
        target = random.choice([x for x in wallets if x["address"] != w["address"]])
        sun_amount = int(w["balance"] * 1_000_000) or 1
        send_trx(w["address"], w["private_key_enc"], target["address"], min(w["balance"], sun_amount / 1_000_000))
    update_wallet_balances(group_id)


def circular_warmup(group_id: str):
    wallets = update_wallet_balances(group_id)
    logger.info("🚀 Запуск Circular warmup для %s", group_id)
    for i in range(len(wallets)):
        frm = wallets[i]
        to = wallets[(i + 1) % len(wallets)]
        if frm["balance"] <= 0:
            continue
        sun_amount = int(frm["balance"] * 1_000_000) or 1
        send_trx(frm["address"], frm["private_key_enc"], to["address"], sun_amount / 1_000_000)
    update_wallet_balances(group_id)


def mainchain_warmup(group_id: str):
    wallets = update_wallet_balances(group_id)
    logger.info("🚀 Запуск Main-chain warmup для %s", group_id)
    main = next(w for w in wallets if w["is_main"])
    seq = [main] + [w for w in wallets if not w["is_main"]] + [main]
    for i in range(len(seq) - 1):
        frm, to = seq[i], seq[i + 1]
        if frm["balance"] <= 0:
            continue
        sun_amount = int(frm["balance"] * 1_000_000) or 1
        send_trx(frm["address"], frm["private_key_enc"], to["address"], sun_amount / 1_000_000)
    update_wallet_balances(group_id)