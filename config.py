"""
Configuration management for Telegram URL Monitor Bot
Vercel-compatible version - uses environment variables
"""

import os
import json
import logging

logger = logging.getLogger(__name__)

DATA_DIR = "/tmp"

class Config:
    def __init__(self):
        self.bot_token = os.getenv("BOT_TOKEN", "")
        if not self.bot_token:
            raise ValueError("BOT_TOKEN environment variable is required. Set it in Vercel dashboard.")

        self.primary_admin_chat_id = int(os.getenv("ADMIN_CHAT_ID", "1691680798"))
        self.admin_chat_ids = [self.primary_admin_chat_id]
        self.admin_data_file = os.path.join(DATA_DIR, "admin_data.json")
        self.ping_interval = 60
        self.request_timeout = 30
        self.data_file = os.path.join(DATA_DIR, "urls_data.json")
        self.log_file = "bot.log"
        self._load_admin_data()

    def _load_admin_data(self):
        try:
            with open(self.admin_data_file, 'r') as f:
                data = json.load(f)
                self.admin_chat_ids = data.get('admin_chat_ids', [self.primary_admin_chat_id])
                if self.primary_admin_chat_id not in self.admin_chat_ids:
                    self.admin_chat_ids.append(self.primary_admin_chat_id)
        except (FileNotFoundError, json.JSONDecodeError):
            self._save_admin_data()

    def _save_admin_data(self):
        try:
            os.makedirs(DATA_DIR, exist_ok=True)
            data = {
                'admin_chat_ids': self.admin_chat_ids,
                'primary_admin': self.primary_admin_chat_id
            }
            with open(self.admin_data_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving admin data: {e}")

    def is_admin(self, chat_id):
        return chat_id in self.admin_chat_ids

    def is_primary_admin(self, chat_id):
        return chat_id == self.primary_admin_chat_id

    def add_admin(self, chat_id):
        if chat_id not in self.admin_chat_ids:
            self.admin_chat_ids.append(chat_id)
            self._save_admin_data()
            return True
        return False

    def remove_admin(self, chat_id):
        if chat_id == self.primary_admin_chat_id:
            return False
        if chat_id in self.admin_chat_ids:
            self.admin_chat_ids.remove(chat_id)
            self._save_admin_data()
            return True
        return False

    def get_admin_list(self):
        return self.admin_chat_ids.copy()
