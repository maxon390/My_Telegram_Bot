import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters, \
    CallbackQueryHandler, ConversationHandler
from gpt import ChatGptService
from util import show_main_menu,send_text, send_image, load_message, send_text_buttons, load_prompt

TALK = 1
QUIZ = 2

load_dotenv()  # Тягне ваш ключ із .env

TOKEN = os.getenv("BOT_TOKEN")

OPENAI_TOKEN = os.getenv("OPENAI_API_KEY") #завантажуємо токен chat GPT
gpt_service = ChatGptService(OPENAI_TOKEN) #створюємо обєкт chat GPT

#Стартове меню при запуску бота або при команді /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_text(update, context, load_message('main'))
    #Додавання випадючого меню зліва
    await show_main_menu(update, context,{
        "/start": "Головне меню",
        "/random": "Цікавий рандомний факт",
        "/gpt" : "Запитання чату GPT"
    })


async def gpt(update:Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['mode'] = 'gpt' #Перехід моду в режим gpt
    gpt_service.set_prompt(load_prompt('gpt')) #Завантаження промту з файлу
    await send_image(update,context, 'gpt') #Відправка в чат картинки режиму gpt
    await send_text(update,context, load_message('gpt')) #Відправка тексту режиму, завантаженого з файлу

#Функція обробки будь яких повідомлень від користувача з усіх режимів
async def handle_message(update:Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data['mode'] == 'talk': # цей блок виконується якщо режим talk
        user_message = update.message.text #отримуємо текст повідомлення від користувача
        message = await update.message.reply_text("Набирає повідомлення...")  #відправляємо користувачу повідомлення за записуємо його адресу
        gpt_answer = await gpt_service.add_message(user_message)  #відправляємо чату повідомлення користувача та записуємо відповідь
        await message.edit_text(gpt_answer)  #змінюємо попередне повідомлення користувачу на відповідь від чату
        await send_text_buttons(update,context, '__________', {'start' : 'Завершити діалог'})#Додає кнопку завершити діалог
    elif context.user_data.get('mode') == 'gpt': # цей блок виконується якщо режим gpt
        user_message = update.message.text  #отримуємо текст повідомлення від користувача
        message = await update.message.reply_text("Бот думає..") #відправляємо користувачу повідомлення за записуємо його адресу
        gpt_answer = await gpt_service.add_message(user_message) #відправляємо чату повідомлення користувача та записуємо відповідь
        await message.edit_text(gpt_answer)  #змінюємо попередне повідомлення користувачу на відповідь від чату
    elif context.user_data.get('mode') == 'quiz': # цей блок виконується якщо режим quiz
        user_answer = update.message.text
        message = await update.message.reply_text("Перевіряю...")

        check_query = f"Користувач відповів: '{user_answer}'. Якщо правильно - почни з 'Правильно!', якщо ні - 'Неправильно'. Додай пояснення."
        gpt_answer = await gpt_service.add_message(check_query)

        if "Правильно" in gpt_answer:
            context.user_data['score'] = context.user_data.get('score', 0) + 1

        current_score = context.user_data.get('score', 0)
        final_text = f"{gpt_answer}\n\n🏆 Ваш рахунок: {current_score}"

        await message.edit_text(final_text)

        await send_text_buttons(update, context, "Граємо далі?", {
            'more_quiz': "Ще питання",
            'quiz': "Змінити тему",
            'start': "Завершити квіз"
        })

# Функція виводу рандом факту який генерує чат ГПТ
async def random(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('mode') != 'random': #Якщо режим  не рандом
        context.user_data['mode'] = 'random' # тоді перевести в режим рандом
        await send_image(update, context, 'random') #також завантажити картинку розділу якщо до цього був інший режим
    prompt = load_prompt('random')
    gpt_answer = await gpt_service.send_question(prompt, "Напиши цікавий, рандомний факт. Українською")
    #Виводить текст факту та додає кнопки Ще цікавий факт та Завершити
    await send_text_buttons(update, context, gpt_answer, {
        'random' : "Ще цікавий факт", #При натисканні спрацьовує обробник app.add_handler(CallbackQueryHandler(callback_handler))
        'start' : 'Завершити'}) #При натисканні спрацьовує обробник app.add_handler(CallbackQueryHandler(callback_handler))


# Функція обробки кнопок під повідомленням з random фактом та квізом
async  def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query #отримуємо назву кнопки яка була натиснута
    await query.answer() #даємо відповідь що обробили натискання кнопки
    if query.data == 'random': #якщо прийшло random то запускаємо функцію random
        await random(update, context)
    elif query.data == 'start': #якщо прийшло start то запускаємо функцію start
        await start(update, context)
    elif query.data == 'more_quiz': #якщо прийшло more_quiz то запускаємо функцію quiz_button_handler
        await quiz_button_handler(update, context)


async def talk(update:Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['mode'] = 'talk' #переводимо mode в talk
    await send_image(update, context, 'date') #надсилає зображення режиму в чат
    buttons = {
        'date_grande': "Аріана Гранде",
        'date_robbie': "Марго Роббі",
        'date_zendaya': "Зендея",
        'date_gosling': "Райан Гослінг",
        'date_hardy': "Том Харді",
    }
    await send_text_buttons(update, context, load_message('date'), buttons) # надсилає в чат опис режиму та кнопки
    return TALK #Повертаємо state в talk_handler = ConversationHandler

#  Функція обробки кнопок вибору знаменитості
async def talk_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query #Отримуємо яка кнопка була натиснута
    #print( query)
    await query.answer() #даємо відповідь що обробили натискання кнопки
    gpt_service.set_prompt(load_prompt(query.data)) #Завантажуємо промт знаметиності в чатГПТ
    #await query.edit_message_text(f"Ви обрали особистість. Тепер я спілкуюся як {query.data[5:].capitalize()}!")
    #Надсилаємо повідомлення в чат та кнопку завершити діалог
    await send_text_buttons(update, context, f"Ви обрали особистість. Тепер я спілкуюся як {query.data[5:].capitalize()}!", {'start': 'Завершити'})
    # виходимо з talk_handler = ConversationHandler, подальшою обробкою повідомлень займеться функція handle_message
    return ConversationHandler.END

async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['mode'] = 'quiz' # переводимо мод в режим quiz
    context.user_data['score'] = 0  # Початковий рахунок
    await send_image(update, context, 'quiz') #надсилаємо картинку розділу в чат
    buttons = {
        'quiz_prog': "Програмування",
        'quiz_math': "Математика",
        'quiz_biology': "Біологія"
    }
    await send_text_buttons(update, context, load_message('quiz'), buttons) #надсилаємо в чат текст розділу та кнопки з темами квізу
    return QUIZ #Повертаємо state в quiz_handler = ConversationHandler

async def quiz_button_handler(update:Update, context: ContextTypes.DEFAULT_TYPE):
    quiz_prompts = {
        'quiz_prog': "Ти вчитель програмування. Постав одне цікаве коротке питання про Python. Не пиши варіантів відповіді.",
        'quiz_math': "Ти вчитель математики. Постав одну цікаву коротку логічну задачу. Не пиши відповідь.",
        'quiz_biology': "Ти вчитель біології. Постав одне цікаве коротке питання про тварин чи рослини. Не пиши відповідь."
    }
    query = update.callback_query
    await query.answer()
    if query.data == 'start':
        await start(update, context)  # Викликаємо головне меню
        return ConversationHandler.END

    if query.data == 'quiz_change':
        await quiz(update, context)
        return QUIZ

    """if query.data == 'quiz_change':
        return await quiz(update, context)"""

    if query.data == 'more_quiz':
        question = await gpt_service.add_message("Напиши ще одне питання")
    else:
        # Якщо це вибір нової теми
        gpt_service.set_prompt(quiz_prompts[query.data])
        question = await gpt_service.add_message("Напиши цікаве запитання для квізу")

    await query.edit_message_text(question)
    return ConversationHandler.END





if __name__ == '__main__':
    talk_handler = ConversationHandler(
        entry_points=[CommandHandler("talk", talk)], #викликає функцію talk
        states={
            TALK: [CallbackQueryHandler(talk_button_handler)] #викликає функцію обробки кнопок talk_button_handler
        },
        fallbacks=[CommandHandler("start", start)],

    )

    quiz_handler = ConversationHandler(
        entry_points=[CommandHandler("quiz", quiz), #Запускає функцію quiz по команді /quiz
                      CallbackQueryHandler(quiz, pattern='quiz') #Запускає функцію quiz по по натисканню кнопки з query = quiz
                      ],
        states={
            QUIZ: [CallbackQueryHandler(quiz_button_handler)]#Запускає функцію обробки кнопок вибору теми квізу
        },
        fallbacks=[]
    )



    app = ApplicationBuilder().token(TOKEN).build()
    # Обробник запуска бота або команди /start
    app.add_handler(CommandHandler("start", start))
    # Обробник команди /random
    app.add_handler(CommandHandler("random", random))
    # Обробник команди /talk викликає ConversationHandler
    app.add_handler(talk_handler)

    # Обробник команди /quiz викликає quiz_handler = ConversationHandler
    app.add_handler(quiz_handler)

    # Обробник кнопок під повідомленням random факту
    app.add_handler(CallbackQueryHandler(callback_handler))
    # Обробник команди /gpt
    app.add_handler((CommandHandler('gpt', gpt))) #Викликає функцію gpt
    # Обробник будь-яких текстових повідомлень
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Бот запущений...")
    app.run_polling()
