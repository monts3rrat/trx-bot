# bot/utils.py
import json
import os
from tronpy import Tron

from bot.config import config

def load_dummy_data() -> dict:
    if not os.path.exists(config.DATA_FILE):
        return {"groups": [], "statistics": {}}
    with open(config.DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_dummy_data(data: dict):
    os.makedirs(os.path.dirname(config.DATA_FILE), exist_ok=True)
    with open(config.DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def get_group_by_id(group_id: str) -> dict | None:
    data = load_dummy_data()
    for grp in data.get("groups", []):
        if grp["id"] == group_id:
            return grp
    return None

def add_group(group: dict):
    data = load_dummy_data()
    data.setdefault("groups", []).append(group)
    save_dummy_data(data)

def update_group(group_id: str, update_data: dict) -> bool:
    data = load_dummy_data()
    for i, grp in enumerate(data.get("groups", [])):
        if grp["id"] == group_id:
            data["groups"][i].update(update_data)
            save_dummy_data(data)
            return True
    return False

def update_wallet_balances(group_id: str) -> list[dict]:
    """
    Синхронизирует баланс каждого кошелька группы с сетью TRON и сохраняет в JSON.
    """
    tron = Tron()
    data = load_dummy_data()
    for grp in data.get("groups", []):
        if grp["id"] == group_id:
            for w in grp.get("wallets", []):
                try:
                    sun = tron.get_account_balance(w["address"])
                    w["balance"] = sun / 1_000_000
                except Exception:
                    pass
            save_dummy_data(data)
            return grp["wallets"]
    return []

def record_transaction(group_id: str, usdt: float, trx_fee: float):
    data = load_dummy_data()
    stats = data.setdefault("statistics", {"total_transactions":0, "total_usdt":0.0, "total_trx":0.0})
    stats["total_transactions"] += 1
    stats["total_usdt"] += usdt
    stats["total_trx"] += trx_fee
    save_dummy_data(data)

def get_next_group_id() -> str:
    data = load_dummy_data()
    count = len(data.get("groups", [])) + 1
    return f"group_{count}"