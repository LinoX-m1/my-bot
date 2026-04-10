import telebot
from flask import Flask
from threading import Thread

# Flask server yaratamiz (bot o'chib qolmasligi uchun)
app = Flask('')

@app.route('/')
def home():
    return "Bot ishlayapti!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# BU YERGA TOKENINGIZNI QO'YING
bot = telebot.TeleBot("8770000703:AAEXRnIxr8iRBu_eUP9f3GPi8yBID6oTEmw")

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Salom! Men har doim ishlaydigan botman!")

@bot.message_handler(func=lambda m: True)
def echo_all(message):
    bot.reply_to(message, "Siz yozdingiz: " + message.text)

keep_alive()
bot.infinity_polling()
