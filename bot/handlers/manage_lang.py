import os

from telegram import Update
from telegram.ext import CallbackContext

from config import uploads_path, custom_voice_filename
from bot.bot_manager import BotManager
from bot.keyboard_markup import get_lang_markup, get_voice_markup



async def set_language(update: Update, context: CallbackContext) -> None:
    """
    Handle the language selection command. Displays language options if the user has permission.
    """
    username = update.effective_user.username

    manager = BotManager()

    if not manager.is_allowed_user(username):
        manager.logger.warning(f'{username} tried issuing a command but was not allowed.')
        await update.message.reply_text(manager.get_message("access_denied"))
        return

    cur_lang = manager.get_user_language(username)
    message = manager.get_message('choose_lang', cur_lang)
    await update.message.reply_text(message, reply_markup=get_lang_markup())


async def language_button(update: Update, context: CallbackContext) -> None:
    """
    Handle language selection callback when user clicks a language button. Sets the user's preferred language.
    """
    query = update.callback_query
    await query.answer()

    username = update.effective_user.username
    manager = BotManager()

    pref_lang = query.data
    manager.set_user_language(username, pref_lang)
    manager.logger.info(f"{username} set {pref_lang} language.")
    message = manager.get_message('lang_is_set', pref_lang).format(lang=pref_lang.upper())
    await query.message.reply_text(message)


async def set_voice(update: Update, context: CallbackContext) -> None:
    """
    Handle the voice selection command. Displays voice options if the user has permission.
    """
    username = update.effective_user.username
    manager = BotManager()

    if not manager.is_allowed_user(username):
        manager.logger.warning(f'{username} tried issuing a command but was not allowed.')
        await update.message.reply_text(manager.get_message("access_denied"))
        return

    cur_lang = manager.get_user_language(username)
    message = manager.get_message('choose_voice', cur_lang)
    cur_voice = manager.get_user_voice(username)
    custom = cur_voice if os.path.exists(os.path.join(uploads_path, username, custom_voice_filename)) else False
    await update.message.reply_text(message, reply_markup=get_voice_markup(cur_lang, cur_voice, has_custom=custom))


async def voice_button(update: Update, context: CallbackContext) -> None:
    """
    Handle voice selection callback when user clicks a language button. Sets the user's preferred language.
    """
    query = update.callback_query
    await query.answer()

    username = update.effective_user.username
    manager = BotManager()
    lang = manager.get_user_language(username)

    pref_voice = query.data
    manager.set_user_voice(username, pref_voice)
    manager.logger.info(f"{username} set {pref_voice} voice.")
    message = manager.get_message('voice_is_set', lang).format(voice=pref_voice)
    await query.message.reply_text(message)
