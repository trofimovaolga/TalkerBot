from telegram import Update
from telegram.ext import CallbackContext

from bot.bot_manager import BotManager



async def start(update: Update, context: CallbackContext) -> None:
    """Handles the /start command. Sends a welcome message and asks for language preference."""
    username = update.effective_user.username

    manager = BotManager()
    lang = manager.get_user_language(username)

    if not manager.is_allowed_user(username):
        manager.logger.warning(f'{username} tried issuing a command but was not allowed.')
        await update.message.reply_text(manager.get_message("access_denied"))
        return

    await update.message.reply_text(manager.get_message("welcome", lang))


async def add_user(update: Update, context: CallbackContext) -> None:
    """
    Handle adding a user to the allowlist.

    This function checks if the user is an admin, then attempts to add a new user to the allowlist.
    If the user is not an admin, it returns a 'not_authorized' message.
    If no arguments are provided, it asks the user to specify a username.
    If the user is already in the allowlist, it returns a 'user_exists' message.
    Otherwise, it adds the user to the allowlist and returns a 'user_added' message.
    """
    username = update.effective_user.username

    manager = BotManager()
    lang = manager.get_user_language(username)
    
    if not manager.is_admin(username):
        message = manager.get_message('not_authorized', lang)
    elif not context.args:
        message = manager.get_message('add_user', lang)
    else:
        new_user = context.args[0]
        new_user = new_user.replace('@', '')

        if manager.is_allowed_user(new_user):
            message = manager.get_message('user_exists', lang).format(username=new_user)
        else:
            manager.add_user(new_user)
            message = manager.get_message('user_added', lang).format(username=new_user)
            manager.logger.info(f'{username} added new user {new_user}')
    
    await update.message.reply_text(message)


async def add_admin(update: Update, context: CallbackContext) -> None:
    """
    Handle adding admin user.

    This function checks if the user is an admin, then attempts to add a new user to the allowlist.
    If the user is not an admin, it returns a 'not_authorized' message.
    If no arguments are provided, it asks the user to specify a username.
    If the user is already marked as admin in the allowlist, it returns a 'user_exists' message.
    Otherwise, it adds the user with admin's status to the allowlist and returns a 'user_added' message.
    
    """
    username = update.effective_user.username

    manager = BotManager()
    lang = manager.get_user_language(username)
    
    if not manager.is_admin(username):
        message = manager.get_message('not_authorized', lang)
    elif not context.args:
        message = manager.get_message('add_admin', lang)
    else:
        new_user = context.args[0]
        new_user = new_user.replace('@', '')

        if manager.is_allowed_user(new_user) and manager.is_admin(new_user):
            message = manager.get_message('user_exists', lang).format(username=new_user)
        else:
            manager.add_user(new_user, is_admin=1)
            message = manager.get_message('user_added', lang).format(username=new_user)
            manager.logger.info(f'{username} added new user {new_user}')
    
    await update.message.reply_text(message)


async def del_user(update: Update, context: CallbackContext) -> None:
    """
    Handle removing a user from the allowlist.

    This function checks if the user is an admin, then attempts to remove a user from the allowlist.
    If the user is not an admin, it returns a 'not_authorized' message.
    If no arguments are provided, it prompts the user to specify a username.
    If the user is not in the allowlist, it returns a 'user_not_found' message.
    Otherwise, it removes the user from the allowlist and returns a 'user_removed' message.
    """
    username = update.effective_user.username

    manager = BotManager()
    lang = manager.get_user_language(username)

    if not manager.is_admin(username):
        message = manager.get_message('not_authorized', lang)
    elif not context.args:
        message = manager.get_message('specify_username', lang)
    else:
        user_to_remove = context.args[0]
        user_to_remove = user_to_remove.replace('@', '')

        if manager.is_allowed_user(user_to_remove):
            manager.remove_user(user_to_remove)
            message = manager.get_message('user_removed', lang).format(username=user_to_remove)
            manager.logger.info(f'{username} removed user {user_to_remove}')
        else:
            message = manager.get_message('user_not_found', lang).format(username=user_to_remove)
    
    await update.message.reply_text(message)


async def show_users(update: Update, context: CallbackContext) -> None:
    """
    Handle showing the current users in the allowlist.

    This function checks if the user is an admin, then returns a list of users in the allowlist.
    If the user is not an admin, it returns a 'not_authorized' message.
    Otherwise, it returns a formatted list of users.
    """
    username = update.effective_user.username

    manager = BotManager()
    lang = manager.get_user_language(username)

    if not manager.is_admin(username):
        message = manager.get_message('not_authorized', lang)
    else:
        users_list = [f"{i+1}. @{e[0].replace('@', '')}, lang: {e[1]}, is admin: {e[2]}" for i, e in enumerate(manager.list_users())]
        users_list = sorted(users_list, key=lambda x: x[0])
        users_list = '\n'.join(users_list)
        message = manager.get_message('show_users', lang).format(users=users_list)

    await update.message.reply_text(message)
