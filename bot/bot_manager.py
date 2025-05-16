import os
import json
import sqlite3

from config import db_path, messages_path, supported_languages, ADMIN_NICKNAME
from utils.logging_config import setup_logging
from utils.singleton import singleton



@singleton
class BotManager:
    def __init__(self, db_path: str = db_path, messages_file: str = messages_path):
        self.default_admin = ADMIN_NICKNAME.replace("@", "")
        self._init_db(db_path)
        self.supported_languages = supported_languages
        self.messages = self._load_messages(messages_file)
        self.logger = setup_logging('BotManager')


    def _init_db(self, db_path: str):
        """Initialize SQLite database with the users table."""
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                language TEXT NOT NULL DEFAULT 'en',
                voice TEXT NOT NULL DEFAULT 'orig',
                is_admin INTEGER DEFAULT 0
            )
        """)

        self.cursor.execute("SELECT username FROM users WHERE username = ?", (self.default_admin,))
        if self.cursor.fetchone() is None:  # Only add if not already present
            self.cursor.execute("INSERT INTO users (username, language, voice, is_admin) VALUES (?, ?, ?, ?)", (self.default_admin, 'en', 'orig', 1))

        self.conn.commit()

    
    def _load_messages(self, messages_file: str) -> dict[str, dict[str, str]]:
        """Load messages from external JSON file."""
        if not os.path.exists(messages_file):
            raise FileNotFoundError(f"Messages file '{messages_file}' not found.")
        with open(messages_file, 'r', encoding='utf-8') as f:
            return json.load(f)


    def set_user_language(self, username: str, lang: str) -> bool:
        """
        Set user's language preference.
        Args:
            username: Telegram user ID.
            lang: Language key ('en', 'ru', 'de').
        Returns:
            bool: True if successful, False if language is unsupported.
        """
        if lang not in self.supported_languages:
            return False
        
        self.cursor.execute("""
            UPDATE users SET language = ? WHERE username = ?
        """, (lang, username))
        self.conn.commit()
        return True


    def get_user_language(self, username: str) -> str:
        """
        Get user's preferred language, default is 'en'.
        Args:
            username: Telegram username.
        Returns:
            str: Language key ('en', 'ru', 'de').
        """
        self.cursor.execute("""
            SELECT language FROM users WHERE username = ?
        """, (username,))
        result = self.cursor.fetchone()
        return result[0] if result else 'en'
    

    def set_user_voice(self, username: str, voice: str) -> bool:
        """
        Set user's voice preference.
        Args:
            username: Telegram user ID.
            lang: Language key ('orig', 'male', 'female', 'custom').
        Returns:
            bool: True if successful, False if language is unsupported.
        """
        self.cursor.execute("""
            UPDATE users SET voice = ? WHERE username = ?
        """, (voice, username))
        self.conn.commit()
        return True


    def get_user_voice(self, username: str) -> str:
        """
        Get user's preferred voice, default is 'orig'.
        Args:
            username: Telegram username.
        Returns:
            str: Voice key ('orig', 'male', 'female', 'custom').
        """
        self.cursor.execute("""
            SELECT voice FROM users WHERE username = ?
        """, (username,))
        result = self.cursor.fetchone()
        return result[0] if result else 'orig'


    def get_message(self, message_key: str, lang: str = "en") -> str:
        """
        Get a message in specified language.
        Args:
            message_key: Key for the message ('welcome').
            lang: Language key.
        Returns:
            str: Message in requested language.
        """
        if message_key not in self.messages:
            return f"Message '{message_key}' not found."
        return self.messages[message_key][lang]


    def get_supported_languages(self) -> set:
        """Return supported languages."""
        return self.supported_languages


    def is_admin(self, username: str) -> bool:
        """Check if a user is an admin."""
        username = username.replace("@", "")
        self.cursor.execute("SELECT is_admin FROM users WHERE username = ?", (username,))
        result = self.cursor.fetchone()
        return result is not None and result[0] == 1
    

    def is_allowed_user(self, username: str) -> bool:
        """Check if a user is allowed to use the bot."""
        username = username.replace("@", "")
        self.cursor.execute("SELECT username FROM users WHERE username = ?", (username,))
        result = self.cursor.fetchone() is not None
        return result
    

    def add_user(self, username: str, is_admin: int = 0) -> None:
        """Add a user to the allowed list (or update, admin only)."""
        username = username.replace("@", "")
        self.cursor.execute("INSERT OR REPLACE INTO users (username, language, voice, is_admin) VALUES (?, ?, ?, ?)", (username, 'en', 'orig', is_admin))
        self.conn.commit()


    def remove_user(self, username: str) -> None:
        """Remove a user from the allowed list (admin only)."""
        username = username.replace("@", "")
        self.cursor.execute("DELETE FROM users WHERE username = ?", (username,))
        self.conn.commit()


    def list_users(self) -> list:
        """Return a list of all users and their roles (admin only)."""
        self.cursor.execute("SELECT username, language, voice, is_admin FROM users")
        users = self.cursor.fetchall()
        return users
