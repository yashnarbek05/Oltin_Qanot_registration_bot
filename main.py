from telegram import Update
from telegram.ext import ConversationHandler, CommandHandler, MessageHandler, filters, \
    CallbackQueryHandler, ApplicationBuilder

from bot.service import PHOTO, photo, start, language, LANGUAGE, fullname, FULLNAME, get_chat_id, REGENERATE, \
    regenerate, PHOTO_TO_REGENERATE, photo_regenerate, error_handler, admin_response, cancel, leave_group, alll, ADMIN, \
    capture_rejection_reason
from config import BOT_TOKEN, GROUP_CHAT_ID


def main() -> None:
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    application = ApplicationBuilder().token(BOT_TOKEN).read_timeout(300).write_timeout(300).build()


    application.add_handler(MessageHandler(~filters.ChatType.PRIVATE & ~filters.Chat(GROUP_CHAT_ID), leave_group))


    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            LANGUAGE: [CallbackQueryHandler(language)],
            FULLNAME: [CommandHandler('cancel', cancel), MessageHandler(filters.TEXT, fullname)],
            REGENERATE: [CommandHandler("regenerate", regenerate)],
            PHOTO_TO_REGENERATE: [CommandHandler('cancel', cancel), MessageHandler(filters.PHOTO, photo_regenerate)],
            PHOTO: [MessageHandler(filters.PHOTO, photo)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
        per_message=False
    )

    application.add_handler(CallbackQueryHandler(admin_response, pattern="\d"))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & filters.Chat(GROUP_CHAT_ID), capture_rejection_reason))

    application.add_handler(CommandHandler("all", alll))

    application.add_handler(conv_handler)
    application.add_error_handler(error_handler)

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
