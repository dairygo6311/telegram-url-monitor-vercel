import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, Response
import asyncio
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)


async def run_monitoring():
    from telegram import Bot
    from config import Config
    from url_monitor import URLMonitor

    config = Config()
    url_monitor = URLMonitor()
    bot = Bot(token=config.bot_token)
    url_monitor.set_bot_instance(bot)
    url_monitor.set_admin_chat_id(str(config.primary_admin_chat_id))

    results = await url_monitor.ping_all_urls()
    return {
        "total": len(results),
        "online": sum(1 for r in results.values() if r["success"]),
        "offline": sum(1 for r in results.values() if not r["success"]),
    }


@app.route('/', methods=['GET', 'POST'])
def monitor():
    try:
        summary = asyncio.run(run_monitoring())
        body = json.dumps({"status": "ok", **summary})
    except Exception as e:
        logger.error(f"Monitor error: {e}")
        body = json.dumps({"status": "error", "error": str(e)})

    return Response(body, mimetype='application/json')
