from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton
from bot.utils import load_dummy_data

def main_menu_kb():
    b = InlineKeyboardBuilder()
    b.row(
        InlineKeyboardButton(text="📁 Группы", callback_data="groups"),
        InlineKeyboardButton(text="📊 Статистика", callback_data="stats")
    )
    b.row(
        InlineKeyboardButton(text="🔁 Прогрев", callback_data="warmup")
    )
    return b.as_markup()

def groups_menu_kb():
    b = InlineKeyboardBuilder()
    b.row(
        InlineKeyboardButton(text="➕ Создать", callback_data="create_group"),
        InlineKeyboardButton(text="📋 Список", callback_data="groups_list")
    )
    b.row(InlineKeyboardButton(text="🔙 Назад", callback_data="main_menu"))
    return b.as_markup()

def back_to_main_kb():
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text="🔙 Главное меню", callback_data="main_menu"))
    return b.as_markup()

def groups_list_kb():
    b = InlineKeyboardBuilder()
    for grp in load_dummy_data().get("groups", []):
        b.row(
            InlineKeyboardButton(
                text=f"{grp['name']} ({grp['id']})",
                callback_data=f"group_{grp['id']}"
            )
        )
    b.row(InlineKeyboardButton(text="🔙 Назад", callback_data="groups"))
    return b.as_markup()

def group_actions_kb(group_id: str, status: str):
    from bot.keyboards import back_to_main_kb  # avoid circular import in stats handler
    b = InlineKeyboardBuilder()
    b.row(
        InlineKeyboardButton(text="🔁 Прогрев",    callback_data=f"warmup_{group_id}"),
        InlineKeyboardButton(text="📊 Статистика", callback_data=f"stats_{group_id}")
    )
    b.row(
        InlineKeyboardButton(text="✏️ Изменить лимит", callback_data=f"limit_{group_id}"),
        InlineKeyboardButton(text="💳 Пополнить",       callback_data=f"topup_{group_id}")
    )
    if status == "active":
        b.row(InlineKeyboardButton(text="⏸️ Пауза", callback_data=f"pause_{group_id}"))
    else:
        b.row(InlineKeyboardButton(text="▶️ Возобновить", callback_data=f"resume_{group_id}"))
    b.row(
        InlineKeyboardButton(text="💸 Собрать TRX",   callback_data=f"collect_trx_{group_id}"),
        InlineKeyboardButton(text="💵 Собрать USDT",  callback_data=f"collect_usdt_{group_id}")
    )
    b.row(
        InlineKeyboardButton(text="❌ Удалить", callback_data=f"delete_{group_id}"),
        InlineKeyboardButton(text="🔙 К списку", callback_data="groups_list")
    )
    return b.as_markup()

def warmup_methods_kb(group_id: str):
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text="🎲 Рандом",      callback_data=f"method_random_{group_id}"))
    b.row(InlineKeyboardButton(text="🔄 Круговой",    callback_data=f"method_circle_{group_id}"))
    b.row(InlineKeyboardButton(text="⭐ MAIN‑цепочка", callback_data=f"method_main_{group_id}"))
    b.row(InlineKeyboardButton(text="💧 TRX‑only",    callback_data=f"method_trx_{group_id}"))
    b.row(InlineKeyboardButton(text="🔙 Назад",       callback_data="warmup"))
    return b.as_markup()

def ready_kb():
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text="✅ Готово", callback_data="wallets_ready"))
    return b.as_markup()

def settings_menu_kb():
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text="🌙 Ночной режим", callback_data="night_mode"))
    b.row(InlineKeyboardButton(text="🔙 Назад",       callback_data="main_menu"))
    return b.as_markup()

def night_mode_kb():
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text="Вкл 🌙", callback_data="night_mode_on"))
    b.row(InlineKeyboardButton(text="Выкл ☀️", callback_data="night_mode_off"))
    b.row(InlineKeyboardButton(text="🔙 Назад", callback_data="settings"))
    return b.as_markup()