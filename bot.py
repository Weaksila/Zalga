import asyncio
import os
from aiohttp import web
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.fsm.storage.memory import MemoryStorage

# O'zingizning fayllaringizdan importlar
from handlers import router as user_router
from database import init_db, add_user
from keyboards import main_menu_keyboard

# Muhit o'zgaruvchilarini yuklash
load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise ValueError("BOT_TOKEN environment variable not set.")

bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# --- RENDER UCHUN PORTNI ALDASH (MUHIM) ---
async def handle(request):
    return web.Response(text="Bot is running!")

async def start_web_server():
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    # Render bergan PORTni ishlatamiz yoki 8080 ni tanlaymiz
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    print(f"Web server {port}-portda ishga tushdi.")

# --- HANDLERLAR ---
@dp.message(CommandStart())
async def command_start_handler(message: types.Message) -> None:
    await init_db() # Ma'lumotlar bazasini tekshirish
    add_user(message.from_user.id)
    await message.answer(
        f"Salom, {message.from_user.full_name}! Zal botiga xush kelibsiz!\n\nMen sizga mashg'ulotlaringizni rejalashtirish, natijalaringizni kuzatish va ovqatlanishingizni nazorat qilishda yordam beraman.",
        reply_markup=main_menu_keyboard()
    )

async def main() -> None:
    # Ma'lumotlar bazasini ishga tushirish
    await init_db()
    
    # Web serverni ishga tushirish (Render xato bermasligi uchun)
    await start_web_server()
    
    # Routerni qo'shish
    dp.include_router(user_router)
    
    # Botni ishga tushirish
    print("Bot pollingni boshladi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Bot to'xtatildi.")
