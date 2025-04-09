import os
import openai
from openai import OpenAI
from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Получаем токены из переменных окружения
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Подключаем OpenAI с новым клиентом
client = OpenAI(api_key=OPENAI_API_KEY)

def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    update.message.reply_html(
        rf"Привет, {user.mention_html()}! Я бот, запрограммированный на сарказм. Дерзай.",
        reply_markup=ForceReply(selective=True),
    )

def help_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Напиши мне что-нибудь. Я подумаю, стоит ли отвечать.")

def handle_message(update: Update, context: CallbackContext) -> None:
    user_input = update.message.text

    try:
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Ты саркастичный, язвительный бот, которому всё надоело."},
                {"role": "user", "content": user_input},
            ],
            temperature=0.9
        )
        reply = completion.choices[0].message.content
    except Exception as e:
        reply = f"Извини, я поломался. Причина: {e}"

    update.message.reply_text(reply)

def main() -> None:
    updater = Updater(token=TELEGRAM_BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()



