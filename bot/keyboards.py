# bot\keyboards.py

from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.types import InlineKeyboardButton, KeyboardButton
from bot.utils import load_dummy_data

def main_menu_kb():
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="📁 Группы", callback_data="groups"),
        InlineKeyboardButton(text="🔁 Прогрев", callback_data="warmup")
    )
    builder.row(
        InlineKeyboardButton(text="📊 Статистика", callback_data="stats"),
        InlineKeyboardButton(text="⚙️ Настройки", callback_data="settings")
    )
    return builder.as_markup()

def groups_menu_kb():
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="➕ Создать группу", callback_data="create_group"),
        InlineKeyboardButton(text="📋 Список групп", callback_data="groups_list")
    )
    builder.row(
        InlineKeyboardButton(text="🔍 Поиск группы", callback_data="search_group"),
        InlineKeyboardButton(text="⭐ Избранное", callback_data="favorites")
    )
    builder.row(InlineKeyboardButton(text="🔙 Назад", callback_data="main_menu"))
    return builder.as_markup()

def group_actions_kb(group_id: str):
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="⏯️ Пауза", callback_data=f"pause_{group_id}"),
        InlineKeyboardButton(text="▶️ Продолжить", callback_data=f"resume_{group_id}")
    )
    builder.row(
        InlineKeyboardButton(text="💸 Собрать TRX", callback_data=f"collect_trx_{group_id}"),
        InlineKeyboardButton(text="📊 Статистика", callback_data=f"stats_{group_id}")
    )
    builder.row(
        InlineKeyboardButton(text="⚙️ Настройки", callback_data=f"settings_{group_id}"),
        InlineKeyboardButton(text="❌ Удалить", callback_data=f"delete_{group_id}")
    )
    builder.row(InlineKeyboardButton(text="🔙 Назад", callback_data="groups_list"))
    return builder.as_markup()

def warmup_methods_kb(group_id: str):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🎲 Рандомный", callback_data=f"method_random_{group_id}"))
    builder.row(InlineKeyboardButton(text="🔄 Круговой", callback_data=f"method_circle_{group_id}"))
    builder.row(InlineKeyboardButton(text="⭐ MAIN-цепочка", callback_data=f"method_main_{group_id}"))
    builder.row(InlineKeyboardButton(text="🔙 Назад", callback_data="warmup"))
    return builder.as_markup()

def back_to_main_kb():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🔙 Главное меню", callback_data="main_menu"))
    return builder.as_markup()

def back_to_groups_kb():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🔙 К группам", callback_data="groups"))
    return builder.as_markup()

def ready_kb():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="✅ Готово", callback_data="wallets_ready"))
    return builder.as_markup()

def groups_list_kb():
    builder = InlineKeyboardBuilder()
    data = load_dummy_data()
    
    for group in data["groups"]:
        builder.row(InlineKeyboardButton(
            text=f"{group['name']} ({group['id']})", 
            callback_data=f"group_{group['id']}")
        )
    
    builder.row(InlineKeyboardButton(text="🔙 Назад", callback_data="groups"))
    return builder.as_markup()

def settings_menu_kb():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🌙 Ночной режим", callback_data="night_mode"))
    builder.row(InlineKeyboardButton(text="🔐 Безопасность", callback_data="security_settings"))
    builder.row(InlineKeyboardButton(text="🔙 Назад", callback_data="main_menu"))
    return builder.as_markup()

def night_mode_kb():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Включить 🌙", callback_data="night_mode_on"))
    builder.row(InlineKeyboardButton(text="Выключить ☀️", callback_data="night_mode_off"))
    builder.row(InlineKeyboardButton(text="🔙 Назад", callback_data="settings"))
    return builder.as_markup()