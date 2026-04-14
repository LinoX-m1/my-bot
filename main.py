import telebot
import random
import sqlite3
from flask import Flask
from threading import Thread

TOKEN = "8770000703:AAEXRnIxr8iRBu_eUP9f3GPi8yBID6oTEmw"
ADMIN_ID = 123456789

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# --- DATABASE ---
def init_db():
    conn = sqlite3.connect('game.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            cards TEXT,
            items INTEGER,
            chances INTEGER
        )
    ''')
    conn.commit()
    conn.close()

def get_user(user_id):
    conn = sqlite3.connect('game.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id=?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user

# --- DEMON SLAYER (45 ta) ---
CARDS = [
# ⭐ (1⭐) — Oddiylar (10 ta)
("Tanjiro Kamado",1),
("Nezuko Kamado",1),
("Zenitsu Agatsuma",1),
("Inosuke Hashibira",1),
("Kanao Tsuyuri",1),
("Aoi Kanzaki",1),
("Murata",1),
("Sabito",1),
("Makomo",1),
("Genya Shinazugawa",1),

# ⭐⭐ (2⭐) — O‘rta (10 ta)
("Rui",2),
("Enmu",2),
("Tamayo",2),
("Yushiro",2),
("Hand Demon",2),
("Spider Father",2),
("Spider Mother",2),
("Spider Brother",2),
("Susamaru",2),
("Yahaba",2),

# ⭐⭐⭐ (3⭐) — Kuchli (10 ta)
("Shinobu Kocho",3),
("Mitsuri Kanroji",3),
("Obanai Iguro",3),
("Muichiro Tokito",3),
("Tengen Uzui",3),
("Kyojuro Rengoku",3),
("Giyu Tomioka",3),
("Daki",3),
("Gyutaro",3),
("Gyokko",3),

# ⭐⭐⭐⭐ (4⭐) — Juda kuchli (8 ta)
("Sanemi Shinazugawa",4),
("Gyomei Himejima",4),
("Hantengu",4),
("Akaza",4),
("Doma",4),
("Nakime",4),
("Kaigaku",4),
("Kagaya Ubuyashiki",4),

# ⭐⭐⭐⭐⭐ (5⭐) — Eng kuchli (7 ta)
("Muzan Kibutsuji",5),
("Kokushibo",5),
("Yoriichi Tsugikuni",5),
("Upper Moon 1 Kokushibo",5),
("Upper Moon 2 Doma",5),
("Upper Moon 3 Akaza",5),
("Upper Moon 4 Hantengu",5)
]

# --- DROP CHANCE ---
def get_star():
    r = random.randint(1,100)
    if r <= 5:
        return 5
    elif r <= 15:
        return 4
    elif r <= 35:
        return 3
    elif r <= 60:
        return 2
    else:
        return 1

# --- MENU ---
def menu():
    m = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    m.add("🎴 Karta olish", "🎒 Kartalarim")
    return m

# --- START ---
@bot.message_handler(commands=['start'])
def start(msg):
    user = get_user(msg.from_user.id)

    if not user:
        conn = sqlite3.connect('game.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users VALUES (?, ?, ?, ?)",
                       (msg.from_user.id, "", 0, 5))
        conn.commit()
        conn.close()

        bot.send_message(ADMIN_ID, f"🆕 USER: {msg.from_user.id}")

    bot.send_message(msg.chat.id, "Xush kelibsiz!", reply_markup=menu())

# --- CARD ---
@bot.message_handler(func=lambda m: m.text == "🎴 Karta olish")
def get_card(msg):
    user = get_user(msg.from_user.id)

    if user[3] <= 0:
        return bot.send_message(msg.chat.id, "❌ Chance yo'q!")

    star = get_star()
    possible = [c for c in CARDS if c[1] == star]

    if not possible:
        possible = CARDS

    card = random.choice(possible)

    cards_list = user[1].split(',') if user[1] else []
    items = user[2]

    if card[0] in cards_list:
        items += star

    cards_list.append(card[0])

    conn = sqlite3.connect('game.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET cards=?, items=?, chances=chances-1 WHERE id=?",
                   (",".join(cards_list), items, msg.from_user.id))
    conn.commit()
    conn.close()

    bot.send_message(msg.chat.id, f"🎉 {card[0]} ({star}⭐)\n💎 {items}")

# --- MY CARDS ---
@bot.message_handler(func=lambda m: m.text == "🎒 Kartalarim")
def my_cards(msg):
    user = get_user(msg.from_user.id)
    if user and user[1]:
        bot.send_message(msg.chat.id, user[1])
    else:
        bot.send_message(msg.chat.id, "Bo'sh")

# --- SERVER ---
@app.route('/')
def home():
    return "Bot ishlayapti"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    Thread(target=run).start()

# --- RUN ---
if __name__ == "__main__":
    init_db()
    keep_alive()
    bot.infinity_polling()
