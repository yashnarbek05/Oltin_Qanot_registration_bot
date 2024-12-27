from asyncio import run

from aiogram import Bot, Dispatcher, F

from bot.service import start, check_button
from config import BOT_TOKEN

dp = Dispatcher()
bot = Bot(BOT_TOKEN)

excel_document = None


async def main():
    dp.message.register(start)
    dp.callback_query.register(check_button, F.in_(('en','ru','uz')))

    await dp.start_polling(bot, polling_timeout=1)


if __name__ == "__main__":
    run(main())

    # excel_document = get_values_from_sheet()
    # print(excel_document)
    # fullname = excel_document[1][2].split(" ")
    # print(fullname)
    # firstname, lastname = fullname[0], fullname[1]
    # print(firstname + " and " + lastname)
    # prepare_badge(firstname, lastname, excel_document[1][0], 10, "images/я мечтала об этом котике.jpg")
