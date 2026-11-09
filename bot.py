import asyncio
import json
import random
import os
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

# ================== НАСТРОЙКИ ==================
BOT_TOKEN = "9218686222:AAFpEP0sPlyurUV_hMWzfUnaK3ysE1OTxhw"
ADMIN_ID = 7510323045

STICKERS_FILE = "stickers.json"

PHRASE = "Ты крутышка коротышка 🤍"

# ================== БОТ ==================
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


def load_stickers() -> list:
    if not os.path.exists(STICKERS_FILE):
        return []
    try:
        with open(STICKERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def save_stickers(data: list):
    with open(STICKERS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def gift_keyboard():
    kb = InlineKeyboardBuilder()
    kb.button(text="🎁 Открыть подарок", callback_data="open_gift")
    return kb.as_markup()


# ================== ПОЛЬЗОВАТЕЛЬ ==================
@dp.message(CommandStart())
async def start(message: Message):
    stickers = load_stickers()
    if not stickers:
        if message.from_user.id == ADMIN_ID:
            await message.answer(
                "👋 Привет, админ!\n\n"
                "Стикеров пока нет. Просто пришли мне любой стикер — я его запомню.\n"
                "Команды: /stickers — список, /del — удалить последний, /clear — очистить."
            )
        else:
            await message.answer("🎁 Скоро тут появится подарок. Загляни чуть позже 🤍")
        return

    await message.answer(
        "🎁 <b>Тебе подарок!</b>\n\n"
        "Внутри что-то маленькое и милое.\n"
        "Нажми кнопку, чтобы открыть 👇",
        parse_mode="HTML",
        reply_markup=gift_keyboard(),
    )


@dp.callback_query(F.data == "open_gift")
async def open_gift(call: CallbackQuery):
    stickers = load_stickers()
    if not stickers:
        await call.answer("Подарков пока нет 🙈", show_alert=True)
        return

    await call.answer("Открываем... 🎉")

    try:
        await call.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass

    await call.message.answer_sticker(random.choice(stickers))
    await call.message.answer(PHRASE)


# ================== АДМИН-ПАНЕЛЬ ==================
@dp.message(F.sticker)
async def add_sticker(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    stickers = load_stickers()
    fid = message.sticker.file_id

    if fid in stickers:
        await message.answer("Этот стикер уже есть в подарках 🙂")
        return

    stickers.append(fid)
    save_stickers(stickers)
    await message.answer(f"✅ Стикер добавлен! Всего подарков: {len(stickers)}")


@dp.message(Command("stickers"))
async def list_stickers(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    stickers = load_stickers()
    if not stickers:
        await message.answer("Список пуст. Пришли стикер, чтобы добавить.")
        return

    await message.answer(f"📦 Подарков в базе: {len(stickers)}")
    for fid in stickers:
        try:
            await message.answer_sticker(fid)
        except Exception:
            await message.answer("⚠️ стикер недоступен")


@dp.message(Command("del"))
async def del_last(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    stickers = load_stickers()
    if not stickers:
        await message.answer("Удалять нечего.")
        return

    stickers.pop()
    save_stickers(stickers)
    await message.answer(f"🗑 Удалён последний стикер. Осталось: {len(stickers)}")


@dp.message(Command("clear"))
async def clear_all(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    save_stickers([])
    await message.answer("🧹 Все подарки удалены.")


@dp.message(Command("help"))
async def help_cmd(message: Message):
    if message.from_user.id == ADMIN_ID:
        await message.answer(
            "Админ-команды:\n"
            "• пришли стикер — добавить в подарки\n"
            "/stickers — список\n"
            "/del — удалить последний\n"
            "/clear — очистить всё"
        )
    else:
        await message.answer("Просто зайди в бота — тебя ждёт подарок 🎁")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())