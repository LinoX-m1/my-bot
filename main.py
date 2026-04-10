import telebot
import random
import time
import sqlite3
from flask import Flask
from threading import Thread

# --- SOZLAMALAR ---
TOKEN = "8770000703:AAEXRnIxr8iRBu_eUP9f3GPi8yBID6oTEmw" # O'z tokeningizni qo'ying!
bot = telebot.TeleBot(TOKEN)
app = Flask('')

# --- MA'LUMOTLAR BAZASI ---
def init_db():
    conn = sqlite3.connect('game.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                      (id INTEGER PRIMARY KEY, anime TEXT, cards TEXT, items INTEGER, last_get INTEGER, chances INTEGER)''')
    conn.commit()
    conn.close()

# --- MAXIMAL PERSONAJLAR RO'YXATI (60+) ---
CARDS_DATA = {
    "Naruto": [
        {"name": "Naruto Uzumaki", "star": 1, "img": "https://i.pinimg.com/564x/01/23/45/naruto.jpg"},
        {"name": "Sakura Haruno", "star": 1, "img": "https://i.pinimg.com/564x/01/23/45/sakura.jpg"},
        {"name": "Hinata Hyuga", "star": 1, "img": "https://i.pinimg.com/564x/01/23/45/hinata.jpg"},
        {"name": "Rock Lee", "star": 2, "img": "https://i.pinimg.com/564x/01/23/45/lee.jpg"},
        {"name": "Shikamaru Nara", "star": 2, "img": "https://i.pinimg.com/564x/01/23/45/shika.jpg"},
        {"name": "Neji Hyuga", "star": 2, "img": "https://i.pinimg.com/564x/01/23/45/neji.jpg"},
        {"name": "Kakashi Hatake", "star": 3, "img": "https://i.pinimg.com/564x/01/23/45/kakashi.jpg"},
        {"name": "Might Guy", "star": 3, "img": "https://i.pinimg.com/564x/01/23/45/guy.jpg"},
        {"name": "Jiraiya", "star": 3, "img": "https://i.pinimg.com/564x/01/23/45/jiraiya.jpg"},
        {"name": "Itachi Uchiha", "star": 4, "img": "https://i.pinimg.com/564x/01/23/45/itachi.jpg"},
        {"name": "Minato Namikaze", "star": 4, "img": "https://i.pinimg.com/564x/01/23/45/minato.jpg"},
        {"name": "Pain (Nagato)", "star": 4, "img": "https://i.pinimg.com/564x/01/23/45/pain.jpg"},
        {"name": "Madara Uchiha", "star": 5, "img": "https://i.pinimg.com/564x/01/23/45/madara.jpg"},
        {"name": "Kurama Mode Naruto", "star": 5, "img": "https://i.pinimg.com/564x/01/23/45/k_naruto.jpg"},
        {"name": "Sasuke Rinnegan", "star": 5, "img": "https://i.pinimg.com/564x/01/23/45/s_rinne.jpg"}
    ],
    "One Piece": [
        {"name": "Luffy", "star": 1, "img": "https://i.pinimg.com/564x/01/23/45/luffy.jpg"},
        {"name": "Usopp", "star": 1, "img": "https://i.pinimg.com/564x/01/23/45/usopp.jpg"},
        {"name": "Nami", "star": 1, "img": "https://i.pinimg.com/564x/01/23/45/nami.jpg"},
        {"name": "Roronoa Zoro", "star": 2, "img": "https://i.pinimg.com/564x/01/23/45/zoro.jpg"},
        {"name": "Sanji", "star": 2, "img": "https://i.pinimg.com/564x/01/23/45/sanji.jpg"},
        {"name": "Tony Tony Chopper", "star": 2, "img": "https://i.pinimg.com/564x/01/23/45/chopper.jpg"},
        {"name": "Brook", "star": 3, "img": "https://i.pinimg.com/564x/01/23/45/brook.jpg"},
        {"name": "Nico Robin", "star": 3, "img": "https://i.pinimg.com/564x/01/23/45/robin.jpg"},
        {"name": "Franky", "star": 3, "img": "https://i.pinimg.com/564x/01/23/45/franky.jpg"},
        {"name": "Ace", "star": 4, "img": "https://i.pinimg.com/564x/01/23/45/ace.jpg"},
        {"name": "Sabo", "star": 4, "img": "https://i.pinimg.com/564x/01/23/45/sabo.jpg"},
        {"name": "Trafalgar Law", "star": 4, "img": "https://i.pinimg.com/564x/01/23/45/law.jpg"},
        {"name": "Gear 5 Luffy", "star": 5, "img": "https://i.pinimg.com/564x/01/23/45/g5.jpg"},
        {"name": "Shanks", "star": 5, "img": "https://i.pinimg.com/564x/01/23/45/shanks.jpg"},
        {"name": "Whitebeard", "star": 5, "img": "https://i.pinimg.com/564x/01/23/45/wb.jpg"}
    ],
    "Attack on Titan": [
        {"name": "Eren Yeager", "star": 1, "img": "https://i.pinimg.com/564x/01/23/45/eren.jpg"},
        {"name": "Sasha", "star": 1, "img": "https://i.pinimg.com/564x/01/23/45/sasha.jpg"},
        {"name": "Connie", "star": 1, "img": "https://i.pinimg.com/564x/01/23/45/connie.jpg"},
        {"name": "Mikasa Ackerman", "star": 2, "img": "https://i.pinimg.com/564x/01/23/45/mikasa.jpg"},
        {"name": "Armin Arlert", "star": 2, "img": "https://i.pinimg.com/564x/01/23/45/armin.jpg"},
        {"name": "Jean", "star": 2, "img": "https://i.pinimg.com/564x/01/23/45/jean.jpg"},
        {"name": "Levi Ackerman", "star": 3, "img": "https://i.pinimg.com/564x/01/23/45/levi.jpg"},
        {"name": "Erwin Smith", "star": 3, "img": "https://i.pinimg.com/564x/01/23/45/erwin.jpg"},
        {"name": "Hange Zoe", "star": 3, "img": "https://i.pinimg.com/564x/01/23/45/hange.jpg"},
        {"name": "Reiner (Armored Titan)", "star": 4, "img": "https://i.pinimg.com/564x/01/23/45/reiner.jpg"},
        {"name": "Bertholdt (Colossal)", "star": 4, "img": "https://i.pinimg.com/564x/01/23/45/berth.jpg"},
        {"name": "Zeke (Beast Titan)", "star": 4, "img": "https://i.pinimg.com/564x/01/23/45/zeke.jpg"},
        {"name": "Eren Founding Titan", "star": 5, "img": "https://i.pinimg.com/564x/01/23/45/eren5.jpg"},
        {"name": "Ymir Fritz", "star": 5, "img": "https://i.pinimg.com/564x/01/23/45/ymir.jpg"}
    ],
    "Dragon Ball": [
        {"name": "Goku", "star": 1, "img": "https://i.pinimg.com/564x/01/23/45/goku.jpg"},
        {"name": "Krillin", "star": 1, "img": "https://i.pinimg.com/564x/01/23/45/krillin.jpg"},
        {"name": "Yamcha", "star": 1, "img": "https://i.pinimg.com/564x/01/23/45/yamcha.jpg"},
        {"name": "Vegeta", "star": 2, "img": "https://i.pinimg.com/564x/01/23/45/vegeta.jpg"},
        {"name": "Gohan", "star": 2, "img": "https://i.pinimg.com/564x/01/23/45/gohan.jpg"},
        {"name": "Piccolo", "star": 2, "img": "https://i.pinimg.com/564x/01/23/45/piccolo.jpg"},
        {"name": "Future Trunks", "star": 3, "img": "https://i.pinimg.com/564x/01/23/45/trunks.jpg"},
        {"name": "Frieza", "star": 3, "img": "https://i.pinimg.com/564x/01/23/45/frieza.jpg"},
        {"name": "Cell", "star": 3, "img": "https://i.pinimg.com/564x/01/23/45/cell.jpg"},
        {"name": "Goku Black", "star": 4, "img": "https://i.pinimg.com/564x/01/23/45/gblack.jpg"},
        {"name": "Hit", "star": 4, "img": "https://i.pinimg.com/564x/01/23/45/hit.jpg"},
        {"name": "Beerus", "star": 4, "img": "https://i.pinimg.com/564x/01/23/45/beerus.jpg"},
        {"name": "UI Goku", "star": 5, "img": "https://i.pinimg.com/564x/01/23/45/uigoku.jpg"},
        {"name": "Zeno", "star": 5, "img": "https://i.pinimg.com/564x/01/23/45/zeno.jpg"},
        {"name": "Broly (Super)", "star": 5, "img": "https://i.pinimg.com/564x/01/23/45/broly.jpg"}
    ]
}

