from telegram import Update, Bot, BusinessConnection
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
import logging
import os

# Включение логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Задайте ваш токен, полученный от @BotFather
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")  # Замените на токен вашего бота или используйте переменную окружения

# Инициализация бота и его приложения
app = Application.builder().token(TELEGRAM_TOKEN).build()

# Хранение активных бизнес-подключений
business_connections = {}

# Обработчик для команды /start
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Здравствуйте! Чем могу помочь?")

# Обработчик бизнес-соединений
async def handle_business_connection(update: Update, context: CallbackContext):
    business_connection = update.business_connection
    if business_connection:
        business_connections[business_connection.id] = business_connection
        await context.bot.send_message(
            business_connection.user_chat_id,
            f"Бизнес-подключение установлено: {business_connection.user.first_name}"
        )
        logger.info("Новое бизнес-подключение от %s", business_connection.user.first_name)

# Обработчик сообщений от бизнес-пользователей
async def handle_business_message(update: Update, context: CallbackContext):
    if update.message:
        business_connection_id = update.message.business_connection_id
        business_connection = business_connections.get(business_connection_id)
        
        if business_connection and business_connection.can_reply:
            response_text = "Спасибо за ваше сообщение! Мы скоро с вами свяжемся."
            await context.bot.send_message(
                chat_id=business_connection.user_chat_id,
                text=response_text,
                business_connection_id=business_connection.id
            )
            logger.info("Ответ отправлен бизнес-пользователю: %s", business_connection.user.first_name)
        else:
            logger.warning("Нет разрешения на ответ в чате с ID %s", update.message.chat_id)

# Основной обработчик текстовых сообщений
async def echo(update: Update, context: CallbackContext):
    await update.message.reply_text("Спасибо за ваше сообщение. Мы скоро с вами свяжемся!")

# Регистрация обработчиков
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.BusinessConnection.ALL, handle_business_connection))
app.add_handler(MessageHandler(filters.BusinessMessage.ALL, handle_business_message))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

# Запуск бота
if __name__ == "__main__":
    app.run_polling()
