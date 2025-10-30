import telebot
from telebot import types

# 🔑 ТВОИ ДАННЫЕ
TOKEN = "8301682057:AAFNA8W88VhAp9pRMdb8MBYScUOx1PbdOSQ"
ADMIN_ID = 8183780518  # пример: 512345678

bot = telebot.TeleBot(TOKEN)
user_data = {}

# ---------- Главное меню ----------
def main_menu(chat_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("📦 Сделать заказ")
    btn2 = types.KeyboardButton("ℹ️ Контакты")
    btn3 = types.KeyboardButton("💊 Помощь")
    markup.add(btn1)
    markup.add(btn2, btn3)
    bot.send_message(chat_id, "Выберите действие:", reply_markup=markup)

# ---------- Команда /start ----------
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "👋 Здравствуйте! Добро пожаловать мы вам поможем заказать лекарства .")
    main_menu(message.chat.id)

# ---------- Контакты ----------
@bot.message_handler(func=lambda message: message.text == "ℹ️ Контакты")
def contacts(message):
    bot.send_message(message.chat.id, "📞 По вопросам обращаться: @ingotiv_228\n🏪")

# ---------- Помощь ----------
@bot.message_handler(func=lambda message: message.text == "💊 Помощь")
def help(message):
    bot.send_message(message.chat.id, "Чтобы оформить заказ, нажмите 📦 Сделать заказ и следуйте шагам.")

# ---------- Сделать заказ ----------
@bot.message_handler(func=lambda message: message.text == "📦 Сделать заказ")
def make_order(message):
    bot.send_message(message.chat.id, "Введите название лекарства 💊:")
    user_data[message.chat.id] = {'step': 'medicine'}

# ---------- Этапы оформления заказа ----------
@bot.message_handler(func=lambda message: message.chat.id in user_data)
def handle_order(message):
    chat_id = message.chat.id
    step = user_data[chat_id]['step']

    if step == 'medicine':
        user_data[chat_id]['medicine'] = message.text
        bot.send_message(chat_id, "🏙️ В каком городе оформить заказ?")
        user_data[chat_id]['step'] = 'city'

    elif step == 'city':
        user_data[chat_id]['city'] = message.text
        bot.send_message(chat_id, "📦 Сколько упаковок нужно?")
        user_data[chat_id]['step'] = 'quantity'

    elif step == 'quantity':
        user_data[chat_id]['quantity'] = message.text
        bot.send_message(chat_id, "Введите ваш номер телефона от Telegram или от Whatsapp что бы мы могли с вами связаться 📞:")
        user_data[chat_id]['step'] = 'phone'

    elif step == 'phone':
        user_data[chat_id]['phone'] = message.text
        confirm_order(chat_id)

# ---------- Подтверждение заказа ----------
def confirm_order(chat_id):
    order = user_data[chat_id]
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("✅ Подтвердить", callback_data="confirm"))
    markup.add(types.InlineKeyboardButton("❌ Отменить", callback_data="cancel"))

    bot.send_message(chat_id,
        f"Проверьте заказ:\n\n"
        f"💊 Лекарство: {order['medicine']}\n"
        f"🏙️ Город: {order['city']}\n"
        f"📦 Количество: {order['quantity']}\n"
        f"📞 Телефон: {order['phone']}\n\n"
        f"Подтвердите, если всё верно 👇",
        reply_markup=markup
    )

# ---------- Обработка кнопок ----------
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat_id = call.message.chat.id
    if call.data == "confirm":
        order = user_data.get(chat_id)
        if order:
            send_order_to_admin(order, chat_id)
            bot.send_message(chat_id, "✅ Спасибо! Ваш заказ отправлен.")
            user_data.pop(chat_id, None)
        else:
            bot.send_message(chat_id, "⚠️ Ошибка: данные заказа не найдены.")
        main_menu(chat_id)

    elif call.data == "cancel":
        bot.send_message(chat_id, "❌ Заказ отменён.")
        user_data.pop(chat_id, None)
        main_menu(chat_id)

# ---------- Отправка заказа админу ----------
def send_order_to_admin(order, chat_id):
    msg = (
        f"📬 *Новый заказ!*\n\n"
        f"💊 Лекарство: *{order['medicine']}*\n"
        f"🏙️ Город: *{order['city']}*\n"
        f"📦 Количество: *{order['quantity']}*\n"
        f"📞 Телефон: *{order['phone']}*\n"
        f"👤 ID клиента: `{chat_id}`"
    )
    bot.send_message(ADMIN_ID, msg, parse_mode="Markdown")

# ---------- Запуск ----------
bot.polling(none_stop=True)


# --- Держим бота живым (для Replit или хостинга) ---
from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "Бот работает!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

keep_alive()
