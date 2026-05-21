import os
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    ContextTypes,
    filters,
)
from dotenv import load_dotenv
from downloader import download_video

load_dotenv()

BOT_TOKEN = os.getenv("8928147933:AAF2A4YVxQLOnJM6fxzg46oPsIhFnmWm53g")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text

    await update.message.reply_text("⏳ Yuklanmoqda...")

    try:
        file_path = download_video(url)

        await update.message.reply_video(
            video=open(file_path, "rb")
        )

        os.remove(file_path)

    except Exception as e:
        await update.message.reply_text(f"Xato: {e}")


app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(
    MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
)

print("Bot ishladi...")

app.run_polling()
