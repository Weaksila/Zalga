import asyncio
import os
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.fsm.storage.memory import MemoryStorage
from handlers import router as user_router
from database import init_db, add_user
from keyboards import main_menu_keyboard

# Load environment variables from .env file
load_dotenv()

# Bot tokenini .env faylidan oling
TOKEN = os.getenv("BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not TOKEN:
    raise ValueError("BOT_TOKEN environment variable not set. Please create a .env file with BOT_TOKEN.")

bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

@dp.message(CommandStart())
async def command_start_handler(message: types.Message) -> None:
    init_db()
    add_user(message.from_user.id)
    await message.answer(
        f"Salom, {message.from_user.full_name}! Zal botiga xush kelibsiz!\n\nMen sizga mashg\"ulotlaringizni rejalashtirish, natijalaringizni kuzatish va ovqatlanishingizni nazorat qilishda yordam beraman.",
        reply_markup=main_menu_keyboard()
    )

async def main() -> None:
    dp.include_router(user_router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
