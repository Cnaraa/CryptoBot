from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_buttons = ['Добавить операцию', 'Портфель', 'Как пользоваться ботом?']
main_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
main_keyboard.add(main_buttons[0], main_buttons[1]).add(main_buttons[2])


actions_buttons = ['Купить', 'Продать', 'Депозит', 'Вернуться']
actions_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
actions_keyboard.add(actions_buttons[0], actions_buttons[1], actions_buttons[2]).add(actions_buttons[3])

close_action_button = ['Отменить операцию']
close_action_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
close_action_keyboard.add(close_action_button[0])