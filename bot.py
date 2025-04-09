import logging
import os
import random
import openai
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackContext,
    MessageHandler,
    Filters,
    CallbackQueryHandler
)
from apscheduler.schedulers.background import BackgroundScheduler
import pytz

# Логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Конфигурация
TOKEN = os.environ.get("BOT_TOKEN")
TZ = pytz.timezone(os.environ.get("TZ", "Asia/Almaty"))
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

subscribers = set()

# Команда /start
def start(update: Update, context: CallbackContext):
    user = update.effective_user
    chat_id = update.effective_chat.id
    username = f"@{user.username}" if user.username else user.first_name

    subscribers.add(chat_id)

    keyboard = [[InlineKeyboardButton("Отписаться (но ты слабак)", callback_data="unsubscribe")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text(
        f"Привет, {username}.\n"
        f"Ты подключился к 'ПроснисьТыПродажник'.\n"
        f"С 10:00 ежедневно я буду вставать раньше тебя, чтобы убедиться: ты не просрал KPI.",
        reply_markup=reply_markup
    )

# Команда /stop
def stop(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    if chat_id in subscribers:
        subscribers.remove(chat_id)
        update.message.reply_text("Окей, ты отписался. KPI сам себя не провалит, но ты попробуешь.")
    else:
        update.message.reply_text("Ты даже не был подписан. Легенда невидимого фронта.")

# Обработка кнопок
def button_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    chat_id = query.message.chat_id

    if query.data == "unsubscribe":
        subscribers.discard(chat_id)
        keyboard = [[InlineKeyboardButton("Вернуться (в ад продаж)", callback_data="resubscribe")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(
            text="Ты сбежал. Не все рождены для звонков. Кто-то выбирает путь 'просто посидеть в офисе'.",
            reply_markup=reply_markup
        )
    elif query.data == "resubscribe":
        subscribers.add(chat_id)
        query.edit_message_text(text="Возвращение блудного менеджера. Добро пожаловать в пекло.")

# GPT-сарказм
def generate_response(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Ты корпоративный ИИ-бот, дерзкий, язвительный, говоришь с сарказмом и агрессией. Мотивируешь через стыд и жёсткие подколы."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.95,
            max_tokens=120
        )
        return response.choices[0].message['content'].strip()
    except Exception as e:
        return f"Ошибка ИИ. Видимо, ты перегрузил мой интеллект своей глупостью. ({e})"

# Ответ на сообщения
def handle_message(update: Update, context: CallbackContext):
    user = update.effective_user
    name = user.first_name or "ты"
    text = update.message.text

    reply = generate_response(text)
    context.bot.send_message(chat_id=update.effective_chat.id, text=f"{name}, {reply}")

# Утренняя рассылка
def send_morning_messages(context: CallbackContext):
    for chat_id in subscribers:
        try:
            user = context.bot.get_chat(chat_id)
            username = f"@{user.username}" if user.username else user.first_name
            msg = generate_response(f"Напомни {username} в 10:00, что он должен делать продажи, но с язвительным и мотивационным стилем.")
            context.bot.send_message(chat_id=chat_id, text=msg)
        except Exception as e:
            logging.warning(f"Ошибка при отправке утреннего сообщения: {e}")

# Запуск
def main():
    updater = Updater(token=TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("stop", stop))
    dispatcher.add_handler(CallbackQueryHandler(button_callback))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    scheduler = BackgroundScheduler()
    scheduler.add_job(lambda: send_morning_messages(None), 'cron', hour=10, minute=0, timezone=TZ)
    scheduler.start()

    updater.start_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        url_path=TOKEN,
        webhook_url=f"https://prodazhnik-bot.onrender.com/{TOKEN}"
    )

if __name__ == '__main__':
    main()



