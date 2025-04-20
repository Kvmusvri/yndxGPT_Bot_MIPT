from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types.web_app_info import WebAppInfo


main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Расскажи историю')],
        [KeyboardButton(text='Расскажи шутку')],
        [KeyboardButton(text='Узнать обстановку')]
    ],
    resize_keyboard=True,
)