import os
from dotenv import load_dotenv


load_dotenv()

TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
ADMIN_NICKNAME = os.getenv("ADMIN_NICKNAME")
ADD_DRIVING_VIDEO = 0

supported_languages = {"en", "de", "ru"}
messages_path = "./resources/bot_messages.json"
log_file_path = "./storage/logs/tg_bot.log"
uploads_path = "./storage/uploads/"
db_path = "./storage/db/users_data.db"

inference_path = "./LivePortrait/inference.py"
max_duration = 60  # Max video duration in seconds
cleanup_user_data = True  # Delete images and videos after processing
cleanup_animations = False  # Delete resulting animations after sending
