from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_buttons = ['Добавить операцию', 'Портфель']
main_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
main_keyboard.add(main_buttons[0], main_buttons[1])


actions_buttons = ['Купить', 'Продать', 'Депозит']
actions_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
actions_keyboard.add(actions_buttons[0], actions_buttons[1]).add(actions_buttons[2])