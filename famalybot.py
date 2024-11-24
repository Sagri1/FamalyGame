import telebot
from telebot import types

# Переменные
users_feature = []
users_list = []
game_started = False
ver = '3.10'

# Токен
token='8144689811:AAHnhzpXuNLs_ZrNlohCMI1ukPTVD2AOYiY'
bot=telebot.TeleBot(token)

# Приветствие
@bot.message_handler(commands=['start'])
def start_message(message):
    markup = types.InlineKeyboardMarkup()
    button_continue = types.InlineKeyboardButton("Продолжить", callback_data="continue")
    markup.add(button_continue)    
    bot.send_message(message.chat.id, 'Приветствую вас! Правила игры очень просты — вы мне рассказываете свой факт и имя. '
                                        'Потом я выбираю факт, который мне понравился, и рисую изображение, отражающее этот факт. '
                                        'Чтобы победить, надо угадать имя человека, чей это факт. ' + ver, reply_markup=markup)

# Обработка нажатия на кнопку "Продолжить"
@bot.callback_query_handler(func=lambda call: call.data == "continue")
def continue_game(call):
    bot.send_message(call.message.chat.id, "Добавим участников.")
    # Вызываем функцию для добавления участника
    add_participant(call.message)

# Добавление участника
def add_participant(message):
    msg = bot.send_message(message.chat.id, "Введите имя участника и его особенность (через запятую):")
    bot.register_next_step_handler(msg, process_participant)

def process_participant(message):
    try:
        name, feature = message.text.split(',')
        name = name.strip()
        feature = feature.strip()
        users_list.append(name)
        users_feature.append(feature)
        bot.send_message(message.chat.id, f"Добавлен участник: {name}")
        lobby(message)
    except ValueError:
        bot.send_message(message.chat.id, "Ошибка ввода. Пожалуйста, введите имя и особенность через запятую.")

def lobby(message):
    markup = types.InlineKeyboardMarkup()
    button_new_player = types.InlineKeyboardButton("Новый участник", callback_data="new_player")
    markup.add(button_new_player)
    
    # Добавляем кнопку "Начать", если участников 2 или более
    if len(users_list) >= 2: 
        button_game = types.InlineKeyboardButton("Начать", callback_data="game")
        markup.add(button_game)

    # Отправка сообщения с участниками в формате строки
    participants_list = "\n".join(users_list)  # Преобразуем список в строку
    bot.send_message(message.chat.id, f"Участники:\n{participants_list}", reply_markup=markup)

# Обработка нажатия на кнопку "Новый участник"
@bot.callback_query_handler(func=lambda call: call.data == "new_player")
def on_new_player(call):
    add_participant(call.message)

# Обработка нажатия на кнопку "Начать"
@bot.callback_query_handler(func=lambda call: call.data == "game")
def start_game(call):
    global game_started
    game_started = True
    current_round = 0
    total_rounds = len(users_list)  # Количество раундов равно количеству участников

    bot.send_message(call.message.chat.id, f"Игра начата! Всего раундов: {total_rounds}.")
    game(call, current_round)

def game(call, current_round):
    for i in range(len(users_list)):
        markup = types.InlineKeyboardMarkup()
        if current_round < len(users_list):
            name = users_list[current_round]
            feature = users_feature[current_round]
            bot.send_message(call.message.chat.id, f"Раунд {current_round + 1}")
            bot.send_message(call.message.chat.id, f"Кто это, если его особенность: {users_feature[current_round]} ?")

            msg = bot.send_message(call.message.chat.id, f"{name}, ваш ответ:")
            bot.register_next_step_handler(msg, lambda m: check_answer(m, name, current_round))
        else:
            bot.send_message(call.message.chat.id, "Игра завершена!")

def check_answer(message, correct_name, current_round):
    answer = message.text.strip().lower()

    if answer == correct_name.lower():
        bot.send_message(message.chat.id, "Правильно! Вы угадали!")
    else:
        bot.send_message(message.chat.id, f"Неправильно. Это был {correct_name}.")
    
    game(message, current_round + 1)

# Запуск
bot.infinity_polling()
