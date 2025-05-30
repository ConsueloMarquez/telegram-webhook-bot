import asyncio
import logging
import os

from aiohttp import web
from aiogram import Bot, Dispatcher, F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.filters import CommandStart

# ✅ Получаем токен и URL из переменных окружения
API_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

if not API_TOKEN:
    raise ValueError("❌ Переменная окружения BOT_TOKEN не установлена.")
if not WEBHOOK_URL:
    raise ValueError("❌ Переменная окружения WEBHOOK_URL не установлена.")

# Инициализация
bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Клавиатура
yes_no_keyboard = ReplyKeyboardMarkup(
    resize_keyboard=True,
    keyboard=[[KeyboardButton(text="Si"), KeyboardButton(text="No")]]
)

# Состояния
class Form(StatesGroup):
    tree = State()
    bush = State()
    apple = State()
    road = State()

@dp.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    await state.set_state(Form.tree)
    await message.answer("Avete mai registrato un ZEN?", reply_markup=yes_no_keyboard)

@dp.message(Form.tree)
async def answer_tree(message: types.Message, state: FSMContext):
    await state.update_data(tree=message.text)
    await state.set_state(Form.bush)
    await message.answer("Avete mai registrato un Trade Republic?", reply_markup=yes_no_keyboard)

@dp.message(Form.bush)
async def answer_bush(message: types.Message, state: FSMContext):
    await state.update_data(bush=message.text)
    await state.set_state(Form.apple)
    await message.answer("Avete mai registrato un Bitsa?", reply_markup=yes_no_keyboard)

@dp.message(Form.apple)
async def answer_apple(message: types.Message, state: FSMContext):
    await state.update_data(apple=message.text)
    await state.set_state(Form.road)
    await message.answer("Avete mai registrato un BBVA?", reply_markup=yes_no_keyboard)

@dp.message(Form.road)
async def answer_road(message: types.Message, state: FSMContext):
    await state.update_data(road=message.text)
    data = await state.get_data()
    summary = (
        f"📋 Elenco delle registrazioni da {message.from_user.full_name}:\n"
        f" ZEN: {data['tree']}\n"
        f" Trade Republic: {data['bush']}\n"
        f" Bitsa: {data['apple']}\n"
        f" BBVA: {data['road']}"
    )
    await message.answer("Grazie! La domanda è stata elaborata. Il nostro responsabile vi contatterà al più presto 👌", reply_markup=ReplyKeyboardRemove())
    await message.answer(summary)
    await state.clear()

# Обработчик webhook'а
async def handle_webhook(request):
    body = await request.json()
    update = types.Update(**body)
    await dp.feed_update(bot, update)
    return web.Response(text="ok")

async def on_startup(app):
    await bot.set_webhook(f"{WEBHOOK_URL}/webhook")

async def on_shutdown(app):
    await bot.delete_webhook()

async def main():
    app = web.Application()
    app.router.add_post("/webhook", handle_webhook)
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host="0.0.0.0", port=int(os.getenv("PORT", "8080")))
    await site.start()

    print("Bot is running...")
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
