from aiogram import types
from aiogram.utils.keyboard import ReplyKeyboardBuilder

def main_menu_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.row(
        types.KeyboardButton(text="Mashqlar Rejasi"),
        types.KeyboardButton(text="Natijalarim")
    )
    builder.row(
        types.KeyboardButton(text="Kkal Hisoblagich")
    )
    return builder.as_markup(resize_keyboard=True)
