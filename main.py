from telegram import Update
from telegram.ext import ConversationHandler, CommandHandler, MessageHandler, filters, \
    CallbackQueryHandler, ApplicationBuilder

from bot.service import PHOTO, photo, start, language, LANGUAGE, fullname, FULLNAME, get_chat_id, REGENERATE, \
    regenerate, PHOTO_TO_REGENERATE, photo_regenerate, error_handler, admin_response
from config import BOT_TOKEN


def main() -> None:
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    application = ApplicationBuilder().token(BOT_TOKEN).read_timeout(300).write_timeout(300).build()

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    application.add_handler(CommandHandler("get_chat_id", get_chat_id))

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            LANGUAGE: [CallbackQueryHandler(language)],
            FULLNAME: [MessageHandler(filters.TEXT, fullname)],
            REGENERATE: [CommandHandler("regenerate", regenerate)],
            PHOTO_TO_REGENERATE: [MessageHandler(filters.PHOTO, photo_regenerate)],
            PHOTO: [MessageHandler(filters.PHOTO, photo)],
        },
        fallbacks=[]
    )

    application.add_handler(conv_handler)
    application.add_handler(MessageHandler(filters.TEXT, admin_response))
    application.add_error_handler(error_handler)

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()

    # excel_document = get_values_from_sheet()
    # print(excel_document)
    # fullname = excel_document[1][2].split(" ")
    # print(fullname)
    # firstname, lastname = fullname[0], fullname[1]
    # print(firstname + " and " + lastname)
    # prepare_badge(firstname, lastname, excel_document[1][0], 10, "images/я мечтала об этом котике.jpg")
