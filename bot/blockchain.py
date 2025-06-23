# bot/blockchain.py
import random
from tronpy import Tron
from tronpy.keys import PrivateKey

from bot.security import SecurityManager
from bot.utils import update_wallet_balances, record_transaction, get_group_by_id

tron = Tron()

def send_trx(from_addr: str, priv_key_dec: str, to_addr: str, amount_trx: float) -> float:
    """
    Отправляет TRX и возвращает комиссию в TRX.
    """
    priv = PrivateKey(bytes.fromhex(priv_key_dec))
    txn = (
        tron.trx.transfer(from_addr, to_addr, int(amount_trx * 1_000_000))
        .build()
        .inspect()
        .sign(priv)
    )
    result = txn.broadcast().wait()
    fee = result["fee"] / 1_000_000
    return fee

def send_usdt(from_addr: str, priv_key_dec: str, to_addr: str, amount_usdt: float) -> float:
    """
    Отправляет USDT (TRC20); возвращает комиссию в TRX.
    """
    priv = PrivateKey(bytes.fromhex(priv_key_dec))
    contract = tron.get_contract("TLa2f6VPqDgRE67v1736s7bJ8Ray5wYjU7")  # USDT TRC20
    txn = (
        contract.functions.transfer(to_addr, int(amount_usdt * 1_000_000))
        .with_owner(from_addr)
        .build()
        .sign(priv)
    )
    result = txn.broadcast().wait()
    fee = result["fee"] / 1_000_000
    return fee

def _get_wallets(group_id: str) -> list[dict]:
    grp = get_group_by_id(group_id)
    return grp["wallets"] if grp else []

def random_warmup(group_id: str, main_percent: int, amount_trx: float):
    """
    Случайные транзакции внутри группы.
    main_percent — вероятность участия main‑кошелька.
    """
    wallets = _get_wallets(group_id)
    wallets = sorted(wallets, key=lambda w: not w["is_main"])
    for w in wallets:
        if random.randint(1,100) <= main_percent or not w["is_main"]:
            to = random.choice([x for x in wallets if x["address"]!=w["address"]])
            fee = send_trx(w["address"], SecurityManager.decrypt_data(w["private_key_enc"]), to["address"], amount_trx)
            record_transaction(group_id, 0.0, fee)
    update_wallet_balances(group_id)

def circular_warmup(group_id: str, amount_trx: float):
    """
    Круговой прогрев: i → i+1 → ... → last → first.
    """
    wallets = _get_wallets(group_id)
    n = len(wallets)
    for i in range(n):
        frm = wallets[i]
        to = wallets[(i+1)%n]
        fee = send_trx(frm["address"], SecurityManager.decrypt_data(frm["private_key_enc"]), to["address"], amount_trx)
        record_transaction(group_id, 0.0, fee)
    update_wallet_balances(group_id)

def mainchain_warmup(group_id: str, amount_trx: float):
    """
    MAIN → второй → остальные → MAIN.
    """
    wallets = _get_wallets(group_id)
    main = next(w for w in wallets if w["is_main"])
    others = [w for w in wallets if not w["is_main"]]
    sequence = [main] + others + [main]
    for i in range(len(sequence)-1):
        frm = sequence[i]
        to = sequence[i+1]
        fee = send_trx(frm["address"], SecurityManager.decrypt_data(frm["private_key_enc"]), to["address"], amount_trx)
        record_transaction(group_id, 0.0, fee)
    update_wallet_balances(group_id)