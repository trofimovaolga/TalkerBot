import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from bot.bot_manager import BotManager
from config import supported_languages, custom_voice_filename



def get_lang_markup():
    """Generate markup for language selection"""
    keyboard = []
    for lang in supported_languages:
        keyboard.append([
            InlineKeyboardButton(f"{lang.upper()}", callback_data=f"{lang}"),
        ])

    return InlineKeyboardMarkup(keyboard)


def get_voice_markup(lang: str, voice: str, has_custom=False):
    """
    Generate markup for voice selection.
    
    Args:
        lang: User's language code
        voice: Currently selected voice
        has_custom: Boolean indicating if custom voice is available
    """
    manager = BotManager()
    
    current_voice_id = voice.split()[0] if voice else ""
    voice_options = ["orig", "male", "female"]

    keyboard = []
    for option in voice_options:
        message = manager.get_message(option, lang)
        is_selected = current_voice_id == option
        prefix = "✅ " if is_selected else ""
        keyboard.append([
            InlineKeyboardButton(f"{prefix}{message}", callback_data=option)
        ])
    
    if has_custom:
        custom_message = manager.get_message("custom", lang)
        is_selected = current_voice_id == custom_voice_filename
        prefix = "✅ " if is_selected else ""
        keyboard.append([
            InlineKeyboardButton(f"{prefix}{custom_message}", callback_data="custom")
        ])
    
    return InlineKeyboardMarkup(keyboard)