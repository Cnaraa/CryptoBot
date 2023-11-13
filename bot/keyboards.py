from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_buttons = ['Добавить монету', 'Портфель']
main_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
main_keyboard.add(main_buttons[0], main_buttons[1])