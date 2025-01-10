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
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.ERROR
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.ERROR)

logger = logging.getLogger(__name__)

FULLNAME, PHOTO, LOCATION, BIO = range(1, 5)
LANGUAGE = 0
REGENERATE = 6
PHOTO_TO_REGENERATE = 7

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
        'en': f"Hello, {query.from_user.first_name}! Enter the full name you filled in the membership form:",
        'ru': f"Здравствуйте, {query.from_user.first_name}! Введите полное имя, которое вы указали в форме членства:",
        'uz': f"Assalomu alaykum, {query.from_user.first_name}! A'zolik anketasida toʻldirgan toʻliq ism va familiyangizni kiriting:"
    }

    await query.edit_message_text(text=messages.get(query.data))

    context.user_data['language'] = query.data

    return FULLNAME


async def fullname(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    user_fullname = update.message.text

    logger.info("name of %s: %s", user.first_name, user_fullname)

    messages = {
        'uz': "Iltimos, kuting, men sizning ismingizni ro'yxatdan o'tgan odamlar ro'yxatidan qidiryapman ...",
        'ru': 'Пожалуйста, подождите, я ищу ваше имя в списке зарегистрированных людей…',
        'en': "Please wait, I am searching your name from registreted people's list..."
    }

    await update.message.reply_text(
        messages.get(context.user_data.get('language'))
    )

    result = all(not char.isdigit() for char in user_fullname)
    messages = {
        'uz': f"Siz to'liq ismingizni noto'g'ri kiritdingiz, \"{user_fullname}\"😕, \nqayta yuboring...",
        'ru': f"Вы неправильно ввели свое полное имя: \"{user_fullname}\"😕, \nотправьте еще раз...",
        'en': f"You have entered your full name incorrectly: \"{user_fullname}\"😕, \nsend again..."
    }

    if not result:
        await update.message.reply_text(messages.get(context.user_data.get('language')))
        return FULLNAME

    requested = any(user_fullname == userr.get_fullname().strip() for userr in users_apply_certificate)

    messages = {
        'uz': "Sizning ma'lumotlaringiz allaqachon adminlarga yuborildi, iltimos ularning javobini kuting😐",
        'ru': "Ваша информация уже отправлена администраторам, дождитесь ответа😐",
        'en': "Your information has already been sent to the admins, please wait for their response😐"
    }

    if requested:
        await update.message.reply_text(messages.get(context.user_data.get('language')))
        return ConversationHandler.END

    excel_document = await get_values_from_sheet()

    if len(excel_document) <= 1:
        await update.message.reply_text(
            "You did not registrate from website yet!"
        )
        return ConversationHandler.END
    else:
        user_from_excel = ''
        for i in range(1, len(excel_document)):
            user_from_excel = excel_document[i]
            if (user_fullname.lower() == user_from_excel[2].lower().strip() and
                    (len(user_from_excel) != 13 or user_from_excel[12] == 'FALSE') and  # is_given
                    (len(user_from_excel) != 14 or user_from_excel[13] == 'FALSE')  # is_allowed
            ):

                messages = {
                    'uz': "Sizning roʻyxatdan oʻtganingiz tasdiqlandi. Bizga rasmiy rasmingizni yuboring.\nRasm talablari:\n1. Tiniq va yuz qism toʻliq tushsin.\n2. Rasm oʻlchamiga eʼtibor bering. \n3. Yoki namunaga qarang",
                    'ru': 'Ваша регистрация подтверждена. Пожалуйста, пришлите нам свою официальную фотографию.\nТребования к фотографии:\n1. Четкое и анфас.\n2. Обратите внимание на размер фотографии. \n3. Или посмотрите образец',
                    'en': "Your registration has been confirmed. Please send us your official photo.\nPhoto requirements:\n1. Clear and full face.\n2. Pay attention to the size of the photo. \n3. Or see a sample"
                }

                await update.message.reply_photo("images/example_avatar_photo.png",
                                                 caption=messages.get(context.user_data.get('language'))
                                                 )

                context.user_data['fullname'] = user_from_excel[2]
                context.user_data['time'] = user_from_excel[0]
                context.user_data['vol_id'] = i + VOLUNTEER_ID_BEGINNING
                return PHOTO

            elif (user_fullname.lower() == user_from_excel[2].lower()
                  and len(user_from_excel) > 13 and user_from_excel[12] == 'TRUE'  # is_given
            ):
                messages = {
                    'uz': "Men sizning guvohnomangizni allaqachon yaratdim, agar qayta tiklamoqchi bo'lsangiz, \n/regenerate yuboring...",
                    'ru': 'Я уже создал ваш бежик, отправьте \n/regenerate, если хотите восстановить…',
                    'en': "I generated your badge already, send \n/regenerate if you want regenerate..."
                }

                await update.message.reply_text(
                    messages.get(context.user_data.get('language'))
                )

                context.user_data['fullname'] = user_from_excel[2]
                context.user_data['time'] = user_from_excel[0]
                context.user_data['vol_id'] = i + VOLUNTEER_ID_BEGINNING

                logger.info(f"sending to regenerate {user_fullname}")

                return REGENERATE

    messages = {
        'uz': 'Roʻyxatdan oʻtganlar roʻyxatidan toʻliq ismingizni topa olmadik, avval volunteers.uz dan roʻyxatdan oʻting, keyin /start yuboring',
        'ru': "Мы не можем найти ваше полное имя в списке зарегистрированных людей, сначала зарегистрируйтесь на сайте Volunteers.uz, затем отправьте /start",
        'en': "We can't find your fullname from registreted people's list, first register from volunteers.uz, then send /start"
    }

    await update.message.reply_text(
        messages.get(context.user_data.get('language'))
    )
    return ConversationHandler.END


async def photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the photo and asks for a location."""
    user = update.message.from_user
    photo_file = await update.message.photo[-1].get_file()
    await photo_file.download_to_drive(f"images/user_photo/{context.user_data.get('fullname')}.jpg")

    caption = (f"New volunteer🥳 \n\nuser-id: "
               + f"`{update.effective_user.id}`"
               + f"\nfull-name: {context.user_data.get('fullname')}"
                 f"\nJoined: {context.user_data.get('time')}")

    with open(f"images/user_photo/{context.user_data.get('fullname')}.jpg", "rb") as photo:
        await context.bot.send_photo(chat_id=GROUP_CHAT_ID, photo=photo, caption=caption, parse_mode="Markdown")
        await context.bot.send_message(chat_id=GROUP_CHAT_ID,
                                       text=f"shu ko'rinishda javob bering:\n@{context.bot.username} user_id: ✅/❌ [cause]")

    logger.info("Photo of %s: %s sent to group", user.first_name,
                f"images/user_photo/{context.user_data.get('fullname')}.jpg")

    messages = {
        'uz': "Ajoyib! Endi maʼlumotlaringizni adminlarga joʻnatdim, ruxsat berishsa tez orada guvohnomangizni yuboraman. Meni kuting...",
        'ru': "Отлично! Теперь я отправил ваши данные администраторам, если они мне позволят, то пришлю ваши бежик в ближайшее время. Подождите меня...",
        'en': "Great! Now I've sent your details to the admins, I'll send your credentials soon if they'll let me. Wait for me..."
    }

    await update.message.reply_text(
        messages.get(context.user_data.get('language'))
    )

    users_apply_certificate.append(User(context.user_data.get('fullname'),
                                        context.user_data.get("time"),
                                        context.user_data.get("vol_id"),
                                        f"images/user_photo/{context.user_data.get('fullname')}.jpg",
                                        f"{update.effective_user.id}",
                                        context.user_data.get('language'),
                                        context.user_data.get("vol_id") - VOLUNTEER_ID_BEGINNING))

    return ConversationHandler.END


async def get_chat_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send the group chat ID."""
    chat_id = update.effective_chat.id
    logger.info(f"This chat's ID is: {chat_id}")
    await update.message.reply_text(f"This chat's ID is: {chat_id}")


async def error_handler(update: Update, context: CallbackContext):
    """Log the error and send a message to the user."""
    # Log the error
    logger.error(f"Exception occurred: {context.error}")
    await context.bot.send_message(chat_id=GROUP_CHAT_ID,
                                   text=f"Xatolik yuz berdi😢: \n\n{context.error}")


async def cancel(update: Update, context: CallbackContext):
    messages = {
        'uz': 'Bekor qilindi!',
        'ru': 'Отменено!',
        'en': 'Cancelled!'
    }
    await update.message.reply_text(messages.get(context.user_data.get('language')))
    return ConversationHandler.END


async def admin_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if (
            update.message.chat.type == "group" or update.message.chat.type == "supergroup") and update.message.chat_id == GROUP_CHAT_ID:
        # Get the message text
        received_message = update.message.text

        received_message_split = received_message.split(" ", 3)

        if received_message_split[0] != "@" + context.bot.username:
            return

        user = ""
        for i in range(len(users_apply_certificate)):

            user = users_apply_certificate[i]

            if received_message_split[1].replace(":", "") == user.get_chat_id():

                if received_message_split[2] == "✅":
                    updated2, allowed = await update_allowing(user.get_sheet_id(), True)

                    logging.info(f"{updated2} rows updated to {allowed}!!! ")
                    logging.info(f"index = {user.get_sheet_id()} ")

                    await context.bot.send_message(chat_id=GROUP_CHAT_ID,
                                                   text=f"{user.get_fullname()} ga guvohnoma olishiga ruxsat berildi✅")

                    photo_name = await prepare_badge(user.get_fullname(),
                                                     str(user.get_vol_id()),
                                                     user.get_user_photo())

                    with open(photo_name, "rb") as prepared_badge:
                        logging.info("Photo opened for sending to user!")

                        messages = {
                            'uz': "Tabriklaymiz🎉, sizning  guvohnomangiz tayyor bo'ldi. Volontyorlik faoliyatingizga omad tilaymiz. Volontyorlik oilamizga xush kelibsiz🤗\nKanalimizga obuna bo'ling: @Volunteers_uz",
                            'ru': 'Поздравляем🎉, ваш сертификат готов. Удачи в вашем волонтерстве. Добро пожаловать в нашу волонтерскую семью🤗\nПодпишитесь на наш канал: @Volunteers_uz',
                            'en': "Congratulations🎉, your certificate is ready. Good luck with your volunteering. Welcome to our volunteer family🤗\nSubscribe to our channel: @Volunteers_uz"
                        }

                        await context.bot.send_photo(chat_id=user.get_chat_id(),
                                                     photo=prepared_badge,
                                                     caption=messages.get(context.user_data.get('language')))

                        updated1, given = await update_given(user.get_sheet_id(), True)
                        logging.info("Photo sent successfully to user <3 ")
                        logging.info(f"{updated1} rows updated to {given}!!! ")

                    users_apply_certificate.pop(i)

                    if os.path.exists(photo_name):
                        os.remove(photo_name)  # Delete the file
                        os.remove(user.get_user_photo())  # Delete the file
                    else:
                        print(f"The file {photo_name} does not exist.")

                    return

                elif received_message_split[2] == "❌":
                    await context.bot.send_message(chat_id=GROUP_CHAT_ID,
                                                   text=f"{user.get_fullname()} ga guvohnoma olishiga ruxsat berilmadi❌")

                    messages = {
                        'uz': f"Uzur, sizing yuborgan ma'lumotlaringiz adminlar tomonidan rad etildi.\n{'' if len(received_message_split) < 4 else 'sabab: ' + received_message_split[3]}",
                        'ru': f"К сожалению, предоставленная вами информация была отклонена администраторами.\n{'' if len(received_message_split) < 4 else 'причина: ' + received_message_split[3]}",
                        'en': f"Sorry, your submitted information has been rejected by admins.\n{'' if len(received_message_split) < 4 else 'cause: ' + received_message_split[3]}"
                    }

                    await context.bot.send_message(chat_id=user.get_chat_id(),
                                                   text=messages.get(context.user_data.get('language')))

                    updated2, allowed = await update_allowing(user.get_sheet_id(), False)

                    logging.info(f"{updated2} rows updated to {allowed}!!! ")

                    updated1, given = await update_given(user.get_sheet_id(), False)

                    logging.info(f"{updated1} rows updated to {given}!!! ")
                    users_apply_certificate.pop(i)

                    if os.path.exists(user.get_user_photo()):
                        os.remove(user.get_user_photo())  # Delete the file
                        print(f"The file {user.get_user_photo()} has been deleted successfully.")
                    else:
                        print(f"The file {user.get_user_photo()} does not exist.")

                    return

                else:
                    await context.bot.send_message(chat_id=GROUP_CHAT_ID,
                                                   text=f"{received_message_split[2]} xato context kiritdingiz!")
                    return

        await context.bot.send_message(chat_id=GROUP_CHAT_ID,
                                       text=f"Bunday {received_message_split[1].replace(':', '')} idli odam topilmadi!")


async def regenerate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    messages = {
        'uz': "Bizga rasmiy rasmingizni yuboring.\nRasm talablari:\n1. Tiniq va yuz qism toʻliq tushsin.\n2. Rasm oʻlchamiga eʼtibor bering. \n3. Yoki namunaga qarang",
        'ru': 'Пожалуйста, пришлите нам свою официальную фотографию.\nТребования к фотографии:\n1. Четкое и анфас.\n2. Обратите внимание на размер фотографии. \n3. Или посмотрите образец',
        'en': "Please send us your official photo.\nPhoto requirements:\n1. Clear and full face.\n2. Pay attention to the size of the photo. \n3. Or see a sample"
    }

    await update.message.reply_photo("images/example_avatar_photo.png",
                                     caption=messages.get(context.user_data.get('language'))
                                     )
    return PHOTO_TO_REGENERATE


async def photo_regenerate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    messages = {
        'uz': "Iltimos kuting. Men sizning guvohnomangizni tayyorlayapman ...",
        'ru': "Пожалуйста, подождите. Я готовлю твой бежик...",
        'en': "Please wait. I am preparing your badge..."
    }
    await update.message.reply_text(
        messages.get(context.user_data.get('language'))
    )

    photo_file = await update.message.photo[-1].get_file()
    await photo_file.download_to_drive(f"images/user_photo/{context.user_data.get('fullname')}.jpg")

    photo_name = await prepare_badge(context.user_data.get('fullname'),
                                     str(context.user_data.get("vol_id")),
                                     f"images/user_photo/{context.user_data.get('fullname')}.jpg")
    messages = {
        'uz': "Tabriklaymiz🎉, sizning  guvohnomangiz tayyor bo'ldi. Volontyorlik faoliyatingizga omad tilaymiz. Volontyorlik oilamizga xush kelibsiz🤗\nKanalimizga obuna bo'ling: @Volunteers_uz",
        'ru': 'Поздравляем🎉, ваш сертификат готов. Удачи в вашем волонтерстве. Добро пожаловать в нашу волонтерскую семью🤗\nПодпишитесь на наш канал: @Volunteers_uz',
        'en': "Congratulations🎉, your certificate is ready. Good luck with your volunteering. Welcome to our volunteer family🤗\nSubscribe to our channel: @Volunteers_uz"
    }

    with open(photo_name, "rb") as prepared_badge:
        logging.info("Photo opened for sending to user!")
        await update.message.reply_photo(prepared_badge,
                                         caption=messages.get(context.user_data.get('language')))
        logging.info("Photo sent successfully to user <3 ")

    if os.path.exists(photo_name):
        os.remove(photo_name)  # Delete the file
        os.remove(f"images/user_photo/{context.user_data.get('fullname')}.jpg")  # Delete the file
        print(f"The file {photo_name} has been deleted successfully.")
    else:
        print(f"The file {photo_name} does not exist.")

    return ConversationHandler.END


async def leave_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.message.chat_id,
                                   text="Uzur, bu bot sizning guruhingiz uchun emas!\nThis bot is not working in your group😣")
    await context.bot.leave_chat(update.message.chat_id)


async def alll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat_id != GROUP_CHAT_ID:
        return

    text = "Guvohnoma olmoqchi bo'lgan volontiyorlar yoq!"

    if not users_apply_certificate:
        await context.bot.send_message(GROUP_CHAT_ID, text=text, parse_mode="Markdown")

    for volunteer in users_apply_certificate:
        text = (
            f"New volunteer🥳 \n\n"
            f"user-id: `{volunteer.get_chat_id()}`\n"
            f"full-name: {volunteer.get_fullname()}\n"
            f"Joined: {volunteer.get_time()}"
        )
        await context.bot.send_message(chat_id=GROUP_CHAT_ID, text=text, parse_mode="Markdown")

    await context.bot.send_message(chat_id=GROUP_CHAT_ID, text=f"{len(users_apply_certificate)} nafar volontiyorga javob berilmadi⁉️")