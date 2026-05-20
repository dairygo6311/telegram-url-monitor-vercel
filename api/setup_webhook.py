"""
Webhook Setup Handler for Vercel
Visit /api/setup?domain=your-app.vercel.app to register the Telegram webhook
"""

import sys
import os
import json
import asyncio
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


async def set_webhook(domain: str) -> dict:
    from telegram import Bot
    from config import Config

    config = Config()
    bot = Bot(token=config.bot_token)

    webhook_url = f"https://{domain}/api/webhook"

    await bot.set_webhook(
        url=webhook_url,
        allowed_updates=["message", "callback_query"]
    )

    info = await bot.get_webhook_info()
    return {
        "webhook_url": webhook_url,
        "pending_updates": info.pending_update_count,
        "last_error": info.last_error_message
    }


class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        query_string = self.path.split('?', 1)[1] if '?' in self.path else ''
        params = parse_qs(query_string)
        domain = params.get('domain', [None])[0]

        if not domain:
            html = """<!DOCTYPE html>
<html>
<head><title>Webhook Setup</title>
<style>
body { font-family: sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; }
input { width: 100%; padding: 10px; margin: 10px 0; font-size: 16px; border: 1px solid #ccc; border-radius: 5px; }
button { background: #0088cc; color: white; padding: 12px 24px; border: none; border-radius: 5px; font-size: 16px; cursor: pointer; }
button:hover { background: #006699; }
.info { background: #f0f8ff; border: 1px solid #0088cc; padding: 15px; border-radius: 5px; margin: 20px 0; }
</style>
</head>
<body>
<h1>🤖 Telegram Webhook Setup</h1>
<div class="info">
  <strong>Instructions:</strong><br>
  Enter your Vercel domain below to register the Telegram webhook.<br>
  Example: <code>my-bot.vercel.app</code>
</div>
<form method="GET">
  <label>Your Vercel Domain:</label>
  <input type="text" name="domain" placeholder="your-app.vercel.app" required>
  <button type="submit">Register Webhook</button>
</form>
<p><small>Make sure BOT_TOKEN environment variable is set in Vercel dashboard first.</small></p>
</body>
</html>"""
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(html.encode())
            return

        try:
            result = asyncio.run(set_webhook(domain))
            response = {
                "status": "success",
                "message": "Webhook registered successfully!",
                "webhook_url": result["webhook_url"],
                "pending_updates": result["pending_updates"],
                "last_error": result["last_error"]
            }
            status_code = 200
        except Exception as e:
            response = {"status": "error", "error": str(e)}
            status_code = 500

        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response, indent=2).encode())

    def log_message(self, format, *args):
        pass
