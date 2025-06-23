# bot\utils.py

import json
import os
from bot.config import config

def load_dummy_data():
    try:
        if not os.path.exists(config.DATA_FILE):
            return {"groups": [], "statistics": {"total_transactions": 0, "total_usdt": 0.0, "total_trx": 0.0}}
            
        with open(config.DATA_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"groups": [], "statistics": {"total_transactions": 0, "total_usdt": 0.0, "total_trx": 0.0}}

def save_dummy_data(data):
    os.makedirs(os.path.dirname(config.DATA_FILE), exist_ok=True)
    with open(config.DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def get_group_by_id(group_id: str):
    data = load_dummy_data()
    for group in data["groups"]:
        if group["id"] == group_id:
            return group
    return None

def get_next_group_id():
    data = load_dummy_data()
    return f"group_{len(data['groups']) + 1}"

def add_group(group_data):
    data = load_dummy_data()
    data["groups"].append(group_data)
    save_dummy_data(data)

def update_group(group_id, update_data):
    data = load_dummy_data()
    for i, group in enumerate(data["groups"]):
        if group["id"] == group_id:
            data["groups"][i] = {**group, **update_data}
            save_dummy_data(data)
            return True
    return False