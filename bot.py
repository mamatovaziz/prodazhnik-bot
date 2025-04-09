import logging
import os
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
import random

# Логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Конфигурация
TOKEN = os.environ.get("BOT_TOKEN")
TZ = pytz.timezone(os.environ.get("TZ", "Asia/Almaty"))
subscribers = set()

# Утренние персональные шутки
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

# Команда /start
def start(update: Update, context: CallbackContext):
    user = update.effective_user
    chat_id = update.effective_chat.id
    username = f"@{user.username}" if user.username else user.first_name

    subscribers.add(chat_id)

    keyboard = [
        [InlineKeyboardButton("Отписаться (но ты слабак)", callback_data="unsubscribe")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text(
        f"Привет, {username}.\n"
        f"Добро пожаловать в рассылку 'ПроснисьТыПродажник'.\n"
        f"С 10:00 ежедневно тебя будет будить не совесть, а я.",
        reply_markup=reply_markup
    )

# Команда /stop
def stop(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    if chat_id in subscribers:
        subscribers.remove(chat_id)
        update.message.reply_text("Окей, ты отписался. Мир стал чуть тише. Но твой KPI — нет.")
    else:
        update.message.reply_text("Ты и не был подписан, но уже расстроил меня.")

# Обработка кнопок
def button_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    chat_id = query.message.chat_id

    if query.data == "unsubscribe":
        if chat_id in subscribers:
            subscribers.remove(chat_id)
            keyboard = [
                [InlineKeyboardButton("Хочу вернуться (я был слаб)", callback_data="resubscribe")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            query.edit_message_text(
                text="Ты отписался. Не все рождены для давления. Кто-то выбирает путь слабого Wi-Fi.",
                reply_markup=reply_markup
            )
    elif query.data == "resubscribe":
        subscribers.add(chat_id)
        query.edit_message_text(
            text="Возвращение блудного продажника. Надеюсь, ты теперь готов к KPI."
        )

# Ответы на любые сообщения
def handle_message(update: Update, context: CallbackContext):
    user = update.effective_user
    username = user.username or ""
    name = user.first_name or "ты"

    responses = {
        "Arystan010": [
            f"{name}, хватит сверкать самоуверенностью. Она не продаёт кухни.",
            f"Арыстан, CRM не падает от взгляда. Придётся звонить."
        ],
        "Aleksandraofficial_0": [
            f"Александра, если бы мысли звонили клиентам — ты была бы чемпион.",
            f"Звонок — не проклятие. Попробуй, не бойся."
        ],
        "Ayanskiy01": [
            f"Аян, проспал сообщение? Шок-контент.",
            f"Аян, включи будильник и режим продажника."
        ],
        "salamatmalam": [
            f"Рауан, 'брат' — не универсальный скрипт продаж.",
            f"Рауан, клиенты — не твои соседи по аулу. Тон деловой."
        ],
        "Bibaryss": [
            f"Бибарыс, хватит уговаривать клиентов. Дави по скрипту.",
            f"Вежливость — хорошо. Но закрытые сделки — лучше."
        ],
        "whitey43": [
            f"Алексей, CRM ждёт. Лия не поможет с отчётами.",
            f"35 лет. С молоденькой. Но всё ещё нет планов по продажам."
        ],
        "w900zx": [
            f"Лия, с клиентами не надо как с единорогами. Жёстче.",
            f"Сказка — сказкой, но кухня сама себя не продаст."
        ]
    }

    general_responses = [
        "Интересно. А теперь позвони кому-нибудь, герой.",
        "Ты умеешь писать. Может теперь — продавать?",
        "Слова не закрывают сделки. Действуй.",
        "Может, CRM тоже хочет узнать об этом?",
        "Если бы клавиатура считалась KPI, ты бы был топ.",
        "Пока ты пишешь мне — кто-то делает продажу. И это не ты.",
        "Отличный текст. А где деньги, Лебовски?"
    ]

    if username in responses:
        reply = random.choice(responses[username])
    else:
        reply = f"{name}, {random.choice(general_responses)}"

    context.bot.send_message(chat_id=update.effective_chat.id, text=reply)

# Утренняя рассылка
def send_morning_messages(context: CallbackContext):
    for chat_id in subscribers:
        user = context.bot.get_chat(chat_id)
        username = f"@{user.username}" if user.username else user.first_name
        msg = messages.get(username, f"{username}, пора что-то делать. Желательно полезное.")
        context.bot.send_message(chat_id=chat_id, text=msg)

# Запуск бота
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