def get_user(user_id):
    conn = sqlite3.connect('game.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id=?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user

# --- TUGMALAR ---
def main_markup():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🎴 Karta olish", "🎒 Kartalarim")
    markup.add("🛠 Menyusi", "🔄 Anime almashtirish")
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    user = get_user(message.from_user.id)
    if not user:
        conn = sqlite3.connect('game.db', check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?)", (message.from_user.id, None, "", 0, 0, 10))
        conn.commit()
        conn.close()
        send_anime_choice(message)
    else:
        bot.send_message(message.chat.id, "Bosh menyu:", reply_markup=main_markup())

def send_anime_choice(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for anime in CARDS_DATA.keys():
        markup.add(anime)
    bot.send_message(message.chat.id, "Anime tanlang:", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text in CARDS_DATA.keys())
def set_anime(message):
    conn = sqlite3.connect('game.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET anime=? WHERE id=?", (message.text, message.from_user.id))
    conn.commit()
    conn.close()
    bot.send_message(message.chat.id, f"Siz {message.text} ni tanladingiz!", reply_markup=main_markup())

@bot.message_handler(func=lambda m: m.text == "🎴 Karta olish")
def get_card(message):
    user = get_user(message.from_user.id)
    if not user or not user[1]: return send_anime_choice(message)

    current_time = int(time.time())
    if user[5] <= 0 and current_time - user[4] < 10800:
        mins = (10800 - (current_time - user[4])) // 60
        return bot.send_message(message.chat.id, f"⌛ Kutish kerak: {mins} daqiqa.")

    r = random.randint(1, 100)
    star = 5 if r <= 5 else 4 if r <= 15 else 3 if r <= 35 else 2 if r <= 65 else 1
    
    anime_cards = [c for c in CARDS_DATA[user[1]] if c['star'] == star]
    if not anime_cards: anime_cards = CARDS_DATA[user[1]]
    
    card = random.choice(anime_cards)
    conn = sqlite3.connect('game.db', check_same_thread=False)
    cursor = conn.cursor()
    
    new_items = user[3]
    caption = f"✨ **YANGI KARTA!**\n\n👤 Ism: {card['name']}\n⭐ Daraja: {star}\n💎 Sizda bor: {new_items}"
    
    if card['name'] in user[2]:
        p = star + 1
        new_items += p
        caption += f"\n\n♻️ Dublikat! +{p} ta predmet berildi."
    
    new_cards = user[2] + f"{card['name']},"
    new_chances = user[5] - 1 if user[5] > 0 else 0
    
    cursor.execute("UPDATE users SET cards=?, items=?, last_get=?, chances=? WHERE id=?", 
                   (new_cards, new_items, current_time, new_chances, message.from_user.id))
    conn.commit()
    conn.close()

    try:
        bot.send_photo(message.chat.id, card['img'], caption=caption, parse_mode="Markdown")
    except:
        bot.send_message(message.chat.id, caption)

@bot.message_handler(func=lambda m: m.text == "🎒 Kartalarim")
def my_cards(message):
    user = get_user(message.from_user.id)
    if user and user[2]:
        bot.send_message(message.chat.id, f"Sizning kartalaringiz:\n{user[2].rstrip(',')}")
    else: bot.send_message(message.chat.id, "Sizda hali karta yo'q.")

@bot.message_handler(func=lambda m: m.text == "🛠 Menyusi")
def menu(message):
    user = get_user(message.from_user.id)
    text = f"⚙️ **STATISTIKA**\n\n💎 Predmetlar: {user[3]}\n🎟 Imkoniyatlar: {user[5]}\n\n10 💎 evaziga 🎟 olish uchun /craft deb yozing."
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
        bot.send_message(message.chat.id, "✅ Tayyor! 1 ta imkoniyat qo'shildi.")
    else: bot.send_message(message.chat.id, "❌ Predmet yetarli emas.")

@bot.message_handler(func=lambda m: m.text == "🔄 Anime almashtirish")
def change_anime(message): send_anime_choice(message)

@app.route('/')
def home(): return "Bot Live"
def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive(): Thread(target=run).start()

if __name__ == "__main__":
    init_db()
    keep_alive()
    bot.infinity_polling()
