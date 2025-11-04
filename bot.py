import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from dotenv import load_dotenv
import asyncpg
from datetime import datetime, timedelta

# --- Загрузи переменные ---
load_dotenv()
API_TOKEN = os.getenv('API_TOKEN')
DB_DSN = os.getenv('DB_DSN')

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
db_pool = None
main_kb = ReplyKeyboardMarkup(resize_keyboard=True).add(
    KeyboardButton('🔍 Поиск облигаций'), KeyboardButton('👤 Профиль')
)

async def get_user(user_id):
    return await db_pool.fetchrow("SELECT * FROM users WHERE telegram_id=$1", user_id)

async def init_user(message):
    user = await get_user(message.from_user.id)
    if not user:
        invite_code = str(message.from_user.id) + str(int(datetime.now().timestamp()))[-4:]
        await db_pool.execute(
            "INSERT INTO users (telegram_id, username, invite_code, last_request) VALUES ($1,$2,$3,$4)",
            message.from_user.id, message.from_user.username, invite_code, datetime.now().date()
        )

@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    await init_user(message)
    await message.answer(
        "Привет! Я — бот для поиска облигаций.\n\nВыберите действие:",
        reply_markup=main_kb
    )

@dp.message_handler(lambda m: m.text == "👤 Профиль")
async def profile(message: types.Message):
    user = await get_user(message.from_user.id)
    status = "Премиум" if user['is_premium'] and user['premium_until'] and user['premium_until'] > datetime.now() else "Обычный"
    ref_link = f"https://t.me/{(await bot.get_me()).username}?start={user['invite_code']}"
    text = (
        f"Ваш статус: {status}\n"
        f"Запросов сегодня: {user['requests_left']}\n"
        f"Бонусы: {user['bonus_points']}\n"
        f"Реферальная ссылка: {ref_link}\n"
        f"Покупка запросов или премиума: /buy"
    )
    await message.answer(text)

@dp.message_handler(lambda m: m.text == "🔍 Поиск облигаций")
async def search(message: types.Message):
    user = await get_user(message.from_user.id)
    if user['last_request'] < datetime.now().date():
        limit = 5 if user['is_premium'] and user['premium_until'] and user['premium_until'] > datetime.now() else 3
        await db_pool.execute("UPDATE users SET requests_left=$1, last_request=$2 WHERE telegram_id=$3", limit, datetime.now().date(), message.from_user.id)
        user = await get_user(message.from_user.id)
    if user['requests_left'] <= 0:
        await message.answer("Лимит запросов исчерпан! /buy — купить ещё.")
        return
    await db_pool.execute("UPDATE users SET requests_left=requests_left-1 WHERE telegram_id=$1", message.from_user.id)
    # Для примера: топ-3 наиболее доходных облигации в рублях
    bonds = await db_pool.fetch("SELECT * FROM bonds WHERE currency='RUB' ORDER BY yield_to_maturity DESC LIMIT 3")
    reply = "\n\n".join(
        f"{b['name']} ({b['isin']})\nДоходность: {b['yield_to_maturity']}% до {b['maturity_date']}" for b in bonds
    )
    await message.answer(reply)

@dp.message_handler(commands=['buy'])
async def buy(message: types.Message):
    await message.answer("Пока что оплата реализована вручную.\nСвяжитесь с админом или ждите обновления 🚀")

# --- Подключение к базе ---
async def on_startup(dispatcher):
    global db_pool
    db_pool = await asyncpg.create_pool(dsn=DB_DSN)

if __name__ == "__main__":
    from aiogram import executor
    executor.start_polling(dp, on_startup=on_startup)
