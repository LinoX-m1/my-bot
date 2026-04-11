import telebot
import random
import time
import sqlite3
from flask import Flask
from threading import Thread

# --- SOZLAMALAR ---
TOKEN = "8770000703:AAEXRnIxr8iRBu_eUP9f3GPi8yBID6oTEmw"
ADMIN_ID = 7818670765

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# --- DATABASE ---
def init_db():
    conn = sqlite3.connect('game.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            anime TEXT,
            cards TEXT,
            items INTEGER,
            last_get INTEGER,
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

# --- DATA (30+) ---
CARDS_DATA = {
    "Naruto": [
        {"name":"Naruto","star":1,"img":"https://picsum.photos/200?1"},
        {"name":"Sakura","star":1,"img":"https://picsum.photos/200?2"},
        {"name":"Hinata","star":1,"img":"https://picsum.photos/200?3"},
        {"name":"Kiba","star":1,"img":"https://picsum.photos/200?4"},
        {"name":"Shino","star":1,"img":"https://picsum.photos/200?5"},

        {"name":"Rock Lee","star":2,"img":"https://picsum.photos/200?6"},
        {"name":"Neji","star":2,"img":"https://picsum.photos/200?7"},
        {"name":"Shikamaru","star":2,"img":"https://picsum.photos/200?8"},
        {"name":"Choji","star":2,"img":"https://picsum.photos/200?9"},
        {"name":"Ino","star":2,"img":"https://picsum.photos/200?10"},

        {"name":"Kakashi","star":3,"img":"https://picsum.photos/200?11"},
        {"name":"Guy","star":3,"img":"https://picsum.photos/200?12"},
        {"name":"Asuma","star":3,"img":"https://picsum.photos/200?13"},
        {"name":"Kurenai","star":3,"img":"https://picsum.photos/200?14"},
        {"name":"Yamato","star":3,"img":"https://picsum.photos/200?15"},

        {"name":"Itachi","star":4,"img":"https://picsum.photos/200?16"},
        {"name":"Pain","star":4,"img":"https://picsum.photos/200?17"},
        {"name":"Konan","star":4,"img":"https://picsum.photos/200?18"},
        {"name":"Deidara","star":4,"img":"https://picsum.photos/200?19"},
        {"name":"Sasori","star":4,"img":"https://picsum.photos/200?20"},

        {"name":"Madara","star":5,"img":"https://picsum.photos/200?21"},
        {"name":"Hashirama","star":5,"img":"https://picsum.photos/200?22"},
        {"name":"Minato","star":5,"img":"https://picsum.photos/200?23"},
        {"name":"Obito","star":5,"img":"https://picsum.photos/200?24"},
        {"name":"Six Naruto","star":5,"img":"https://picsum.photos/200?25"},

        {"name":"Sasuke Rinnegan","star":5,"img":"https://picsum.photos/200?26"},
        {"name":"Kaguya","star":5,"img":"https://picsum.photos/200?27"},
        {"name":"Jiraiya","star":4,"img":"https://picsum.photos/200?28"},
        {"name":"Tsunade","star":4,"img":"https://picsum.photos/200?29"},
        {"name":"Orochimaru","star":4,"img":"https://picsum.photos/200?30"},
    ],

    "One Piece": [
        {"name":"Luffy","star":1,"img":"https://picsum.photos/200?a1"},
        {"name":"Usopp","star":1,"img":"https://picsum.photos/200?a2"},
        {"name":"Nami","star":1,"img":"https://picsum.photos/200?a3"},
        {"name":"Chopper","star":1,"img":"https://picsum.photos/200?a4"},
        {"name":"Brook","star":1,"img":"https://picsum.photos/200?a5"},

        {"name":"Zoro","star":2,"img":"https://picsum.photos/200?a6"},
        {"name":"Sanji","star":2,"img":"https://picsum.photos/200?a7"},
        {"name":"Robin","star":2,"img":"https://picsum.photos/200?a8"},
        {"name":"Franky","star":2,"img":"https://picsum.photos/200?a9"},
        {"name":"Jinbe","star":2,"img":"https://picsum.photos/200?a10"},

        {"name":"Ace","star":3,"img":"https://picsum.photos/200?a11"},
        {"name":"Sabo","star":3,"img":"https://picsum.photos/200?a12"},
        {"name":"Law","star":3,"img":"https://picsum.photos/200?a13"},
        {"name":"Kid","star":3,"img":"https://picsum.photos/200?a14"},
        {"name":"Smoker","star":3,"img":"https://picsum.photos/200?a15"},

        {"name":"Doflamingo","star":4,"img":"https://picsum.photos/200?a16"},
        {"name":"Katakuri","star":4,"img":"https://picsum.photos/200?a17"},
        {"name":"Big Mom","star":4,"img":"https://picsum.photos/200?a18"},
        {"name":"Kaido","star":4,"img":"https://picsum.photos/200?a19"},
        {"name":"Blackbeard","star":4,"img":"https://picsum.photos/200?a20"},

        {"name":"Gear 5 Luffy","star":5,"img":"https://picsum.photos/200?a21"},
        {"name":"Shanks","star":5,"img":"https://picsum.photos/200?a22"},
        {"name":"Roger","star":5,"img":"https://picsum.photos/200?a23"},
        {"name":"Whitebeard","star":5,"img":"https://picsum.photos/200?a24"},
        {"name":"Rayleigh","star":5,"img":"https://picsum.photos/200?a25"},

        {"name":"Garp","star":4,"img":"https://picsum.photos/200?a26"},
        {"name":"Fujitora","star":4,"img":"https://picsum.photos/200?a27"},
        {"name":"Kizaru","star":4,"img":"https://picsum.photos/200?a28"},
        {"name":"Aokiji","star":4,"img":"https://picsum.photos/200?a29"},
        {"name":"Enel","star":4,"img":"https://picsum.photos/200?a30"},
    ],
  
    "Dragon Ball": [
    {"name":"Goku","star":1,"img":"https://picsum.photos/200?db1"},
    {"name":"Krillin","star":1,"img":"https://picsum.photos/200?db2"},
    {"name":"Yamcha","star":1,"img":"https://picsum.photos/200?db3"},
    {"name":"Tien","star":1,"img":"https://picsum.photos/200?db4"},

    {"name":"Vegeta","star":2,"img":"https://picsum.photos/200?db5"},
    {"name":"Gohan","star":2,"img":"https://picsum.photos/200?db6"},
    {"name":"Piccolo","star":2,"img":"https://picsum.photos/200?db7"},
    {"name":"Trunks","star":2,"img":"https://picsum.photos/200?db8"},

    {"name":"Frieza","star":3,"img":"https://picsum.photos/200?db9"},
    {"name":"Cell","star":3,"img":"https://picsum.photos/200?db10"},
    {"name":"Majin Buu","star":3,"img":"https://picsum.photos/200?db11"},
    {"name":"Android 17","star":3,"img":"https://picsum.photos/200?db12"},

    {"name":"Beerus","star":4,"img":"https://picsum.photos/200?db13"},
    {"name":"Whis","star":4,"img":"https://picsum.photos/200?db14"},
    {"name":"Hit","star":4,"img":"https://picsum.photos/200?db15"},
    {"name":"Goku Black","star":4,"img":"https://picsum.photos/200?db16"},

    {"name":"UI Goku","star":5,"img":"https://picsum.photos/200?db17"},
    {"name":"Jiren","star":5,"img":"https://picsum.photos/200?db18"},
    {"name":"Zeno","star":5,"img":"https://picsum.photos/200?db19"},
    {"name":"Broly","star":5,"img":"https://picsum.photos/200?db20"},
],

  "Attack on Titan": [
    {"name":"Eren","star":1,"img":"https://picsum.photos/200?aot1"},
    {"name":"Armin","star":1,"img":"https://picsum.photos/200?aot2"},
    {"name":"Sasha","star":1,"img":"https://picsum.photos/200?aot3"},
    {"name":"Connie","star":1,"img":"https://picsum.photos/200?aot4"},

    {"name":"Mikasa","star":2,"img":"https://picsum.photos/200?aot5"},
    {"name":"Jean","star":2,"img":"https://picsum.photos/200?aot6"},
    {"name":"Historia","star":2,"img":"https://picsum.photos/200?aot7"},
    {"name":"Reiner","star":2,"img":"https://picsum.photos/200?aot8"},

    {"name":"Bertholdt","star":3,"img":"https://picsum.photos/200?aot9"},
    {"name":"Annie","star":3,"img":"https://picsum.photos/200?aot10"},
    {"name":"Ymir","star":3,"img":"https://picsum.photos/200?aot11"},
    {"name":"Hange","star":3,"img":"https://picsum.photos/200?aot12"},

    {"name":"Levi","star":4,"img":"https://picsum.photos/200?aot13"},
    {"name":"Erwin","star":4,"img":"https://picsum.photos/200?aot14"},
    {"name":"Zeke","star":4,"img":"https://picsum.photos/200?aot15"},
    {"name":"Pieck","star":4,"img":"https://picsum.photos/200?aot16"},

    {"name":"Eren Titan","star":5,"img":"https://picsum.photos/200?aot17"},
    {"name":"Founder Eren","star":5,"img":"https://picsum.photos/200?aot18"},
    {"name":"Warhammer Titan","star":5,"img":"https://picsum.photos/200?aot19"},
    {"name":"Colossal Titan","star":5,"img":"https://picsum.photos/200?aot20"},
]
}

# --- MENU ---
def menu():
    m = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    m.add("🎴 Karta olish", "🎒 Kartalarim")
    m.add("🛠 Menu", "🔄 Anime almashtirish")
    return m

# --- START ---
@bot.message_handler(commands=['start'])
def start(msg):
    user = get_user(msg.from_user.id)

    if not user:
        conn = sqlite3.connect('game.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?)",
                       (msg.from_user.id, None, "", 0, 0, 5))
        conn.commit()
        conn.close()

        # 🔥 SENGA XABAR
        bot.send_message(
            ADMIN_ID,
            f"🆕 USER!\nID: {msg.from_user.id}\nUsername: @{msg.from_user.username}"
        )

        return choose_anime(msg)

    bot.send_message(msg.chat.id, "Xush kelibsiz!", reply_markup=menu())

# --- ANIME ---
def choose_anime(msg):
    m = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    for a in CARDS_DATA:
        m.add(a)
    bot.send_message(msg.chat.id, "Anime tanla:", reply_markup=m)

@bot.message_handler(func=lambda m: m.text in CARDS_DATA)
def set_anime(msg):
    conn = sqlite3.connect('game.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET anime=? WHERE id=?", (msg.text, msg.from_user.id))
    conn.commit()
    conn.close()
    bot.send_message(msg.chat.id, "Tanlandi!", reply_markup=menu())

# --- CARD ---
@bot.message_handler(func=lambda m: m.text == "🎴 Karta olish")
def get_card(msg):
    user = get_user(msg.from_user.id)

    if not user or user[1] is None:
        return choose_anime(msg)

    if user[5] <= 0:
        return bot.send_message(msg.chat.id, "Chance yo'q!")

    star = random.randint(1,5)
    cards = [c for c in CARDS_DATA[user[1]] if c['star']==star]
    if not cards:
        cards = CARDS_DATA[user[1]]

    card = random.choice(cards)

    cards_list = user[2].split(',') if user[2] else []
    items = user[3]

    if card['name'] in cards_list:
        items += star

    cards_list.append(card['name'])

    conn = sqlite3.connect('game.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET cards=?, items=?, chances=chances-1 WHERE id=?",
                   (",".join(cards_list), items, msg.from_user.id))
    conn.commit()
    conn.close()

    caption = f"🎉 {card['name']} ({star}⭐)\n💎 {items}"

    bot.send_photo(msg.chat.id, card['img'], caption=caption)

# --- MY CARDS ---
@bot.message_handler(func=lambda m: m.text == "🎒 Kartalarim")
def my_cards(msg):
    user = get_user(msg.from_user.id)
    if user and user[2]:
        bot.send_message(msg.chat.id, user[2])
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
