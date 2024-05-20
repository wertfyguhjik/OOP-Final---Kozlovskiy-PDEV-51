import telebot
from telebot import types
from Config import TOKEN, keys
from extensions import CryptoConverter

bot = telebot.TeleBot(TOKEN)

# значения глобальных переменных будем менять внутри обработчиков нажатий на кнопку.
# да, так не рекомендуется делать.
amount = 0
quote = ""
base = ""


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.send_message(message.chat.id, f"Привет, {message.chat.first_name} \n"
                                      f"Введи сумму, потом выбери валюты для конвертации \n"
                                      f"Список доступных валют: /values")

# оставим обработчик /values как в туториале
@bot.message_handler(commands=['values'])
def values(message):
    text = "Доступные валюты: \n"
    for key in keys.keys():
        text = "\n".join((text, key, ))
    # добавим кнопку для перехода на сайт с курсами
    markup = types.InlineKeyboardMarkup()
    btn0 = types.InlineKeyboardButton("Посмотреть курсы на сайте", url="https://www.cryptocompare.com/")
    markup.add(btn0)
    bot.reply_to(message, text, reply_markup=markup)

@bot.message_handler(content_types=["text"])
def input(message):
    # записываем введённую сумму в переменную
    # исключая ввод букв и отрицательных значений
    global amount
    try:
        amount = float(message.text.strip())
    except ValueError:
        bot.reply_to(message, "Введите число!")
        bot.register_next_step_handler(message, input)
        return
    if amount > 0:
        # добавляем кнопки выбора первой валюты (значения берутся из словаря)
        # похоже, цикл игнорирует указанный row_width=2, но пусть останется так.
        markup = types.InlineKeyboardMarkup(row_width=2)
        for n in range(0, len(keys)):
            btn = types.InlineKeyboardButton(f"{list(keys)[n]}", callback_data=f"quote_{keys.get(list(keys)[n])}")
            markup.add(btn)
        bot.send_message(message.chat.id, "Какую валюту конвертируем?", reply_markup=markup)
    else:
        bot.reply_to(message, "Введите положительную сумму!")
        bot.register_next_step_handler(message, input)

# обрабатываем нажатие кнопки "quote_"
@bot.callback_query_handler(func=lambda call:call.data.startswith('quote_'))
def quote_callback(call):
    global quote
    # берём значение валюты без "quote_", то есть её код
    quote = call.data[6:]
    # добавляем кнопки выбора второй валюты, предыдущие кнопки при этом убираем
    markup = types.InlineKeyboardMarkup(row_width=2)
    for n in range(0, len(keys)):
        btn = types.InlineKeyboardButton(f"{list(keys)[n]}", callback_data=f"base_{keys.get(list(keys)[n])}")
        markup.add(btn)
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                          text="Теперь в какую?", reply_markup=markup)

# обрабатываем нажатие кнопки "base_"
@bot.callback_query_handler(func=lambda call: call.data.startswith('base_'))
def base_callback(call):
    global base
    base = call.data[5:]
    # отлавливаем конвертацию одинаковых валют
    try:
        total_base = CryptoConverter.get_price(quote, base, amount)
    except Exception as e:
        bot.send_message(call.message.chat.id, f"{e}")
    else:
        # теперь выводим результат конвертации, кнопки снова убираем
        text = (f"{amount} {quote} - это {total_base} {base} \n"
                f"Можете повторить ввод.")
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text=text)

bot.polling(none_stop=True)