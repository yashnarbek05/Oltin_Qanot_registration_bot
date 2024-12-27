from aiogram import types, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.state import states


async def start(message: types.Message, bot: Bot, state: FSMContext):
    button1 = InlineKeyboardButton(text="English🇺🇸", callback_data="en")
    button2 = InlineKeyboardButton(text="Uzbek🇺🇿", callback_data="uz")
    button3 = InlineKeyboardButton(text="Русский🇷🇺", callback_data="ru")
    keyboard_inline = InlineKeyboardMarkup().add(
        [button1],
        [button2],
        [button3]
    )

    await message.reply("Iltimos tilni tanlang!", reply_markup=keyboard_inline)
    await state.set_state(states.LANGUAGE)


async def check_button(call: types.CallbackQuery, state: FSMContext):
    lang_texts = {
        "en": "Hello! Enter your name: ",
        "uz": "Assalomu alaykum! Registratsiya uchun ismingizni kiriting:",
        "ru": "Привет! Введите свое имя для регистрации:"
    }

    await call.message.answer(lang_texts[call.data])
    await state.set_state(states.FIRSTNAME)
    await state.update_data(lang=call.data)

    await call.answer(text="Processing...")


async def enter_firstname(message: types.Message, bot: Bot, state: FSMContext):
    await message.copy_to(chat_id=message.chat.id)
    await state.set_state(states.LASTNAME)


async def echo(message: types.Message, bot: Bot):
    await message.copy_to(chat_id=message.chat.id)
