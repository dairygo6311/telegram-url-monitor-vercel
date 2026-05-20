import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, request, Response
import asyncio
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

FORM_HTML = """<!DOCTYPE html>
<html>
<head><title>Webhook Setup</title>
<style>
body{font-family:sans-serif;max-width:600px;margin:50px auto;padding:20px}
input{width:100%;padding:10px;margin:10px 0;font-size:16px;border:1px solid #ccc;border-radius:5px;box-sizing:border-box}
button{background:#0088cc;color:white;padding:12px 24px;border:none;border-radius:5px;font-size:16px;cursor:pointer}
button:hover{background:#006699}
.info{background:#f0f8ff;border:1px solid #0088cc;padding:15px;border-radius:5px;margin:20px 0}
</style></head>
<body>
<h1>🤖 Telegram Webhook Setup</h1>
<div class="info">
  Enter your Vercel domain to register the Telegram webhook.<br>
  Example: <code>my-bot.vercel.app</code>
</div>
<form method="GET">
  <label>Your Vercel Domain:</label>
  <input type="text" name="domain" placeholder="your-app.vercel.app" required>
  <button type="submit">Register Webhook</button>
</form>
<p><small>Make sure BOT_TOKEN is set in Vercel Environment Variables first.</small></p>
</body>
</html>"""


async def set_webhook(domain: str) -> dict:
    from telegram import Bot
    from config import Config
    config = Config()
    bot = Bot(token=config.bot_token)
    webhook_url = f"https://{domain}/api/webhook"
    await bot.set_webhook(url=webhook_url, allowed_updates=["message", "callback_query"])
    info = await bot.get_webhook_info()
    return {"webhook_url": webhook_url, "last_error": info.last_error_message}


@app.route('/', methods=['GET'])
def setup():
    domain = request.args.get('domain')
    if not domain:
        return Response(FORM_HTML, mimetype='text/html')
    try:
        result = asyncio.run(set_webhook(domain))
        body = json.dumps({"status": "success", "message": "Webhook registered!", **result}, indent=2)
        return Response(body, mimetype='application/json')
    except Exception as e:
        body = json.dumps({"status": "error", "error": str(e)})
        return Response(body, status=500, mimetype='application/json')
