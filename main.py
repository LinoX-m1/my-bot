import telebot
import random
import sqlite3
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
TOKEN = os.getenv("TOKEN")
bot = telebot.TeleBot(TOKEN)

# --- DATABASE ---
def init_db():
    conn = sqlite3.connect("game.db")
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY,
            username TEXT,
            cards TEXT,
            items INTEGER,
            chances INTEGER
        )
    """)
    
    # Activity log table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS activity_log(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            username TEXT,
            action TEXT,
            timestamp TEXT
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

def create_user(user_id, username):
    conn = sqlite3.connect("game.db")
    cur = conn.cursor()
    cur.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?)",
                (user_id, username, "", 0, 5))
    conn.commit()
    conn.close()

def update_user(user_id, cards, items, chances):
    conn = sqlite3.connect("game.db")
    cur = conn.cursor()
    cur.execute("UPDATE users SET cards=?, items=?, chances=? WHERE id=?",
                (cards, items, chances, user_id))
    conn.commit()
    conn.close()

# --- ACTIVITY LOG ---
def log_activity(user_id, username, action):
    """Foydalanuvchi faoliyatini qayd qilish"""
    try:
        conn = sqlite3.connect("game.db")
        cur = conn.cursor()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cur.execute("INSERT INTO activity_log (user_id, username, action, timestamp) VALUES (?, ?, ?, ?)",
                    (user_id, username, action, timestamp))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Log xatosi: {e}")

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
    markup.add("📊 Mening ma'lumotlarim")
    return markup

# --- START ---
@bot.message_handler(commands=['start'])
def start(msg):
    try:
        user_id = msg.from_user.id
        username = msg.from_user.username or "no_username"
        
        if not get_user(user_id):
            create_user(user_id, username)
            log_activity(user_id, username, "Botni ishga tushirdi (START)")
        
        bot.send_message(msg.chat.id, f"Xush kelibsiz, @{username}!", reply_markup=menu())
    except Exception as e:
        print(f"Start xatosi: {e}")
        bot.send_message(msg.chat.id, "❌ Xatolik yuz berdi!")

# --- KARTA OLISH ---
@bot.message_handler(func=lambda m: m.text == "🎴 Karta olish")
def get_card(msg):
    try:
        user_id = msg.from_user.id
        username = msg.from_user.username or "no_username"
        user = get_user(user_id)

        if user[4] <= 0:
            bot.send_message(msg.chat.id, "❌ Chance tugadi!")
            return

        star = get_star()
        possible = [c for c in CARDS if c[1] == star]
        card = random.choice(possible)

        cards_list = user[2].split(",") if user[2] else []
        items = user[3]

        if card[0] in cards_list:
            items += star
        else:
            cards_list.append(card[0])

        new_chances = user[4] - 1
        update_user(user_id, ",".join(cards_list), items, new_chances)
        
        # Activity log
        log_activity(user_id, username, f"Karta oldi: {card[0]} ({star}⭐)")

        bot.send_message(
            msg.chat.id,
            f"🎉 {card[0]} ({star}⭐)\n💎 {items}\n🎯 Qolgan chance: {new_chances}"
        )
    except Exception as e:
        print(f"Karta olish xatosi: {e}")
        bot.send_message(msg.chat.id, "❌ Xatolik yuz berdi!")

# --- KARTALARIM ---
@bot.message_handler(func=lambda m: m.text == "🎒 Kartalarim")
def my_cards(msg):
    try:
        user_id = msg.from_user.id
        username = msg.from_user.username or "no_username"
        user = get_user(user_id)

        if user[2]:
            cards = user[2].split(",")
            text = "🎒 Sening kartalaring:\n\n"
            for c in cards:
                text += f"• {c}\n"
            
            text += f"\n💎 Jami itemlar: {user[3]}"
            bot.send_message(msg.chat.id, text)
        else:
            bot.send_message(msg.chat.id, "Bo'sh 📭")
        
        log_activity(user_id, username, "Kartalarni ko'rdi")
    except Exception as e:
        print(f"Kartalarim xatosi: {e}")
        bot.send_message(msg.chat.id, "❌ Xatolik yuz berdi!")

# --- MENING MA'LUMOTLARIM ---
@bot.message_handler(func=lambda m: m.text == "📊 Mening ma'lumotlarim")
def my_info(msg):
    try:
        user_id = msg.from_user.id
        username = msg.from_user.username or "no_username"
        user = get_user(user_id)
        
        text = f"""
👤 **Ma'lumotlaringiz:**
🆔 User ID: `{user_id}`
📝 Username: @{username}
🎴 Kartalar soni: {len(user[2].split(',')) if user[2] else 0}
💎 Jami itemlar: {user[3]}
🎯 Qolgan chance: {user[4]}
        """
        
        bot.send_message(msg.chat.id, text, parse_mode="Markdown")
        log_activity(user_id, username, "Ma'lumotlarini ko'rdi")
    except Exception as e:
        print(f"Ma'lumot xatosi: {e}")
        bot.send_message(msg.chat.id, "❌ Xatolik yuz berdi!")

# --- RUN ---
if __name__ == "__main__":
    init_db()
    print("Bot ishga tushdi... ✅")
    bot.infinity_polling()
