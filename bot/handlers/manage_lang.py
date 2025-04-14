from telegram import Update
from telegram.ext import CallbackContext

from bot.bot_manager import BotManager
from bot.keyboard_markup import get_lang_markup



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
