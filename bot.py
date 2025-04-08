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
from datetime import datetime
import pytz 
import random
# Включаем логирование (для дебага)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TOKEN = os.environ.get("BOT_TOKEN")
TZ = pytz.timezone(os.environ.get("TZ", "Asia/Almaty"))

# Хранилище подписчиков
subscribers = set()

# Индивидуальные сообщения (можно менять под своих)
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

# Обработка нажатий кнопок
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
    username = f"@{user.username}" if user.username else user.first_name

    sarcastic_responses = [
        "Интересно. А теперь попробуй сказать это клиенту.",
        "Слова — это хорошо. Продажи — лучше.",
        "Да-да, расскажи ещё. Мне нужен материал для стендапа.",
        "Если бы сообщения продавали кухни — ты был бы легендой.",
        "А теперь глубоко вдохни и иди звонить.",
        "Ого, ты умеешь печатать. А тыкать на 'позвонить' не пробовал?",
        "Запиши это в отчёт. Назови 'Великий Монолог'."
    ]

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"{username}, {sarcastic_responses[hash(username) % len(sarcastic_responses)]}"
    )

# Рассылка сообщений в 10:00
def send_morning_messages(context: CallbackContext):
    for chat_id in subscribers:
        user = context.bot.get_chat(chat_id)
        username = f"@{user.username}" if user.username else user.first_name
        msg = messages.get(username, f"{username}, пора что-то делать. Желательно полезное.")
        context.bot.send_message(chat_id=chat_id, text=msg)

# Основной запуск
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
    webhook_url = f"https://prodazhnik-bot.onrender.com/{TOKEN}"
)

if __name__ == '__main__':
    main()
def handle_message(update, context):
    user_id = update.effective_user.username or ""
    name = update.effective_user.first_name or "ты"

    responses = {
        "Arystan010": [
            f"{name}, хорош уже быть самым красивым и уверенным в комнате. Уступи место боту.",
            f"Арыстан, ты опять думаешь, что это CRM тебя боится? Мальчик ты дерзкий, но наивный."
        ],
        "Aleksandraofficial_0": [
            f"Александра, ты снова спрашиваешь бота? Попробуй сначала позвонить клиенту, потом мучай меня.",
            f"Твоя внимательность достойна награды. Но не от меня."
        ],
        "Ayanskiy01": [
            f"Аян, ты хотя бы это сообщение не проспал?",
            f"Аян, я надеюсь ты сейчас не за рулём, а то опять 'сломался'."
        ],
        "salamatmalam": [
            f"Рауан, я бы ответил тебе на твоём диалекте, но мой село-бот словарь не установлен.",
            f"Голос у тебя — как будто ты торгуешь овцами, а не кухнями."
        ],
        "Bibaryss": [
            f"Бибарыс, хватит извиняться перед клиентами. Они тебя не любят, они тебя используют.",
            f"Ты — воплощение доброты, и этим ты раздражаешь весь отдел."
        ],
        "whitey43": [
            f"Алексей, хватит писать. Лучше спроси Лию, что тебе ответить.",
            f"35 лет. С молоденькой. Но с ботом ты не потягаешься."
        ],
        "w900zx": [
            f"Лия, говори с клиентами как с ботом. Волшебно, сказочно и ни о чём.",
            f"Ты не Лия, ты персонаж из сказки. Я жду, когда прилетят единороги."
        ]
    }

    default_responses = [
        f"{name}, я тебя не знаю, но уже устал от тебя.",
        "Ты написал сообщение. Это успех. Но не для тебя.",
        "Бот тебя услышал. Но предпочёл проигнорировать.",
        "Я бы тебе ответил, но корпоративный устав запрещает общение с непрофильными элементами."
    ]

    user_responses = responses.get(user_id, default_responses)
    update.message.reply_text(random.choice(user_responses))
