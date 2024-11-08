import logging
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from telegram.ext import BusinessConnectionHandler

# Включите логирование для отслеживания ошибок и отладочной информации
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Токен вашего бота
BOT_TOKEN = 'YOUR_BOT_TOKEN'

# Функция для обработки команд
async def start(update: Update, context: CallbackContext) -> None:
    if update.message:
        await update.message.reply_text('Здравствуйте! Я ваш бизнес-бот. Чем могу помочь?')

# Обработка входящих бизнес-сообщений
async def handle_business_message(update: Update, context: CallbackContext) -> None:
    # Проверка, если сообщение от бизнес-аккаунта
    if update.business_message:
        # Проверяем, что update.message существует перед попыткой отправить ответ
        if update.message:
            await update.message.reply_text("Сообщение от бизнес-аккаунта обработано.")
        else:
            logger.warning("Получено сообщение без объекта message.")

# Обработка изменений связи с бизнес-аккаунтом
async def handle_business_connection(update: Update, context: CallbackContext) -> None:
    if update.business_connection:
        business_connection = update.business_connection
        logger.info(f"Business connection established with ID: {business_connection.id}")
        
        if business_connection.can_reply:
            if update.message:
                await update.message.reply_text("Я могу отвечать от имени вашего бизнес-аккаунта!")
            else:
                logger.warning("Получено сообщение без объекта message.")

# Функция для отправки сообщений от имени бизнеса
async def send_business_message(update: Update, context: CallbackContext) -> None:
    if update.business_connection and update.business_connection.can_reply:
        # Отправить сообщение от имени бизнес-аккаунта
        if update.message:
            await context.bot.send_message(chat_id=update.message.chat_id, text="Привет, это сообщение от вашего бизнес-бота!", 
                                           business_connection_id=update.business_connection.id)
        else:
            logger.warning("Получено сообщение без объекта message.")

# Обработка ошибок
async def error(update: Update, context: CallbackContext) -> None:
    logger.warning(f'Ошибка: {context.error}')

def main():
    # Создание объекта приложения
    application = Application.builder().token(BOT_TOKEN).build()

    # Регистрация обработчиков
    application.add_handler(CommandHandler('start', start))
    application.add_handler(BusinessConnectionHandler(handle_business_connection))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_business_message))
    application.add_handler(CommandHandler('send_business_message', send_business_message))

    # Логирование ошибок
    application.add_error_handler(error)

    # Запуск бота
    application.run_polling()

if __name__ == '__main__':
    main()
