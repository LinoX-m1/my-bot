import telebot
import random
import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("8770000703:AAEXRnIxr8iRBu_eUP9f3GPi8yBID6oTEmw")
bot = telebot.TeleBot(TOKEN)

# --- DATABASE ---
def init_db():
    conn = sqlite3.connect("game.db")
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY,
            cards TEXT,
            items INTEGER,
            chances INTEGER
        )
    """)
    conn.commit()
    conn.close()

def get_user(user_id):
    conn = sqlite3.connect("game.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE id=?", (user_id,))
    user = cur.fetchone()
    conn.close()
    return user

def create_user(user_id):
    conn = sqlite3.connect("game.db")
    cur = conn.cursor()
    cur.execute("INSERT INTO users VALUES (?, ?, ?, ?)",
                (user_id, "", 0, 5))
    conn.commit()
    conn.close()

def update_user(user_id, cards, items, chances):
    conn = sqlite3.connect("game.db")
    cur = conn.cursor()
    cur.execute("UPDATE users SET cards=?, items=?, chances=? WHERE id=?",
                (cards, items, chances, user_id))
    conn.commit()
    conn.close()

# --- 45 TA DEMON SLAYER ---
CARDS = [
# ⭐1 (10 ta)
("Tanjiro Kamado",1),
("Nezuko Kamado",1),
("Zenitsu Agatsuma",1),
("Inosuke Hashibira",1),
("Kanao Tsuyuri",1),
("Aoi Kanzaki",1),
("Genya Shinazugawa",1),
("Sabito",1),
("Makomo",1),
("Murata",1),

# ⭐2 (10 ta)
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

# ⭐3 (10 ta)
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

# ⭐4 (8 ta)
("Sanemi Shinazugawa",4),
("Gyomei Himejima",4),
("Hantengu",4),
("Akaza",4),
("Doma",4),
("Nakime",4),
("Kaigaku",4),
("Kagaya Ubuyashiki",4),

# ⭐5 (7 ta)
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
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🎴 Karta olish", "🎒 Kartalarim")
    return markup

# --- START ---
@bot.message_handler(commands=['start'])
def start(msg):
    if not get_user(msg.from_user.id):
        create_user(msg.from_user.id)

    bot.send_message(msg.chat.id, "Xush kelibsiz!", reply_markup=menu())

# --- KARTA OLISH ---
@bot.message_handler(func=lambda m: m.text == "🎴 Karta olish")
def get_card(msg):
    user = get_user(msg.from_user.id)

    if user[3] <= 0:
        bot.send_message(msg.chat.id, "❌ Chance tugadi!")
        return

    star = get_star()
    possible = [c for c in CARDS if c[1] == star]

    card = random.choice(possible)

    cards_list = user[1].split(",") if user[1] else []
    items = user[2]

    if card[0] in cards_list:
        items += star
    else:
        cards_list.append(card[0])

    # Update database with new chances value
    new_chances = user[3] - 1
    update_user(msg.from_user.id, ",".join(cards_list), items, new_chances)

    bot.send_message(
        msg.chat.id,
        f"🎉 {card[0]} ({star}⭐)\n💎 {items}\n🎯 Qolgan chance: {new_chances}"
    )

# --- KARTALARIM ---
@bot.message_handler(func=lambda m: m.text == "🎒 Kartalarim")
def my_cards(msg):
    user = get_user(msg.from_user.id)

    if user[1]:
        cards = user[1].split(",")

        text = "🎒 Sening kartalaring:\n\n"
        for c in cards:
            text += f"• {c}\n"

        bot.send_message(msg.chat.id, text)
    else:
        bot.send_message(msg.chat.id, "Bo'sh")

# --- RUN ---
if __name__ == "__main__":
    init_db()
    bot.infinity_polling()
