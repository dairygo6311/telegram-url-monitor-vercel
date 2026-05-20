"""
URL Monitor Cron Job Handler for Vercel
Called every minute by Vercel Cron to ping all monitored URLs
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

    summary = {
        "total": len(results),
        "online": sum(1 for r in results.values() if r["success"]),
        "offline": sum(1 for r in results.values() if not r["success"]),
        "details": {
            url: {
                "success": r["success"],
                "status_code": r["status_code"],
                "response_time": round(r["response_time"], 3)
            }
            for url, r in results.items()
        }
    }
    return summary


class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        try:
            summary = asyncio.run(run_monitoring())
            response_body = json.dumps({
                "status": "ok",
                "message": f"Pinged {summary['total']} URLs",
                "online": summary["online"],
                "offline": summary["offline"],
                "details": summary["details"]
            }).encode()

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(response_body)

        except Exception as e:
            logger.error(f"Monitor error: {e}")
            error_body = json.dumps({"status": "error", "error": str(e)}).encode()
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(error_body)

    def do_POST(self):
        self.do_GET()

    def log_message(self, format, *args):
        pass
