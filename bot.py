import logging
import os
import random
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
from datetime import datetime
import pytz
from openai import OpenAI

# Настройка клиента OpenAI
client = OpenAI()

# Логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Переменные окружения
TELEGRAM_BOT_TOKEN = os.environ.get("BOT_TOKEN")
TZ = pytz.timezone(os.environ.get("TZ", "Asia/Almaty"))

subscribers = set()

messages = {
    "@Arystan010": "Арыстан, снова понедельник. Очаровывать клиентов взглядом — это не стратегия.",
    "@Aleksandraofficial_0": "Александра, если клиенту не позвонить — он не купит кухню телепатически.",
    "@Ayanskiy01": "Аян, если ты читаешь это — ты проснулся. Это уже достижение.",
    "@salamatmalam": "Рауан, клиенты — это не соседи. Перестань говорить 'брат, ща всё будет'.",
    "@Bibaryss": "Бибарыс, клиент — не мама. Не надо быть таким вежливым. Дави.",
    "@whitey43": "Алексей, KPI — это не роман. Переключись с Лии на звонки.",
    "@w900zx": "Лия, добавь к своей сказочной подаче немного коммерческого террора.",
    "@mystery": "Едил, твоё авто болеет чаще, чем ты работаешь. Вперёд, воин!"
}

# Команды

def start(update: Update, context: CallbackContext):
    user = update.effective_user
    chat_id = update.effective_chat.id
    username = f"@{user.username}" if user.username else user.first_name
    subscribers.add(chat_id)

    keyboard = [[InlineKeyboardButton("Отписаться (но ты слабак)", callback_data="unsubscribe")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text(
        f"Привет, {username}.\nДобро пожаловать в рассылку 'ПроснисьТыПродажник'.\nС 10:00 ежедневно тебя будет будить не совесть, а я.",
        reply_markup=reply_markup
    )

def stop(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    if chat_id in subscribers:
        subscribers.remove(chat_id)
        update.message.reply_text("Окей, ты отписался. Мир стал чуть тише. Но твой KPI — нет.")
    else:
        update.message.reply_text("Ты и не был подписан, но уже расстроил меня.")

def button_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    chat_id = query.message.chat_id

    if query.data == "unsubscribe":
        if chat_id in subscribers:
            subscribers.remove(chat_id)
            keyboard = [[InlineKeyboardButton("Хочу вернуться (я был слаб)", callback_data="resubscribe")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            query.edit_message_text("Ты отписался. Не все рождены для давления. Кто-то выбирает путь слабого Wi-Fi.", reply_markup=reply_markup)

    elif query.data == "resubscribe":
        subscribers.add(chat_id)
        query.edit_message_text("Возвращение блудного продажника. Надеюсь, ты теперь готов к KPI.")

# OpenAI ответ

def generate_ai_reply(prompt):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Ты язвительный и саркастичный помощник продаж."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"ИИ лёг. Причина: {str(e)}"

# Ответ на любое сообщение

def handle_message(update: Update, context: CallbackContext):
    prompt = update.message.text
    reply = generate_ai_reply(prompt)
    update.message.reply_text(reply)

# Утренняя рассылка

def send_morning_messages(context: CallbackContext):
    for chat_id in subscribers:
        user = context.bot.get_chat(chat_id)
        username = f"@{user.username}" if user.username else user.first_name
        msg = messages.get(username, f"{username}, пора что-то делать. Желательно полезное.")
        context.bot.send_message(chat_id=chat_id, text=msg)

# Запуск

def main():
    updater = Updater(token=TELEGRAM_BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("stop", stop))
    dispatcher.add_handler(CallbackQueryHandler(button_callback))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    scheduler = BackgroundScheduler()
    scheduler.add_job(lambda: send_morning_messages(None), 'cron', hour=10, minute=0, timezone=TZ)
    scheduler.start()

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()




