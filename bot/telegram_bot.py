from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    ConversationHandler,
    CommandHandler,
    filters,
    MessageHandler,
)

from bot.handlers.manage_user_file import (
    add_ref_image_handler,
    add_driving_video_handler,
    cancel_handler, 
    ask_voice_handler,
    add_voice_handler,
)
from bot.handlers.manage_users import start, add_user, add_admin, del_user, show_users
from bot.handlers.manage_lang import set_language, language_button, set_voice, voice_button
from config import supported_languages, supported_voices, ADD_DRIVING_VIDEO, ADD_VOICE



class TalkerBot:
    def __init__(self, token: str):
        self.app = ApplicationBuilder().token(token).build()
        self._register_handlers()


    def _register_handlers(self):
        self.app.add_handler(CommandHandler("start", start))
        
        self.app.add_handler(CommandHandler("set_lang", set_language))
        lang_buttons = '|'.join(list(supported_languages))
        self.app.add_handler(CallbackQueryHandler(language_button, pattern=f'^({lang_buttons})$'))

        self.app.add_handler(CommandHandler("set_voice", set_voice))
        voice_buttons = '|'.join(list(supported_voices))
        self.app.add_handler(CallbackQueryHandler(voice_button, pattern=f'^({voice_buttons})$'))

        voice_conv_handler = ConversationHandler(
            entry_points=[CommandHandler("upload_voice", ask_voice_handler)],
            states={
                ADD_VOICE: [MessageHandler(filters.ALL & ~filters.COMMAND, add_voice_handler)],
            },
            fallbacks=[CommandHandler('cancel', cancel_handler)],
            name="voice_conversation"
        )
        self.app.add_handler(voice_conv_handler)

        conv_handler = ConversationHandler(
            entry_points=[MessageHandler(filters.PHOTO & ~filters.COMMAND, add_ref_image_handler)],
            states={
                ADD_DRIVING_VIDEO: [MessageHandler((filters.VIDEO | filters.VIDEO_NOTE) & ~filters.COMMAND, add_driving_video_handler)],
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