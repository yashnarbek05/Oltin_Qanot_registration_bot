import logging
import os

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ContextTypes,
    ConversationHandler, CallbackContext,
)

from bot.models.user import User
from config import GROUP_CHAT_ID, VOLUNTEER_ID_BEGINNING
from image.service import prepare_badge
from sheet.service import get_values_from_sheet, update_allowing, update_given

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

FULLNAME, PHOTO, LOCATION, BIO = range(1, 5)
LANGUAGE = 0
REGENERATE = 6
PHOTO_TO_REGENERATE = 7

volunteer_id = 5

users_apply_certificate = list()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the conversation and asks the user about their gender."""
    keyboard = [
        [InlineKeyboardButton("English🇺🇸", callback_data="en")],
        [InlineKeyboardButton("O'zbek🇺🇿", callback_data="uz")],
        [InlineKeyboardButton("Русский🇷🇺", callback_data="ru")]
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
            "You did not registrate from website yet!"
        )
        return ConversationHandler.END
    else:
        for i in range(1, len(excel_document)):
            if (user_fullname.lower() in excel_document[i][2].lower()
                    and excel_document[i][12] == 'FALSE'  # is_given
                    and excel_document[i][13] == 'FALSE'  # is_allowed
            ):
                await update.message.reply_text(
                    "Ok, you registreted from website, now send me photo:"
                )
                context.user_data['fullname'] = excel_document[i][2]
                context.user_data['time'] = excel_document[i][0]
                context.user_data['vol_id'] = i + VOLUNTEER_ID_BEGINNING
                return PHOTO

            elif (user_fullname.lower() in excel_document[i][2].lower()
                  and excel_document[i][12] == 'TRUE'  # is_given
            ):
                await update.message.reply_text(
                    "I generated your badge already, send \n/regenerate if you want regenerate..."
                )

                context.user_data['fullname'] = excel_document[i][2]
                context.user_data['time'] = excel_document[i][0]
                context.user_data['vol_id'] = i + VOLUNTEER_ID_BEGINNING

                logger.info(f"sending to regenerate {user_fullname}")

                return REGENERATE

    await update.message.reply_text(
        "We can't find your fullname from registreted people's list, first register from volunteers.uz, then send /start"
    )
    return ConversationHandler.END


async def photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the photo and asks for a location."""
    user = update.message.from_user
    photo_file = await update.message.photo[-1].get_file()
    await photo_file.download_to_drive(f"images/user_photo/{context.user_data.get("fullname")}.jpg")

    caption = (f"New volunteer🥳 \n\nuser-id: "
               + f"{update.effective_user.id}"
               + f"\nfull-name: {context.user_data.get("fullname")}"
                 f"\nJoined: {context.user_data.get('time')}")

    with open(f"images/user_photo/{context.user_data.get("fullname")}.jpg", "rb") as photo:
        await context.bot.send_photo(chat_id=GROUP_CHAT_ID, photo=photo, caption=caption)
        await context.bot.send_message(chat_id=GROUP_CHAT_ID,
                                       text="shu ko'rinishda javob bering:\n@register0815bot user_id: ✅/❌")

    logger.info("Photo of %s: %s sent to group", user.first_name,
                f"images/user_photo/{context.user_data.get("fullname")}.jpg")

    # todo should add multiple language
    await update.message.reply_text(
        "Gorgeous! Now, I sent your infos to admins, I will send your badge asap if they allow me. Wait me..."
    )

    users_apply_certificate.append(User(context.user_data.get("fullname"),
                                        context.user_data.get("time"),
                                        context.user_data.get("vol_id"),
                                        f"images/user_photo/{context.user_data.get("fullname")}.jpg",
                                        f"{update.effective_user.id}",
                                        context.user_data.get("language"),
                                        context.user_data.get("vol_id") - VOLUNTEER_ID_BEGINNING))

    return ConversationHandler.END


