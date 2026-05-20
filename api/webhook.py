import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, request, Response
import asyncio
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)


async def process_telegram_update(update_data: dict):
    from telegram import Update
    from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
    from config import Config
    from bot_handlers import BotHandlers
    from url_monitor import URLMonitor

    config = Config()
    url_monitor = URLMonitor()
    bot_handlers = BotHandlers(url_monitor, config)

    application = Application.builder().token(config.bot_token).build()

    application.add_handler(CommandHandler("start", bot_handlers.start_command))
    application.add_handler(CommandHandler("help", bot_handlers.help_command))
    application.add_handler(CommandHandler("seturl", bot_handlers.set_url_command))
    application.add_handler(CommandHandler("removeurl", bot_handlers.remove_url_command))
    application.add_handler(CommandHandler("listurls", bot_handlers.list_urls_command))
    application.add_handler(CommandHandler("status", bot_handlers.status_command))
    application.add_handler(CommandHandler("pingnow", bot_handlers.ping_now_command))
    application.add_handler(CommandHandler("addadmin", bot_handlers.add_admin_command))
    application.add_handler(CommandHandler("removeadmin", bot_handlers.remove_admin_command))
    application.add_handler(CommandHandler("listadmins", bot_handlers.list_admins_command))
    application.add_handler(CallbackQueryHandler(bot_handlers.button_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot_handlers.handle_message))

    async with application:
        update = Update.de_json(update_data, application.bot)
        await application.process_update(update)


@app.route('/', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        return Response('{"status":"webhook active","bot":"Telegram URL Monitor"}',
                        mimetype='application/json')
    try:
        update_data = request.get_json(force=True, silent=True) or {}
        if update_data:
            asyncio.run(process_telegram_update(update_data))
    except Exception as e:
        logger.error(f"Webhook error: {e}")

    return Response('{"ok":true}', mimetype='application/json')
