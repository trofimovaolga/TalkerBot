from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from config import supported_languages



def get_lang_markup():
    """Generate markup for language selection"""
    keyboard = []
    for lang in supported_languages:
        keyboard.append([
            InlineKeyboardButton(f"{lang.upper()}", callback_data=f"{lang}"),
        ])

    return InlineKeyboardMarkup(keyboard)
