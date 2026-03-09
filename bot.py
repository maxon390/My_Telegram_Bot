import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters, \
    CallbackQueryHandler, ConversationHandler
from gpt import ChatGptService
from util import show_main_menu,send_text, send_image, load_message, send_text_buttons, load_prompt

load_dotenv()  # Тягне ваш ключ із .env

TOKEN = os.getenv("BOT_TOKEN")

OPENAI_TOKEN = os.getenv("OPENAI_API_KEY") #завантажуємо токен chat GPT
gpt_service = ChatGptService(OPENAI_TOKEN) #створюємо обєкт chat GPT

#Стартове меню при запуску бота або при команді /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_image(update, context, 'main')
    await send_text(update, context, load_message('main'))
    #Додавання випадючого меню зліва
    await show_main_menu(update, context,{
        "/start": "Головне меню",
        "/random": "Цікавий рандомний факт"
    })


async def handle_message(update:Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text #отримуємо текст повідомлення
    message = await update.message.reply_text("Бот думає..")
    #await gpt_service.clear()
    gpt_answer = await gpt_service.add_message(user_message)
    await message.edit_text(gpt_answer)


async def random(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_image(update, context, 'random')
    prompt = load_prompt('random')
    gpt_answer = await gpt_service.send_question(prompt, "Напиши цікавий, рандомний факт. Українською")
    await send_text_buttons(update, context, gpt_answer, {
        'random' : "Ще цікавий факт",
        'start' : 'Завершити'})


# Функція обробки кнопок під повідомленням з рандомним фактом
async  def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == 'random':
        await random(update, context)
    elif query.data == 'start':
        await start(update, context)

"""conteiner = ConversationHandler(
    entry_points=[CommandHandler("mode", mode_start)], # Початок
    states={
        MODE_CHOOSE: [MessageHandler(filters.TEXT, mode_set)] # Що робити в стані очікування
    },
    fallbacks=[CommandHandler("cancel", start)] # Як вийти, якщо передумав
)"""



if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    # Обробник запуска бота або команди /start
    app.add_handler(CommandHandler("start", start))
    # Обробник запуска бота або команди /random
    app.add_handler(CommandHandler("random", random))
    # Обробник будь-яких текстових повідомлень
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    # Обробник кнопок під повідомленням рандомного факту
    app.add_handler(CallbackQueryHandler(callback_handler))
    print("Бот запущений...")
    app.run_polling()
