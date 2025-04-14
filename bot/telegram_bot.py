from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    ConversationHandler,
    CommandHandler,
    filters,
    MessageHandler,
)

from bot.handlers.manage_user_file import add_ref_image_handler, add_driving_video_handler, cancel_handler
from bot.handlers.manage_users import start, add_user, add_admin, del_user, show_users
from bot.handlers.manage_lang import set_language, language_button
from config import supported_languages, ADD_DRIVING_VIDEO


class TalkerBot:
    def __init__(self, token: str):
        self.app = ApplicationBuilder().token(token).build()
        self._register_handlers()


    def _register_handlers(self):
        self.app.add_handler(CommandHandler("start", start))

        self.app.add_handler(CommandHandler("set_lang", set_language))
        lang_buttons = '|'.join(list(supported_languages))
        self.app.add_handler(CallbackQueryHandler(language_button, pattern=f'^({lang_buttons})$'))

        conv_handler = ConversationHandler(
            entry_points=[MessageHandler(filters.PHOTO, add_ref_image_handler)],
            states={
                ADD_DRIVING_VIDEO: [MessageHandler(filters.VIDEO | filters.VIDEO_NOTE, add_driving_video_handler)],
            },
            fallbacks=[CommandHandler('cancel', cancel_handler)],
        )
        self.app.add_handler(conv_handler)

        # Admin only
        self.app.add_handler(CommandHandler("add_admin", add_admin))
        self.app.add_handler(CommandHandler("add_user", add_user))
        self.app.add_handler(CommandHandler("del_user", del_user))
        self.app.add_handler(CommandHandler("show_users", show_users))
    

    def run(self):
        self.app.run_polling()