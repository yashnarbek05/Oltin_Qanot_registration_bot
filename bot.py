from xml.sax import ContentHandler

from telegram.ext import ApplicationBuilder, CommandHandler, ConversationHandler, filters, MessageHandler

from bot.service import hello, start, get_name, get_age, cancel, WAITING_AGE, WAITING_NAME, handle_text, MESSAGE

TOKEN = "7610459957:AAG4Qfrtl6Vnag5wjlbf-3ACWSSHSX9elkc"


def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("hello", hello))

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            WAITING_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            WAITING_AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_age)],
            MESSAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text)]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)
    app.run_polling()


if __name__ == "__main__":
    main()