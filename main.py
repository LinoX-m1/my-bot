import telebot
import random
import time
import sqlite3
from flask import Flask
from threading import Thread

# --- SOZLAMALAR ---
TOKEN = "BU_YERGA_TOKENNI_QO'YING"
bot = telebot.TeleBot(TOKEN)
app = Flask('')

# --- MA'LUMOTLAR BAZASI (SQLite) ---
def init_db():
    conn = sqlite3.connect('game.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                      (id INTEGER PRIMARY KEY, anime TEXT, cards TEXT, items INTEGER, last_get INTEGER, chances INTEGER)''')
    conn.commit()
    conn.close()

# --- ANIME KARTALARI ---
# Bu yerga o'zingiz xohlagan rasm va ismlarni kiriting
CARDS_DATA = {
    "Naruto": [
        {"name": "Naruto Genin", "star": 1, "img": "https://bit.ly/3xX1"},
        {"name": "Kakashi", "star": 3, "img": "https://bit.ly/3xX2"},
        {"name": "Kurama Naruto", "star": 5, "img": "https://bit.ly/3xX3"}
    ],
    "One Piece": [
        {"name": "Luffy", "star": 1, "img": "https://bit.ly/4yY1"},
        {"name": "Zoro", "star": 3, "img": "https://bit.ly/4yY2"},
        {"name": "Gear 5 Luffy", "star": 5, "img": "https://bit.ly/4yY3"}
    ]
}

# --- FUNKSIYALAR ---
def get_user(user_id):
    conn = sqlite3.connect('game.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id=?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user

@bot.message_handler(commands=['start'])
def start(message):
    user = get_user(message.from_user.id)
    if not user:
        conn = sqlite3.connect('game.db')
        cursor = conn.cursor()
        # Boshlanishiga 10 ta imkoniyat (chances) beramiz
        cursor.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?)", 
                       (message.from_user.id, None, "", 0, 0, 10))
        conn.commit()
        conn.close()
        
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        for anime in CARDS_DATA.keys():
            markup.add(anime)
        bot.send_message(message.chat.id, "Xush kelibsiz! Anime tanlang:", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "Siz allaqachon ro'yxatdan o'tgansiz!")

@bot.message_handler(func=lambda m: m.text in CARDS_DATA.keys())
def set_anime(message):
    conn = sqlite3.connect('game.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET anime=? WHERE id=?", (message.text, message.from_user.id))
    conn.commit()
    conn.close()
    bot.send_message(message.chat.id, f"Siz {message.text} animesini tanladingiz!\nEndi /get_card buyrug'ini ishlating.", reply_markup=telebot.types.ReplyKeyboardRemove())

@bot.message_handler(commands=['get_card'])
def get_card(message):
    user = get_user(message.from_user.id)
    if not user or not user[1]:
        return bot.send_message(message.chat.id, "Avval anime tanlang!")

    current_time = int(time.time())
    last_get = user[4]
    chances = user[5]

    # Har 3 soatda (10800 sekund) tekshirish
    if chances <= 0 and current_time - last_get < 10800:
        qolgan_vaqt = (10800 - (current_time - last_get)) // 60
        return bot.send_message(message.chat.id, f"Kutishingiz kerak: {qolgan_vaqt} daqiqa")

    # Karta tanlash (Random)
    shans = random.randint(1, 100)
    if shans <= 5: star = 5  # 5% imkoniyat
    elif shans <= 15: star = 4
    elif shans <= 35: star = 3
    elif shans <= 65: star = 2
    else: star = 1

    anime_cards = [c for c in CARDS_DATA[user[1]] if c['star'] == star]
    if not anime_cards: # Agar o'sha yulduzli karta bo'lmasa, borini berish
        anime_cards = CARDS_DATA[user[1]]
    
    card = random.choice(anime_cards)
    
    # Bazani yangilash
    conn = sqlite3.connect('game.db')
    cursor = conn.cursor()
    
    new_cards = user[2] + f"{card['name']},"
    new_items = user[3]
    
    # Agar karta avval bor bo'lsa, predmet berish
    if card['name'] in user[2]:
        predmet_soni = star + 1 # 1 yulduzli bo'lsa 2 ta, 5 bo'lsa 6 ta predmet
        new_items += predmet_soni
        bot.send_message(message.chat.id, f"Sizda bu karta bor edi! {predmet_soni} predmet berildi.")
    
    new_chances = max(0, chances - 1)
    cursor.execute("UPDATE users SET cards=?, items=?, last_get=?, chances=? WHERE id=?", 
                   (new_cards, new_items, current_time, new_chances, message.from_user.id))
    conn.commit()
    conn.close()

    bot.send_photo(message.chat.id, card['img'], caption=f"Sizga tushdi: {card['name']}\nDarajasi: {'⭐' * star}")

@bot.message_handler(commands=['my_cards'])
def my_cards(message):
    user = get_user(message.from_user.id)
    if user and user[2]:
        bot.send_message(message.chat.id, f"Sizning kartalaringiz: \n{user[2]}")
    else:
        bot.send_message(message.chat.id, "Sizda hali kartalar yo'q.")

# Flask va Botni yurgizish qismi (oldingidek)
@app.route('/')
def home(): return "OK"
def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive(): Thread(target=run).start()

init_db()
keep_alive()
bot.infinity_polling()
