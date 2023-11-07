from aiogram import Bot, Dispatcher, executor, types
from config import TOKEN
from keyboards import *


bot = Bot(TOKEN)
dp = Dispatcher(bot)


async def on_startup(_):
    print('Бот успешно запущен!')


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await bot.send_message(chat_id=message.from_user.id,
                           text="Привет!",
                           reply_markup=main_keyboard)
    await message.delete()

if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup,
                           skip_updates=True)  # Запуск бота
