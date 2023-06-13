# Создаем колоду с трюками

# Dictionary to store game scores
calculate_score = {}

deck_for_long_tricks = [
    "Фс нолли пивот",
    "Бс нолли пивот",
    "Фс фейки пивот",
    "Бс фейки пивот",
    "Фс нолли шовит",
    "Бс нолли шовит",
    "Фс фейки шовит",
    "Бс фейки шовит",
    "Фс Попшовит",
    "Бс Попшовит",
    "Фс свитч попшовит",
    "Бс свитч попшовит",
    "Фс нк",
    "Бс нк",
    "Фс свитч нк",
    "Бс свитч нк",
    "Нк попшав",
    "Свитч нк попшав",
    "Кросс степ",
    "Беквард кросс степ",
    "Питер пен",
    "Беквард Питер пен",
    "Фс пирует",
    "Бс пирует",
    "Степ 180",
    "Степ 360",
    "Гострайд",
    "Кейвман",
    "Тайгер 180",
    "Тайгер 360",
    "Тайгер 540",
    "Свитч тайгер 180",
    "Свитч тайгер 360",
    "Свитч тайгер 540",
    "Фейки аеро греб",
    "Нолли аеро греб"
]


import datetime
import time
import os
import telebot
import random
import os
from telebot import TeleBot
from keyboa import Keyboa

# Важные переменные

token = "token_your_bot"  # токен бота
bot = telebot.TeleBot(token)  # Переменная бота
banned_users = set()  # Список забаненных пользователей
authorized_users = {}  # Список авторизованных пользователей

num_var = ["1", "2", "3", "4", "5"]

kb_of_num = Keyboa(items=num_var, copy_text_to_callback=True, items_in_row=5)

# Важные переменные



# функция заморозки
def freeze(duration):
    time.sleep(duration * 60)

# Функция защиты от дурака, которая блокирует пользователя на указанное количество секунд
def protect_from_spam(func):
    cooldown = 60  # Время блокировки в секундах

    def wrapper(message):
        chat_id = message.chat.id

        if chat_id in banned_users:
            print("User is banned:", chat_id)
            return

        current_time = time.time()
        last_call = func.last_call.get(chat_id, 0)

        if current_time - last_call >= cooldown:
            func.last_call[chat_id] = current_time
            func(message)
        else:
            bot.send_message(chat_id, "Please wait before sending another message.")

    func.last_call = {}  # Словарь для хранения времени последнего вызова функции
    return wrapper


# функция для вызова комманды /start
@bot.message_handler(commands=['start'])
@protect_from_spam
def send_welcome(message):
    bot.send_message(chat_id=message.chat.id, text="Выберите игру:\n/game_of_skate\n/game_of_longboard")


@bot.message_handler(commands=['end'])
def end_game(message, winner):
    if winner:
        bot.send_message(chat_id=message.chat.id, text="Конец игры\nВыиграл игрок: " + str(winner))
    else:
        bot.send_message(chat_id=message.chat.id, text="Конец игры\nНет победителя")


def game(n, message):
    players = []
    for i in range(n):
        players.append("Player" + str(i + 1))

    bot.send_message(chat_id=message.chat.id, text="У первого игрока есть 2 минуты на выполнение первого трюка")

    trick_status = {}  # Dictionary to track the trick completion status for each player

    for player in players:
        time.sleep(2)
        key_command = ['Сделал', 'Не сделал']

        @bot.callback_query_handler(func=lambda call: True)
        def handle_callback(call):
            if call.data in key_command:
                trick = call.data
                trick_status[player] = trick  # Update the trick status for the current player

                bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                              reply_markup=None)
                game_long(n, call.message)

        @bot.message_handler(func=lambda message: True)
        def handle_other_messages(message):
            bot.send_message(chat_id=message.chat.id, text="Неизвестная команда. Используйте /start для начала.")

        key_choice = Keyboa(items=key_command, copy_text_to_callback=True, items_in_row=2)
        bot.send_message(chat_id=message.chat.id, text="Трюк для " + player, reply_markup=key_choice())

    # Select the winners among the players who have performed all the tricks
    winners = [player for player, trick in trick_status.items() if trick == 'Сделал']
    if winners:
        winner = random.choice(winners)
        end_game(message, winner)
    else:
        bot.send_message(chat_id=message.chat.id, text="Ни один из игроков не выполнил все трюки")



def game_long(n, message):
    if 1 <= n <= 5:
        for i in range(n):
            # Выбираем случайные трюки из колоды
            hand = random.sample(deck_for_long_tricks, 5)

            # Отправляем пользователю список выбранных трюков
            bot.send_message(chat_id=message.chat.id,
                             text="Линия для игрока " + str(i + 1) + "\n" + f"Твоя линия: {', '.join(hand)}")

        game(n, message)
    else:
        bot.send_message(chat_id=message.chat.id, text="Вы ввели неверное значение. Попробуйте снова.")


@bot.message_handler(commands=['game_of_longboard'])
@protect_from_spam
def request_longboard_players(message):
    bot.send_message(chat_id=message.chat.id, text="Введите кол-во игроков от 1 до 5:", reply_markup=kb_of_num())

    @bot.callback_query_handler(func=lambda call: True)
    def handle_callback(call):
        if call.data in num_var:
            n = int(call.data)
            bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=None)
            game_long(n, call.message)

    @bot.message_handler(func=lambda message: True)
    def handle_other_messages(message):
        bot.send_message(chat_id=message.chat.id, text="Неизвестная команда. Используйте /start для начала.")


# Запуск бота
bot.polling()
