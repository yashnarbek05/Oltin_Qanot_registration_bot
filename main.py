from telegram import Update
from telegram.ext import Application, ConversationHandler, CommandHandler, MessageHandler, filters, CallbackQueryHandler

from bot.service import PHOTO, photo, bio, cancel, start, \
    language, BIO, LANGUAGE, FULLNAME, fullname, FULLNAME
from config import BOT_TOKEN


def main() -> None:
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(BOT_TOKEN).build()

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            LANGUAGE: [CallbackQueryHandler(language)],
            FULLNAME: [MessageHandler(filters.TEXT, fullname)],
            PHOTO: [MessageHandler(filters.PHOTO, photo)],
            BIO: [MessageHandler(filters.TEXT & ~filters.COMMAND, bio)],
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )

    application.add_handler(conv_handler)

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
