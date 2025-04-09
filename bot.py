import os
import openai
from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Получаем токен бота из переменных окружения
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not TELEGRAM_BOT_TOKEN or not OPENAI_API_KEY:
    raise ValueError("Отсутствует TELEGRAM_BOT_TOKEN или OPENAI_API_KEY в переменных окружения.")

# Инициализация клиента OpenAI
openai.api_key = OPENAI_API_KEY

def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    update.message.reply_html(
        rf"Привет, {user.mention_html()}! Я бот с искусственным интеллектом и сарказмом. Попробуй меня!",
        reply_markup=ForceReply(selective=True),
    )

def help_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Просто отправь мне сообщение, и я отвечу с изрядной долей сарказма.")

def handle_message(update: Update, context: CallbackContext) -> None:
    user_message = update.message.text

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Ты — саркастичный и язвительный искусственный интеллект."},
                {"role": "user", "content": user_message},
            ],
            temperature=0.9,
            max_tokens=150,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0.6,
        )
        bot_reply = response.choices[0].message['content'].strip()
    except Exception as e:
        bot_reply = f"Ой, произошла ошибка: {e}. Похоже, я сломался. Ура!"

    update.message.reply_text(bot_reply)

def main() -> None:
    updater = Updater(TELEGRAM_BOT_TOKEN)

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    updater.start_polling()
    updater.idle()

if _name_ == '_main_':
    main()



