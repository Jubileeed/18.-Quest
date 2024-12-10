import telebot
from telebot import types
import random

# Ваш токен бота
API_TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'

# Инициализация бота
bot = telebot.TeleBot(API_TOKEN)

# Глобальная переменная для хранения состояния игры и инвентаря для каждого пользователя
game_state = {}

# Функция для поиска предметов в комнате
def explore_room():
    items = ["старый ключ", "лампа", "бумажная карта", "неизвестный ящик"]
    found_item = random.choice(items)
    return found_item

# Функция для взаимодействия с найденным предметом
def interact_with_item(item):
    if item == "старый ключ":
        return "ключ"
    elif item == "лампа":
        return "лампа"
    elif item == "бумажная карта":
        return "карта"
    elif item == "неизвестный ящик":
        if random.randint(0, 1) == 0:
            return "сокровище"
        else:
            return "пустой ящик"
    return None

# Функция для создания клавиатуры с действиями
def create_action_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = types.KeyboardButton("Открыть дверь")
    button2 = types.KeyboardButton("Искать выход в других направлениях")
    button3 = types.KeyboardButton("Осмотреть комнату")
    keyboard.add(button1, button2, button3)
    return keyboard

# Функция для создания клавиатуры с кнопкой "Попробовать снова"
def create_retry_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    retry_button = types.KeyboardButton("Попробовать снова")
    keyboard.add(retry_button)
    return keyboard

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    game_state[user_id] = {'inventory': None}
    keyboard = create_action_keyboard()
    bot.reply_to(message, "Привет, Незнакомец!\nТы очнулся в темной комнате. Вокруг тебя ничего не видно, кроме одной двери на западе.\nТы слышишь шумы за дверью. Что будешь делать?", reply_markup=keyboard)

# Обработчик выбора действия
@bot.message_handler(func=lambda message: message.text in ['Открыть дверь', 'Искать выход в других направлениях', 'Осмотреть комнату'])
def handle_action(message):
    user_id = message.from_user.id
    choice = message.text
    inventory = game_state.get(user_id, {}).get('inventory')

    if choice == 'Открыть дверь':
        if inventory == "ключ":
            bot.reply_to(message, "Ты открыл дверь с помощью ключа и вышел из комнаты.\nПоздравляю! Ты победил.")
            del game_state[user_id]
        else:
            bot.reply_to(message, "Ты пытаешься открыть дверь, но она заперта.")
    elif choice == 'Искать выход в других направлениях':
        if inventory == "карта":
            bot.reply_to(message, "Ты нашел тайный выход на востоке, используя карту.\nПоздравляю! Ты победил.")
            del game_state[user_id]
        else:
            if random.randint(0, 1) == 0:
                bot.reply_to(message, "Ты нашёл выход за спиной!\nПоздравляю! Ты победил.")
                del game_state[user_id]
            else:
                bot.reply_to(message, "Ты не нашёл других выходов и заблудился.\nИгра закончена.", reply_markup=create_retry_keyboard())
                del game_state[user_id]
    elif choice == 'Осмотреть комнату':
        item = explore_room()
        inventory_item = interact_with_item(item)
        game_state[user_id]['inventory'] = inventory_item
        if inventory_item == "ключ":
            bot.reply_to(message, f"Ты нашел {item}. Возможно, он откроет дверь.")
        elif inventory_item == "лампа":
            bot.reply_to(message, f"Ты нашел {item} и зажёг её. Теперь ты видишь комнату лучше.")
        elif inventory_item == "карта":
            bot.reply_to(message, f"Ты нашел {item}. На ней отмечен тайный выход на востоке.")
        elif inventory_item == "сокровище":
            bot.reply_to(message, f"Ты нашел {item} в ящике! Это настоящая удача!")
        elif inventory_item == "пустой ящик":
            bot.reply_to(message, f"Ты нашел {item}, но, к сожалению, он оказался пуст.")

        keyboard = create_action_keyboard()
        bot.reply_to(message, "Что будешь делать дальше?", reply_markup=keyboard)

# Обработчик нажатия кнопки "Попробовать снова"
@bot.message_handler(func=lambda message: message.text == "Попробовать снова")
def retry_game(message):
    send_welcome(message)  # Перезапускаем игру, отправляя сообщение приветствия

# Запуск бота
bot.polling()
