import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from moviepy.editor import VideoFileClip

# 🔥 Faqat bitta TOKEN bo‘ladi
TOKEN = "8928147933:AAF2A4YVxQLOnJM6fxzg46oPsIhFnmWm53g"
ADMIN_ID = 7818670765

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

logging.basicConfig(level=logging.INFO)


def extract_audio(video_path, audio_path):
    video = VideoFileClip(video_path)
    video.audio.write_audiofile(audio_path)
    video.close()


@dp.message_handler(content_types=['video'])
async def handle_video(message: types.Message):
    user = message.from_user

    logging.info(f"User: {user.id} @{user.username}")

    file = await bot.get_file(message.video.file_id)

    video_path = f"video_{user.id}.mp4"
    audio_path = f"audio_{user.id}.mp3"

    await bot.download_file(file.file_path, video_path)

    await message.reply("Video qabul qilindi...")

    extract_audio(video_path, audio_path)

    await message.reply_audio(types.InputFile(audio_path), caption=f"User ID: {user.id}")

    os.remove(video_path)
    os.remove(audio_path)


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
