from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler

from User.model import User


async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(f'Hello {update.effective_user.first_name}')
    return MESSAGE

WAITING_NAME, WAITING_AGE = range(1,3)
MESSAGE = 0

# Start the conversation
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE, user: User) -> int:
    await update.message.reply_text("Hello! What's your name?")
    return WAITING_NAME  # Move to the next state

# Handle name input
async def get_first_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['name'] = update.message.text
    await update.message.reply_text(f"Nice to meet you, {update.message.text}! How old are you?")
    return WAITING_AGE

# Handle age input
async def get_last_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['age'] = update.message.text
    name = context.user_data['name']
    await update.message.reply_text(f"Thank you, {name}. You are {update.message.text} years old.")
    return MESSAGE  # End conversation

# Handle cancellation
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Conversation cancelled.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("your message: " + update.message.text)