from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State, default_state
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from config import TOKEN
from keyboards import *
from check_token import check_token
from db.create_db import *


storage = MemoryStorage()
bot = Bot(TOKEN)
dp = Dispatcher(bot, storage=storage)


class Actions(StatesGroup):

    choose_actions = State()
    add_token = State()
    add_token_amount = State()
    add_token_price = State()
    add_token_in_database = State()
    buy_token = State()
    sell_token = State()
    portfolio = State()


async def on_startup(_):
    print('Бот успешно запущен!')


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await bot.send_message(chat_id=message.from_user.id,
                           text="Привет! 🤖 Этот бот поможет тебе управлять своим криптопортфелем.\n"\
                           "Не забудь заглянуть в 'Как пользоваться ботом?' для подробной инструкции.\n"\
                            "Удачи в трейдинге! 🚀",
                           reply_markup=main_keyboard)
    await message.delete()


@dp.message_handler(Text(equals='Портфель'))
async def show_portfolio(message: types.Message):
    portfolio = get_user_portfolio(int(message.from_user.id))
    message_text = 'Монета | Количество | Общая стоимость | Финансовый результат\n'
    for token in portfolio:
        token_info = portfolio[token]
        message_text += f"{token} | {token_info['token_amount']} | {token_info['token_value']}$ | \
        {token_info['financial_results']}$ ({token_info['financial_results_percentages']}%)\n"
        message_text += '-----------------------------------\n'
    await message.answer(message_text)

@dp.message_handler(Text(equals='Добавить операцию'))
async def add_new_token(message: types.Message, state : FSMContext):
    await bot.send_message(chat_id=message.from_user.id,
                           text="Выберите операцию",
                           reply_markup=actions_keyboard)
    await state.set_state(Actions.choose_actions)


@dp.message_handler(Text(equals='Отменить операцию'), state="*")
async def cancel_action(message: types.Message, state : FSMContext):
    await bot.send_message(chat_id=message.from_user.id,
                           text="Операция отменена",
                           reply_markup=main_keyboard)
    await state.finish()


@dp.message_handler(Text(equals='Как пользоваться ботом?'))
async def sent_help_message(message: types.Message, state : FSMContext):
    help_text = "🤖 **Как пользоваться ботом?** 🤖\n\n"\
        "**● Добавить операцию:** Нажми, чтобы купить/продать монеты или добавить их в портфель.\n"\
        "   ● **Купить:** Покупка новой монеты за счет USDT в портфеле. Укажи кол-во и цену.\n"\
        "   ● **Продать:** Продажа имеющейся монеты. Укажи кол-во, и монета будет продана за USDT.\n"\
        "   ● **Депозит:** Добавление новой монеты в портфель. Укажи кол-во и цену.\n\n"\
        "**● Портфель:** Получи обзор своего текущего портфеля.\n\n"\
        "🚀 Приятного трейдинга! 🚀"
    await message.answer(help_text, parse_mode="Markdown")


@dp.message_handler(state=Actions.choose_actions)
async def choose_action(message: types.Message, state: FSMContext):
    await state.update_data(user_id=int(message.from_user.id))
    if message.text == "Депозит":
        await state.update_data(action='add')
        await state.set_state(Actions.add_token)
        await bot.send_message(chat_id=message.from_user.id,
                           text = "Введите название монеты",
                           reply_markup=close_action_keyboard)
    elif message.text == "Купить":
        await state.update_data(action='buy')
        await state.set_state(Actions.buy_token)
        await bot.send_message(chat_id=message.from_user.id,
                           text = "Введите название монеты",
                           reply_markup=close_action_keyboard)
    elif message.text == 'Вернуться':
        await state.finish()
        await bot.send_message(chat_id=message.from_user.id, text='Возврат в главное меню', reply_markup=main_keyboard)
        return None
    elif message.text == "Продать":
        await state.update_data(action='sell')
        await state.set_state(Actions.sell_token)
        await bot.send_message(chat_id=message.from_user.id,
                           text = "Введите название монеты",
                           reply_markup=close_action_keyboard)
    else:
        await state.finish()
        await bot.send_message(chat_id=message.from_user.id, 
                               text='Некорректное действие', 
                               reply_markup=main_keyboard)



