# handlers/common.py
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.filters import Command

from bot.keyboards import main_menu_kb, back_to_main_kb
from bot.utils import find_groups, add_favorite, remove_favorite, get_favorites, load_dummy_data, add_history

router = Router()

@router.callback_query(F.data == "main_menu")
async def back_to_main(callback: CallbackQuery):
    await callback.message.edit_text("Главное меню:", reply_markup=main_menu_kb())

@router.message(Command("search"))
async def cmd_search(message: Message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        return await message.answer("Использование: /search <имя или ID>")
    matches = find_groups(parts[1])
    if not matches:
        return await message.answer("❌ Группы не найдены.")
    text = "🔎 Результаты поиска:\n" + "\n".join(f"{g['name']} ({g['id']})" for g in matches)
    await message.answer(text)

@router.message(Command("favorites"))
async def cmd_favorites(message: Message):
    fav = get_favorites()
    if not fav:
        return await message.answer("⭐ Список избранных пуст.")
    data = load_dummy_data()
    groups = {g["id"]: g for g in data["groups"]}
    text = "⭐ Избранные группы:\n" + "\n".join(f"{groups[g]['name']} ({g})" for g in fav if g in groups)
    await message.answer(text)

@router.callback_query(F.data.startswith("fav_"))
async def toggle_fav(callback: CallbackQuery):
    gid = callback.data.split("_",1)[1]
    fav = get_favorites()
    if gid in fav:
        remove_favorite(gid)
        await callback.answer("Группа удалена из избранного")
    else:
        add_favorite(gid)
        await callback.answer("Группа добавлена в избранное")
    # обновляем меню группы
    from bot.utils import get_group_by_id
    from bot.keyboards import group_actions_kb
    grp = get_group_by_id(gid)
    await callback.message.edit_reply_markup(reply_markup=group_actions_kb(gid, grp["status"]))

@router.message(Command("history"))
async def cmd_history(message: Message):
    hist = load_dummy_data().get("history", [])[:10]
    if not hist:
        return await message.answer("📜 История пуста.")
    text = "📜 История последних действий:\n" + "\n".join(
        f"{h['time']} | grp:{h['group_id']} | usdt={h['usdt']:.6f} | fee={h['trx_fee']:.6f}"
        for h in hist
    )
    await message.answer(text)