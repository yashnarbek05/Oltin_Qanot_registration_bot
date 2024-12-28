import logging

from telegram import ReplyKeyboardRemove, Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
)

from sheet.service import get_values_from_sheet

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

FULLNAME, PHOTO, LOCATION, BIO = range(1, 5)
LANGUAGE = 0


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the conversation and asks the user about their gender."""
    keyboard = [
        [
            InlineKeyboardButton("English🇺🇸", callback_data="en"),
            InlineKeyboardButton("O'zbek🇺🇿", callback_data="uz"),
            InlineKeyboardButton("Русский🇷🇺", callback_data="ru"),
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Tilni tanlang:", reply_markup=reply_markup)

    return LANGUAGE


async def language(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query

    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    await query.answer("Progress...")

    messages = {
        'en': f"Hello {query.from_user.first_name}! Enter your fullname which you entered to registeration website:",
        'ru': f"Здравствуйте, {query.from_user.first_name}! Введите свое полное имя, которое вы указали на сайте регистрации:",
        'uz': f"Assalomu alaykum {query.from_user.first_name}! Ro'yxatdan o'tish veb-saytiga kiritgan to'liq ismingizni kiriting:"
    }

    await query.edit_message_text(text=messages.get(query.data))

    context.user_data['language'] = query.data

    return FULLNAME


async def fullname(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    user_fullname = update.message.text

    logger.info("name of %s: %s", user.first_name, user_fullname)

    await update.message.reply_text(
        "Please wait, I am searching your name from registreted people's list..."
    )
    excel_document = await get_values_from_sheet()

    if len(excel_document) <= 1:
        await update.message.reply_text(
            "You did not registrate from website"
        )
    else:
        for i in range(1, len(excel_document)):
            if user_fullname.lower() in excel_document[i][2].lower():
                await update.message.reply_text(
                    "Ok, you registreted from website, now send me photo:"
                )
                context.user_data['firstname'] = update.message.text
                return PHOTO

    await update.message.reply_text(
        "We cant find your user_fullname from registreted people's list, first register from volunteers.uz, then send /start"
    )
    return ConversationHandler.END


async def photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the photo and asks for a location."""
    user = update.message.from_user
    photo_file = await update.message.photo[-1].get_file()
    await photo_file.download_to_drive("user_photo.jpg")
    logger.info("Photo of %s: %s", user.first_name, "user_photo.jpg")
    await update.message.reply_text(
        "Gorgeous! Now, send me your location please, or send /skip if you don't want to."
    )

    return ConversationHandler.END


async def bio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the info about the user and ends the conversation."""
    user = update.message.from_user
    logger.info("Bio of %s: %s", user.first_name, update.message.text)
    await update.message.reply_text("Thank you! I hope we can talk again some day.")

    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    await update.message.reply_text(
        "Bye! I hope we can talk again some day.", reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END
