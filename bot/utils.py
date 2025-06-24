# bot/utils.py
import json
import os
from datetime import date, datetime
from tronpy import Tron

from bot.config import config

def load_dummy_data() -> dict:
    if not os.path.exists(config.DATA_FILE):
        return {
            "groups": [],
            "history": [],
            "statistics": {"total_transactions": 0, "total_usdt": 0.0, "total_trx": 0.0}
        }
    with open(config.DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    data.setdefault("history", [])
    data.setdefault("statistics", {"total_transactions": 0, "total_usdt": 0.0, "total_trx": 0.0})
    for grp in data.get("groups", []):
        grp.setdefault("wallets", [])
        grp.setdefault("status", "active")
        grp.setdefault("method", "random")
        grp.setdefault("main_percent", 30)

        grp.setdefault("daily_trx_limit", 10)
        grp.setdefault("trx_interval_min", 1)   
        grp.setdefault("trx_interval_max", 2)  
        grp.setdefault("statistics", {"total_transactions": 0, "total_usdt": 0.0, "total_trx": 0.0})
    return data

def save_dummy_data(data: dict):
    os.makedirs(os.path.dirname(config.DATA_FILE), exist_ok=True)
    with open(config.DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def get_group_by_id(group_id: str) -> dict | None:
    for grp in load_dummy_data().get("groups", []):
        if grp["id"] == group_id:
            return grp
    return None

def get_group_id_by_address(address: str) -> str | None:
    for grp in load_dummy_data().get("groups", []):
        for w in grp.get("wallets", []):
            if w["address"] == address:
                return grp["id"]
    return None

def find_groups(query: str) -> list[dict]:
    q = query.lower()
    return [
        grp for grp in load_dummy_data().get("groups", [])
        if q in grp["id"].lower() or q in grp["name"].lower()
    ]

def add_group(group: dict):
    data = load_dummy_data()
    data.setdefault("groups", []).append(group)
    save_dummy_data(data)

def update_group(group_id: str, update_data: dict) -> bool:
    data = load_dummy_data()
    for i, grp in enumerate(data.get("groups", [])):
        if grp["id"] == group_id:
            grp.update(update_data)
            data["groups"][i] = grp
            save_dummy_data(data)
            return True
    return False

def update_wallet_balances(group_id: str) -> list[dict]:
    tron = Tron(network=config.TRON_NETWORK)
    data = load_dummy_data()
    for i, grp in enumerate(data.get("groups", [])):
        if grp["id"] == group_id:
            for w in grp["wallets"]:
                try:
                    sun = tron.get_account_balance(w["address"])
                    w["balance"] = float(sun) / 1_000_000
                except Exception:
                    pass
            data["groups"][i] = grp
            save_dummy_data(data)
            return grp["wallets"]
    return []

def record_transaction(group_id: str, usdt: float, trx_fee: float):
    data = load_dummy_data()
    # глобальная статистика
    stats_all = data["statistics"]
    stats_all["total_transactions"] += 1
    stats_all["total_usdt"] += usdt
    stats_all["total_trx"] += trx_fee

    # статистика группы
    for grp in data["groups"]:
        if grp["id"] == group_id:
            gstats = grp["statistics"]
            # на всякий случай инициализируем
            gstats.setdefault("positive_tx", 0)
            gstats.setdefault("negative_tx", 0)
            gstats["total_transactions"] += 1
            gstats["total_usdt"] += usdt
            gstats["total_trx"] += trx_fee
            # плюс/минус транзакции
            if usdt > 0:
                gstats["positive_tx"] += 1
            else:
                gstats["negative_tx"] += 1
            break

    # история
    add_history({
        "time": datetime.now().isoformat(sep=" ", timespec="seconds"),
        "group_id": group_id,
        "usdt": usdt,
        "trx_fee": trx_fee
    })
    save_dummy_data(data)

def check_and_increment_daily(group_id: str) -> bool:
    data = load_dummy_data()
    for grp in data["groups"]:
        if grp["id"] == group_id:
            today = str(date.today())
            if grp["daily_trx_date"] != today:
                grp["daily_trx_date"] = today
                grp["daily_trx_count"] = 0
            if grp["daily_trx_count"] >= grp["daily_trx_limit"]:
                return False
            grp["daily_trx_count"] += 1
            save_dummy_data(data)
            return True
    return False

def add_history(event: dict):
    data = load_dummy_data()
    hist = data["history"]
    hist.insert(0, event)
    data["history"] = hist[:50]
    save_dummy_data(data)

def add_favorite(group_id: str):
    data = load_dummy_data()
    fav = data["favorites"]
    if group_id not in fav:
        fav.append(group_id)
    save_dummy_data(data)

def remove_favorite(group_id: str):
    data = load_dummy_data()
    data["favorites"] = [g for g in data["favorites"] if g != group_id]
    save_dummy_data(data)

def get_favorites() -> list[str]:
    return load_dummy_data().get("favorites", [])

def get_next_group_id() -> str:
    data = load_dummy_data()
    count = len(data.get("groups", [])) + 1
    return f"group_{count}"