@dp.message_handler(state=Actions.sell_token)
async def sell_token_from_portfolio(message: types.Message, state: FSMContext):
    await state.update_data(token_name=message.text.upper())
    new_token = await state.get_data()
    if check_token_in_portfolio(new_token):
        await message.answer("Введите количество монет")
        await state.set_state(Actions.add_token_amount)
    else:
        await bot.send_message(chat_id=message.from_user.id,
                               text=f"Монеты {new_token['token_name']} нет в вашем портфеле",
                               reply_markup=main_keyboard)
        await state.finish()


@dp.message_handler(state=Actions.buy_token)
async def buy_token_for_portfolio(message: types.Message, state: FSMContext):
    if check_token(message.text.upper()):
        await state.update_data(token_name=message.text.upper())
        await message.answer("Введите количество монет")
        await state.set_state(Actions.add_token_amount)
    else:
        await bot.send_message(chat_id=message.from_user.id,
                               text='Монета не найдена на бирже',
                               reply_markup=main_keyboard)
        await state.finish()

@dp.message_handler(state=Actions.add_token)
async def add_new_token_in_database(message: types.Message, state: FSMContext):
    if check_token(message.text.upper()):
        await state.update_data(token_name=message.text.upper())
        await message.answer('Введите количество монет')
        await state.set_state(Actions.add_token_amount)
    else:
        await bot.send_message(chat_id=message.from_user.id,
                               text='Монета не найдена на бирже',
                               reply_markup=main_keyboard)
        await state.finish()


@dp.message_handler(state=Actions.add_token_amount)
async def add_token_amount(message: types.Message, state: FSMContext):
    try:
        if "," in message.text:
            add_token_amount = message.text.replace(',', '.')
            add_token_amount = float(add_token_amount)
        else:
            add_token_amount = float(message.text)
        await state.update_data(token_amount=add_token_amount)
        await message.answer('Введите цену монеты')
        await state.set_state(Actions.add_token_price)
    except ValueError:
        await bot.send_message(chat_id=message.from_user.id,
                               text='Введено некорректное значение',
                               reply_markup=main_keyboard)
        await state.finish()


@dp.message_handler(state=Actions.add_token_price)
async def add_token_price(message: types.Message, state: FSMContext):
    try:
        if "," in message.text:
            add_token_price = message.text.replace(',', '.')
            add_token_price = float(add_token_price)
        else:
            add_token_price = float(message.text)
    except ValueError:
        await bot.send_message(chat_id=message.from_user.id,
                            text='Введено некорректное значение',
                            reply_markup=main_keyboard)
        await state.finish()
    else:
        await state.update_data(token_price=add_token_price)
        new_token = await state.get_data()
        #print(new_token)
        if new_token['action'] == 'add':
            result = check_id_in_database(new_token)
            if result:
                await bot.send_message(chat_id=message.from_user.id,
                                text=f"Монета {new_token['token_name']} количеством {new_token['token_amount']} по цене {new_token['token_price']} добавлена в ваш протфель",
                                reply_markup=main_keyboard)
            else:
                await bot.send_message(chat_id=message.from_user.id,
                                    text='Ошибка')
        elif new_token['action'] == 'sell':
            if sell_token(new_token):
                await bot.send_message(chat_id=message.from_user.id,
                                    text=f"Монета {new_token['token_name']} в количестве {new_token['token_amount']} успешно продана",
                                    reply_markup=main_keyboard)
            else:
                await bot.send_message(chat_id=message.from_user.id,
                                    text=f"Недостаточно монет для продажи",
                                    reply_markup=main_keyboard)
        elif new_token['action'] == 'buy':
            if check_token_in_portfolio(new_token):
                await bot.send_message(chat_id=message.from_user.id,
                                    text=f"Монета {new_token['token_name']} в количестве {new_token['token_amount']} добавлена в ваш портфель",
                                    reply_markup=main_keyboard)
            else:
                await bot.send_message(chat_id=message.from_user.id,
                                    text='В вашем портфеле недостаточно средств',
                                    reply_markup=main_keyboard)
        await state.finish()


if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup,
                           skip_updates=True)  # Запуск бота