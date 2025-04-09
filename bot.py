import logging
import os
import random
import requests
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

# Логируем всё, когда кто-то не запланил
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TOKEN = os.environ.get("BOT_TOKEN")
TZ = pytz.timezone(os.environ.get("TZ", "Asia/Almaty"))
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")  # Безопасно!

subscribers = set()

# Индивидуалки
messages = {
    "@Arystan010": "Арыстан, снова понедельник. Очаровывать клиентов взглядом — это не стратегия.",
    "@w900zx": "Лия, добавь к сказочной подаче немного коммерческого террора."
}

# /start

def start(update: Update, context: CallbackContext):
    user = update.effective_user
    chat_id = update.effective_chat.id
    username = f"@{user.username}" if user.username else user.first_name
    subscribers.add(chat_id)

    keyboard = [[InlineKeyboardButton("Отписаться (но ты слабак)", callback_data="unsubscribe")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text(
        f"Привет, {username}.\n🌟 Это 'ПроснисьТыПродажник'! С 10:00 я буду тебя дерзко поднимать.",
        reply_markup=reply_markup
    )

# /stop

def stop(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    if chat_id in subscribers:
        subscribers.remove(chat_id)
        update.message.reply_text("Ладно, отписался. Теперь кому я буду посылать гифки?")
    else:
        update.message.reply_text("Ты и не был подписан, но уже портишь мне настроение.")

# Кнопки

def button_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    chat_id = query.message.chat_id
    if query.data == "unsubscribe":
        subscribers.discard(chat_id)
        query.edit_message_text(
            "Ты сбежал. Да же не важно. Продажи без тебя стали только грустнее."
        )

# Ответ на сообщения

def handle_message(update: Update, context: CallbackContext):
    user = update.effective_user
    username = user.username or ""
    name = user.first_name or "ты"

    responses = {
        "Arystan010": [
            f"{name}, хватит сверкать самоуверенностью. Она не продаёт кухни."
        ],
        "w900zx": [
            f"{name}, с клиентами не надо как с единорогами. Жёстче."
        ]
    }

    general = [
        f"{name}, если бы письма делали план, ты бы был герой.",
        "Ты споришь со мной? Странный выбор, я же бот.",
        "Ты опять пишешь, вместо того чтобы звонить? 🤦"
    ]

    reply = random.choice(responses.get(username, general))
    context.bot.send_message(chat_id=update.effective_chat.id, text=reply)

    if random.random() < 0.3:
        gif_url = "https://media.giphy.com/media/3o6Zt481isNVuQI1l6/giphy.gif"
        context.bot.send_animation(chat_id=update.effective_chat.id, animation=gif_url)

# Утренняя дерзкая поднятка

def send_morning_messages(context: CallbackContext):
    for chat_id in subscribers:
        user = context.bot.get_chat(chat_id)
        username = f"@{user.username}" if user.username else user.first_name
        msg = messages.get(username, f"{username}, пора что-то делать. Желательно полезное.")
        context.bot.send_message(chat_id=chat_id, text=msg)

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


