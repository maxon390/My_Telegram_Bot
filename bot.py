import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler


load_dotenv()  # Тягне ваш ключ із .env

TOKEN = os.getenv("BOT_TOKEN")

