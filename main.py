import logging
import os
from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackContext
from telegram.ext import Dispatcher
from telegram.ext import BusinessConnectionHandler
from telegram import filters  # Используем filters с маленькой буквы

# Включите логирование для отслеживания ошибок и отладочной информации
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Токен вашего бота из переменной окружения
BOT_TOKEN = os.environ.get("TOKEN")

# Функция для обработки команд
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Здравствуйте! Я ваш бизнес-бот. Чем могу помочь?')

# Обработка входящих бизнес-сообщений
def handle_business_message(update: Update, context: CallbackContext) -> None:
    # Проверка, если сообщение от бизнес-аккаунта
    if update.business_message:
        # Можно сделать любые действия с сообщением, например, отправить ответ
        update.message.reply_text("Сообщение от бизнес-аккаунта обработано.")

# Обработка изменений связи с бизнес-аккаунтом
def handle_business_connection(update: Update, context: CallbackContext) -> None:
    if update.business_connection:
        business_connection = update.business_connection
        logger.info(f"Business connection established with ID: {business_connection.id}")
        
        if business_connection.can_reply:
            update.message.reply_text("Я могу отвечать от имени вашего бизнес-аккаунта!")

# Функция для отправки сообщений от имени бизнеса
def send_business_message(update: Update, context: CallbackContext) -> None:
    if update.business_connection and update.business_connection.can_reply:
        # Отправить сообщение от имени бизнес-аккаунта
        context.bot.send_message(chat_id=update.message.chat_id, text="Привет, это сообщение от вашего бизнес-бота!", 
                                 business_connection_id=update.business_connection.id)

# Обработка ошибок
def error(update: Update, context: CallbackContext) -> None:
    logger.warning(f'Ошибка: {context.error}')

def main():
    # Создание объекта бота
    updater = Updater(BOT_TOKEN)

    # Диспетчер для регистрации обработчиков
    dispatcher: Dispatcher = updater.dispatcher

    # Обработчик команд
    dispatcher.add_handler(CommandHandler('start', start))

    # Обработчик бизнес-сообщений
    dispatcher.add_handler(BusinessConnectionHandler(handle_business_connection))

    # Обработчик входящих бизнес-сообщений
    dispatcher.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_business_message))  # Используем filters

    # Обработчик для отправки сообщений от имени бизнеса
    dispatcher.add_handler(CommandHandler('send_business_message', send_business_message))

    # Логирование ошибок
    dispatcher.add_error_handler(error)

    # Запуск бота
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
