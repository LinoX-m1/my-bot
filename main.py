
TOKEN = "8928147933:AAF2A4YVxQLOnJM6fxzg46oPsIhFnmWm53g"
ADMIN_ID = 7818670765
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.reply("Salom 👋 Men oddiy botman!")


@dp.message_handler()
async def echo(message: types.Message):
    await message.reply(message.text)


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
