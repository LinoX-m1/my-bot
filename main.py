import telebot
import random
import time
import sqlite3
from flask import Flask
from threading import Thread

# --- SOZLAMALAR ---
# Telegramdan olgan tokenni shu yerga qo'ying
TOKEN = "BU_YERGA_TOKENNI_QO'YING"
bot = telebot.TeleBot(TOKEN)
app = Flask('')

# --- MA'LUMOTLAR BAZASI (SQLite) ---
def init_db():
    conn = sqlite3.connect('game.db', check_same_thread=False)
    cursor = conn.cursor()
    # Foydalanuvchilar jadvali
    cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                      (id INTEGER PRIMARY KEY, anime TEXT, cards TEXT, items INTEGER, last_get INTEGER, chances INTEGER)''')
    conn.commit()
    conn.close()

# --- ANIME KARTALARI (O'zingiz linklarni almashtiring) ---
CARDS_DATA = {
    "Naruto": [
        {"name": "Naruto Uzumaki", "star": 1, "img": "https://i.pinimg.com/564x/01/23/45/example1.jpg"},
        {"name": "Sasuke Uchiha", "star": 2, "img": "https://i.pinimg.com/564x/01/23/46/example2.jpg"},
        {"name": "Kakashi Hatake", "star": 3, "img": "https://i.pinimg.com/564x/01/23/47/example3.jpg"},
        {"name": "Itachi Uchiha", "star": 4, "img": "https://i.pinimg.com/564x/01/23/48/example4.jpg"},
        {"name": "Kurama Naruto (Mythical)", "star": 5, "img": "https://i.pinimg.com/564x/01/23/49/example5.jpg"}
    ],
    "One Piece": [
        {"name": "Luffy", "star": 1, "img": "https://i.pinimg.com/564x/01/23/50/example6.jpg"},
        {"name": "Zoro", "star": 2, "img": "https://i.pinimg.com/564x/01/23/51/example7.jpg"},
        {"name": "Nami", "star": 3, "img": "https://i.pinimg.com/564x/01/23/52/example8.jpg"},
        {"name": "Sanji", "star": 4, "img": "https://i.pinimg.com/564x/01/23/53/example9.jpg"},
        {"name": "Gear 5 Luffy (Mythical)", "star": 5, "img": "https://i.pinimg.com/564x/01/23/54/example10.jpg"}
    ]
}

def get_user(user_id):
    conn = sqlite3.connect('game.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id=?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user

# --- COMMANDS ---

@bot.message_handler(commands=['start'])
def start(message):
    user = get_user(message.from_user.id)
    if not user:
        conn = sqlite3.connect('game.db', check_same_thread=False)
        cursor = conn.cursor()
        # Boshida 10 ta bepul ochish imkoniyati beriladi
        cursor.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?)", 
                       (message.from_user.id, None, "", 0, 0, 10))
        conn.commit()
        conn.close()
        
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        for anime in CARDS_DATA.keys():
            markup.add(anime)
        bot.send_message(message.chat.id, "Xush kelibsiz! O'yinni boshlash uchun anime tanlang:", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "Xush kelibsiz! Buyruqlar:\n/get_card - Karta olish\n/my_cards - Kartalarim\n/menu - Craft qilish")

@bot.message_handler(func=lambda m: m.text in CARDS_DATA.keys())
def set_anime(message):
    conn = sqlite3.connect('game.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET anime=? WHERE id=?", (message.text, message.from_user.id))
    conn.commit()
    conn.close()
    bot.send_message(message.chat.id, f"Siz {message.text} animesini tanladingiz!\nEndi /get_card buyrug'ini ishlating.", reply_markup=telebot.types.ReplyKeyboardRemove())

@bot.message_handler(commands=['get_card'])
def get_card(message):
    user = get_user(message.from_user.id)
    if not user or not user[1]:
        return bot.send_message(message.chat.id, "Avval /start bosing va anime tanlang!")

    current_time = int(time.time())
    last_get = user[4]
    chances = user[5]

    # Har 3 soatda (10800 sekund) tekshirish, agar chances tugagan bo'lsa
    if chances <= 0:
        if current_time - last_get < 10800:
            vaqt_qoldi = (10800 - (current_time - last_get)) // 60
            return bot.send_message(message.chat.id, f"Charchadingiz! Yana {vaqt_qoldi} daqiqadan keyin karta olishingiz mumkin.")
        else:
            chances = 1 # 3 soat o'tdi, yangi imkoniyat

    # Karta darajasini aniqlash (Random)
    r = random.randint(1, 100)
    if r <= 5: star = 5
    elif r <= 15: star = 4
    elif r <= 35: star = 3
    elif r <= 60: star = 2
    else: star = 1

    anime_cards = [c for c in CARDS_DATA[user[1]] if c['star'] == star]
    if not anime_cards: anime_cards = CARDS_DATA[user[1]]
    
    card = random.choice(anime_cards)
    
    conn = sqlite3.connect('game.db', check_same_thread=False)
    cursor = conn.cursor()
    
    new_items = user[3]
    card_msg = f"Sizga tushdi: {card['name']}\nDarajasi: {'⭐' * star}"
    
    # Agar karta avval bor bo'lsa, predmet berish
    if card['name'] in user[2]:
        p_berildi = star + 1
        new_items += p_berildi
        card_msg += f"\n\n(Bu karta sizda bor! {p_berildi} ta predmet berildi 💎)"
    
    new_cards = user[2] + f"{card['name']},"
    cursor.execute("UPDATE users SET cards=?, items=?, last_get=?, chances=? WHERE id=?", 
                   (new_cards, new_items, current_time, max(0, chances - 1), message.from_user.id))
    conn.commit()
    conn.close()

    try:
        bot.send_photo(message.chat.id, card['img'], caption=card_msg)
    except:
        bot.send_message(message.chat.id, card_msg + "\n(Rasm havolasi xato!)")

@bot.message_handler(commands=['my_cards'])
def my_cards(message):
    user = get_user(message.from_user.id)
    if user and user[2]:
        bot.send_message(message.chat.id, f"Sizning kartalaringiz (Inventar):\n{user[2].replace(',', ', ')}\n\nPredmetlar: {user[3]} ta 💎")
    else:
        bot.send_message(message.chat.id, "Sizda hali kartalar yo'q.")

@bot.message_handler(commands=['menu'])
def menu(message):
    user = get_user(message.from_user.id)
    if not user: return
    text = f"🛠 **Craft menyusi**\n\nSizdagi predmetlar: {user[3]} ta 💎\n\n10 ta predmet evaziga 1 ta qo'shimcha /get_card imkoniyatini olishingiz mumkin.\n\nCraft qilish uchun /craft buyrug'ini yuboring."
    bot.send_message(message.chat.id, text, parse_mode="Markdown")

@bot.message_handler(commands=['craft'])
def craft(message):
    user = get_user(message.from_user.id)
    if user[3] >= 10:
        conn = sqlite3.connect('game.db', check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET items=items-10, chances=chances+1 WHERE id=?", (message.from_user.id,))
        conn.commit()
        conn.close()
        bot.send_message(message.chat.id, "Muvaffaqiyatli! 10 predmetga +1 imkoniyat oldingiz. /get_card deb yozing!")
    else:
        bot.send_message(message.chat.id, f"Predmetlar yetarli emas! Sizda {user[3]} ta bor, 10 ta kerak.")

# --- SERVER QISMI ---
@app.route('/')
def home(): return "Bot ishlayapti!"
def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive(): Thread(target=run).start()

init_db()
keep_alive()
bot.infinity_polling()
