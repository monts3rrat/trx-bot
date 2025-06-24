# bot/states.py
from aiogram.fsm.state import State, StatesGroup

class AuthState(StatesGroup):
    waiting_pin = State()

class GroupState(StatesGroup):
    creating_name = State()
    creating_wallets = State()

class LimitState(StatesGroup):
    waiting_limit = State()

class WarmupState(StatesGroup):
    selecting_group = State()
    selecting_method = State()

class SettingsState(StatesGroup):
    main_menu = State()
    night_mode = State()