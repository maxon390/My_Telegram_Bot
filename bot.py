import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from gpt import ChatGptService

load_dotenv()  # Тягне ваш ключ із .env

TOKEN = os.getenv("BOT_TOKEN")

OPENAI_TOKEN = os.getenv("OPENAI_API_KEY") #завантажуємо токен chat GPT
gpt_service = ChatGptService(OPENAI_TOKEN) #створюємо обєкт chat GPT

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привіт")

async def handle_message(update:Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text #отримуємо текст повідомлення
    message = await update.message.reply_text("Бот думає..")
    gpt_answer = await gpt_service.add_message(user_message)
    await message.edit_text(gpt_answer)

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Бот запущен...")
    app.run_polling()
