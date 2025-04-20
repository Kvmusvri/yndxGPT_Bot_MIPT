from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types.web_app_info import WebAppInfo


estimate_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="👍", callback_data='est_good'),
            InlineKeyboardButton(text="👎", callback_data='est_bad'),

         ],
    ]
)