async def get_chat_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send the group chat ID."""
    chat_id = update.effective_chat.id
    await update.message.reply_text(f"This chat's ID is: {chat_id}")


async def error_handler(update: Update, context: CallbackContext):
    """Log the error and send a message to the user."""
    # Log the error
    logger.error(f"Exception occurred: {context.error}")

    # Optionally, send a message to the user (if the update is available)
    if update:
        await update.message.reply_text("Oops! Something went wrong. Please try again later.")


async def admin_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat.type == "group" or update.message.chat.type == "supergroup":
        # Get the message text
        received_message = update.message.text
        print(received_message)

        received_message_split = received_message.split(" ")

        if received_message_split[0] != "@" + context.bot.username:
            print(context.bot.username, " yoq ekan!!")
            return

        print(received_message_split[2].replace(":", ""))

        user = ""
        for i in range(len(users_apply_certificate)):

            user = users_apply_certificate[i]

            if received_message_split[1].replace(":", "") == user.get_chat_id():
                print("id topildi:", user.get_chat_id())

                if received_message_split[2] == "✅":
                    updated2, allowed = await update_allowing(user.get_sheet_id(), True)

                    logging.info(f"{updated2} rows updated to {allowed}!!! ")
                    logging.info(f"index = {user.get_sheet_id()} ")

                    await context.bot.send_message(chat_id=GROUP_CHAT_ID,
                                                   text=f"{user.get_fullname()} ga badge olishiga ruxsat berildi✅")

                    photo_name = await prepare_badge(user.get_fullname(), user.get_time(),
                                                     str(user.get_vol_id()),
                                                     user.get_user_photo())

                    with open(photo_name, "rb") as prepared_badge:
                        logging.info("Photo opened for sending to user!")

                        # todo should add multiple language
                        await context.bot.send_photo(chat_id=user.get_chat_id(),
                                                     photo=prepared_badge,
                                                     caption="Your badge is ready😇, please join our channel @volunteers_uz !!!")

                        updated1, given = await update_given(user.get_sheet_id(), True)
                        logging.info("Photo sent successfully to user <3 ")
                        logging.info(f"{updated1} rows updated to {given}!!! ")

                    users_apply_certificate.pop(i)

                    if os.path.exists(photo_name):
                        os.remove(photo_name)  # Delete the file
                        os.remove(user.get_user_photo())  # Delete the file
                        print(f"The file {photo_name} has been deleted successfully.")
                    else:
                        print(f"The file {photo_name} does not exist.")

                    return

                elif received_message_split[2] == "❌":
                    await context.bot.send_message(chat_id=GROUP_CHAT_ID,
                                                   text=f"{user.get_fullname()} ga badge olishiga ruxsat berilmadi❌")

                    # todo should add multiple language
                    await context.bot.send_message(chat_id=user.get_chat_id(),
                                                   text="Sorry😞, our admins don't allow to give you a badge😭")

                    updated2, allowed = await update_allowing(user.get_sheet_id(), False)

                    logging.info(f"{updated2} rows updated to {allowed}!!! ")

                    updated1, given = await update_given(user.get_sheet_id(), False)

                    logging.info(f"{updated1} rows updated to {given}!!! ")


                    return

                else:
                    await context.bot.send_message(chat_id=GROUP_CHAT_ID,
                                                   text=f"{received_message_split[2]} xato context kiritdingiz!")
                    return

        await context.bot.send_message(chat_id=GROUP_CHAT_ID,
                                       text=f"Bunday {received_message_split[1].replace(":", "")} idli odam topilmadi!")


async def regenerate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # todo should add multiple language
    await update.message.reply_text(
        "Now send me photo: "
    )
    return PHOTO_TO_REGENERATE


async def photo_regenerate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Please wait. I am preparing your badge...")

    photo_file = await update.message.photo[-1].get_file()
    await photo_file.download_to_drive(f"images/user_photo/{context.user_data.get("fullname")}.jpg")

    photo_name = await prepare_badge(context.user_data.get("fullname"), context.user_data.get("time"),
                                     str(context.user_data.get("vol_id")),
                                     f"images/user_photo/{context.user_data.get("fullname")}.jpg")
    # todo should add multiple language
    with open(photo_name, "rb") as prepared_badge:
        logging.info("Photo opened for sending to user!")
        await update.message.reply_photo(prepared_badge,
                                         caption="Your badge is ready😇, please join our channel @volunteers_uz !!!")
        logging.info("Photo sent successfully to user <3 ")

    if os.path.exists(photo_name):
        os.remove(photo_name)  # Delete the file
        os.remove(f"images/user_photo/{context.user_data.get("fullname")}.jpg")  # Delete the file
        print(f"The file {photo_name} has been deleted successfully.")
    else:
        print(f"The file {photo_name} does not exist.")

    return ConversationHandler.END
