# bot/keyboards.py
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton
from bot.utils import load_dummy_data


def main_menu_kb():
    b = InlineKeyboardBuilder()
    b.row(
        InlineKeyboardButton(text="📁 Группы", callback_data="groups"),
        InlineKeyboardButton(text="🔁 Прогрев", callback_data="warmup")
    )
    b.row(
        InlineKeyboardButton(text="📊 Статистика", callback_data="stats"),
        InlineKeyboardButton(text="⚙️ Настройки", callback_data="settings")
    )
    return b.as_markup()


def groups_menu_kb():
    b = InlineKeyboardBuilder()
    b.row(
        InlineKeyboardButton(text="➕ Создать", callback_data="create_group"),
        InlineKeyboardButton(text="📋 Список", callback_data="groups_list")
    )
    b.row(
        InlineKeyboardButton(text="🔙 Назад", callback_data="main_menu")
    )
    return b.as_markup()


def back_to_main_kb():
    """
    Кнопка возврата в главное меню
    """
    b = InlineKeyboardBuilder()
    b.row(
        InlineKeyboardButton(text="🔙 Главное меню", callback_data="main_menu")
    )
    return b.as_markup()


def groups_list_kb():
    b = InlineKeyboardBuilder()
    data = load_dummy_data()
    for grp in data.get("groups", []):
        b.row(
            InlineKeyboardButton(
                text=f"{grp['name']} ({grp['id']})",
                callback_data=f"group_{grp['id']}"
            )
        )
    b.row(
        InlineKeyboardButton(text="🔙 Назад", callback_data="groups")
    )
    return b.as_markup()


def group_actions_kb(group_id: str):
    b = InlineKeyboardBuilder()
    b.row(
        InlineKeyboardButton(text="⏸️ Пауза", callback_data=f"pause_{group_id}"),
        InlineKeyboardButton(text="▶️ Продолжить", callback_data=f"resume_{group_id}")
    )
    b.row(
        InlineKeyboardButton(text="💸 Собрать TRX", callback_data=f"collect_trx_{group_id}"),
        InlineKeyboardButton(text="💵 Собрать USDT", callback_data=f"collect_usdt_{group_id}")
    )
    b.row(
        InlineKeyboardButton(text="❌ Удалить", callback_data=f"delete_{group_id}"),
        InlineKeyboardButton(text="🔙 Назад", callback_data="groups_list")
    )
    return b.as_markup()


def warmup_methods_kb(group_id: str):
    b = InlineKeyboardBuilder()
    b.row(
        InlineKeyboardButton(text="🎲 Рандом", callback_data=f"method_random_{group_id}")
    )
    b.row(
        InlineKeyboardButton(text="🔄 Круговой", callback_data=f"method_circle_{group_id}")
    )
    b.row(
        InlineKeyboardButton(text="⭐ MAIN‑цепочка", callback_data=f"method_main_{group_id}")
    )
    b.row(
        InlineKeyboardButton(text="🔙 Назад", callback_data="warmup")
    )
    return b.as_markup()


def settings_menu_kb():
    b = InlineKeyboardBuilder()
    b.row(
        InlineKeyboardButton(text="🌙 Ночной режим", callback_data="night_mode")
    )
    b.row(
        InlineKeyboardButton(text="🔙 Назад", callback_data="main_menu")
    )
    return b.as_markup()


def night_mode_kb():
    b = InlineKeyboardBuilder()
    b.row(
        InlineKeyboardButton(text="Вкл 🌙", callback_data="night_mode_on")
    )
    b.row(
        InlineKeyboardButton(text="Выкл ☀️", callback_data="night_mode_off")
    )
    b.row(
        InlineKeyboardButton(text="🔙 Назад", callback_data="settings")
    )
    return b.as_markup()


def ready_kb():
    """
    Кнопка 'Готово' при вводе кошельков
    """
    b = InlineKeyboardBuilder()
    b.row(
        InlineKeyboardButton(text="✅ Готово", callback_data="wallets_ready")
    )
    return b.as_markup()