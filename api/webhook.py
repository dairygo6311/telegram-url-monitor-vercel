"""
Telegram Webhook Handler for Vercel
Receives updates from Telegram and processes them
"""

import sys
import os
import json
import asyncio
import logging
from http.server import BaseHTTPRequestHandler

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def process_telegram_update(update_data: dict):
    from telegram import Update
    from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
    from config import Config
    from bot_handlers import BotHandlers
    from url_monitor import URLMonitor

    config = Config()
    url_monitor = URLMonitor()
    bot_handlers = BotHandlers(url_monitor, config)

    app = Application.builder().token(config.bot_token).build()

    app.add_handler(CommandHandler("start", bot_handlers.start_command))
    app.add_handler(CommandHandler("help", bot_handlers.help_command))
    app.add_handler(CommandHandler("seturl", bot_handlers.set_url_command))
    app.add_handler(CommandHandler("removeurl", bot_handlers.remove_url_command))
    app.add_handler(CommandHandler("listurls", bot_handlers.list_urls_command))
    app.add_handler(CommandHandler("status", bot_handlers.status_command))
    app.add_handler(CommandHandler("pingnow", bot_handlers.ping_now_command))
    app.add_handler(CommandHandler("addadmin", bot_handlers.add_admin_command))
    app.add_handler(CommandHandler("removeadmin", bot_handlers.remove_admin_command))
    app.add_handler(CommandHandler("listadmins", bot_handlers.list_admins_command))
    app.add_handler(CallbackQueryHandler(bot_handlers.button_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot_handlers.handle_message))

    await app.initialize()

    update = Update.de_json(update_data, app.bot)
    await app.process_update(update)

    await app.shutdown()


class handler(BaseHTTPRequestHandler):

    def do_POST(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            update_data = json.loads(body.decode('utf-8'))

            asyncio.run(process_telegram_update(update_data))

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"ok": true}')

        except Exception as e:
            logger.error(f"Webhook error: {e}")
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"ok": true}')

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(b'{"status": "webhook active", "bot": "Telegram URL Monitor"}')

    def log_message(self, format, *args):
        pass
