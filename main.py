import telebot
import os
from telebot.types import Message, BusinessConnection
from telebot.apihelper import ApiTelegramException

# Создайте переменную окружения TOKEN с токеном вашего бота
bot = telebot.TeleBot(os.environ.get("TOKEN"))

# Контактные данные менеджера
manager_contact = (
    "<b>@TehnoViktor_Manager</b>"
)

# Сообщение приветствия с использованием HTML
warning_message = (
    f"Здравствуйте, $name$ 👋\n"
    "Сейчас Вам ответим 👨‍💻\n\n"
    "<u>ОСТОРОЖНО! Вам могут написать мошенники от нашего имени!</u>\n"
    "<b>Мы не берем предоплату за товар, у нас все в наличии!</b>\n\n"
    "Связь с нами: <b>@TehnoViktor_Manager</b>\n"
    "+79495902364 - <b>Виктор</b>"
)

# Словарь для отслеживания, кому отправлено приветственное сообщение
replied_users = set()

# Статистика
statistics = {
    "messages_sent": 0,
    "users_banned": 0
}

# Обработчик для обновлений бизнес-соединений
@bot.message_handler(func=lambda message: isinstance(message, BusinessConnection))
def handle_business_connection(message: BusinessConnection):
    if message.is_enabled:
        print(f"Бизнес-соединение с пользователем {message.user.username} активировано.")
    else:
        print(f"Бизнес-соединение с пользователем {message.user.username} деактивировано.")

# Обработчик для получения сообщений в бизнес-режиме
@bot.message_handler(func=lambda message: isinstance(message, Message) and message.business_connection_id)
def handle_business_message(message: Message):
    # Проверяем, имеет ли бот доступ к чату
    if message.business_connection.can_reply:
        bot.send_message(
            message.chat.id,
            "Это сообщение отправлено от имени бизнес-аккаунта.",
            parse_mode="HTML"
        )
        statistics['messages_sent'] += 1

# Статистика
@bot.message_handler(commands=['stats'])
def send_stats(message: Message):
    if message.chat.type == "private" and message.from_user.username == "lonkigor":
        bot.send_message(
            message.chat.id,
            (f"Статистика бота:\n"
             f"Отправлено сообщений: {statistics['messages_sent']}\n"
             f"Забанено пользователей: {statistics['users_banned']}"),
            parse_mode="HTML"
        )

@bot.message_handler(func=lambda message: True)
def handle_message(message: Message):
    user_id = message.from_user.id
    text = message.text.lower()

    # Игнорируем сообщения от каналов и пользователей с именем "Group"
    if message.chat.type == "channel" or message.from_user.username == "Group":
        return

    # Отправка приветственного сообщения при первом сообщении
    if user_id not in replied_users:
        # Получаем имя пользователя для подстановки в приветствие
        bot.reply_to(
            message,
            warning_message.replace("$name$", message.from_user.first_name),
            parse_mode="HTML"
        )
        replied_users.add(user_id)
        statistics['messages_sent'] += 1
    elif "контакт" in text or "можно купить" in text:
        bot.reply_to(
            message,
            f"Здравствуйте, {message.from_user.first_name}, вот наши контактные данные:\n{manager_contact}",
            parse_mode="HTML"
        )
        statistics['messages_sent'] += 1

# Запуск бота
print("Бот запущен...")
bot.polling()
