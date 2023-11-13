from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State, default_state
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from config import TOKEN
from keyboards import *
from check_token import check_token


storage = MemoryStorage()
bot = Bot(TOKEN)
dp = Dispatcher(bot, storage=storage)


class Actions(StatesGroup):

    add_token = State()
    add_token_count = State()


async def on_startup(_):
    print('Бот успешно запущен!')


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await bot.send_message(chat_id=message.from_user.id,
                           text="Привет!",
                           reply_markup=main_keyboard)
    await message.delete()


@dp.message_handler(Text(equals='Портфель'))
async def show_portfolio(message: types.Message):
    await message.answer('Тут будет состояние вашего портфеля')


@dp.message_handler(Text(equals='Добавить монету'))
async def add_new_token(message: types.Message, state : FSMContext):
    await message.answer('Введите название монеты')
    await state.set_state(Actions.add_token)


@dp.message_handler(state=Actions.add_token)
async def add_new_token_in_database(message: types.Message, state: FSMContext):
    if check_token(message.text.upper()):
        await state.update_data(token=message.text.upper())
        await message.answer('Введите количество монет')
        await state.set_state(Actions.add_token_count)
    else:
        await message.answer('Монета не найдена на бирже')
        await state.finish()


@dp.message_handler(state=Actions.add_token_count)
async def add_token_amount(message: types.Message, state: FSMContext):
    await state.update_data(token_count=message.text)
    new_token = await state.get_data()
    await bot.send_message(chat_id=message.from_user.id,
                           text=f"Монета {new_token['token']} количеством {new_token['token_count']} добавлена в ваш протфель")
    await state.finish()


if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup,
                           skip_updates=True)  # Запуск бота
