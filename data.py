from dataclasses import dataclass
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from random import randint


@dataclass
class BotData:
    TOKEN: str = "YOUR_BOT_TOKEN"
    ADMIN: str = None
    ADMIN_KEY: str = ""
    for num in range(40):
        if num != 0 and num % 4 == 0:
            ADMIN_KEY += "-"
        ADMIN_KEY += list("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890")[randint(0, 61)]
			
def create_markup(btns: list) -> ReplyKeyboardMarkup:
    markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btns = [KeyboardButton(btn) for btn in btns]
    markup.add(*btns)
    return markup

def get_request(message, base: dict) -> list:
    user = str(message.from_user.id)
    return [int(user), message.text, base[user]['notes'], base[user]['templates'], base[user]['input']['request'], base[user]['input']['args']]
