"""
Main web page handler for Vercel
Serves the bot status/welcome page
"""

import sys
import os
import json
from http.server import BaseHTTPRequestHandler

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

HTML_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Telegram URL Monitor Bot</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
        }
        .container {
            text-align: center;
            max-width: 800px;
            padding: 40px;
            background: rgba(255,255,255,0.1);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            box-shadow: 0 8px 32px rgba(31,38,135,0.37);
            border: 1px solid rgba(255,255,255,0.18);
            margin: 20px;
        }
        .logo { font-size: 4rem; margin-bottom: 20px; animation: pulse 2s infinite; }
        @keyframes pulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.05); }
        }
        h1 { font-size: 2.5rem; margin-bottom: 20px; font-weight: 700; }
        .subtitle { font-size: 1.2rem; margin-bottom: 30px; opacity: 0.9; }
        .features {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 40px 0;
        }
        .feature {
            background: rgba(255,255,255,0.1);
            padding: 20px;
            border-radius: 15px;
            border: 1px solid rgba(255,255,255,0.2);
        }
        .feature-icon { font-size: 2rem; margin-bottom: 10px; }
        .status {
            background: rgba(46,204,113,0.2);
            border: 2px solid #2ecc71;
            padding: 15px;
            border-radius: 10px;
            margin: 30px 0;
            font-weight: bold;
        }
        .telegram-link {
            display: inline-block;
            background: #0088cc;
            color: white;
            text-decoration: none;
            padding: 15px 30px;
            border-radius: 25px;
            font-weight: bold;
            font-size: 1.1rem;
            margin-top: 20px;
            transition: transform 0.3s ease;
        }
        .telegram-link:hover { transform: translateY(-2px); }
        .footer { margin-top: 40px; opacity: 0.7; font-size: 0.9rem; }
        @media (max-width: 600px) {
            h1 { font-size: 2rem; }
            .logo { font-size: 3rem; }
            .container { padding: 30px 20px; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">🤖📊</div>
        <h1>Telegram URL Monitor Bot</h1>
        <p class="subtitle">Advanced URL monitoring with real-time alerts and keep-alive pings</p>
        <div class="status">✅ Bot is running and monitoring your URLs!</div>
        <div class="features">
            <div class="feature">
                <div class="feature-icon">⚡</div>
                <h3>Real-time Monitoring</h3>
                <p>Continuous URL health checks every minute</p>
            </div>
            <div class="feature">
                <div class="feature-icon">🔔</div>
                <h3>Smart Alerts</h3>
                <p>Instant Telegram notifications when URLs go down</p>
            </div>
            <div class="feature">
                <div class="feature-icon">📈</div>
                <h3>Performance Analytics</h3>
                <p>Track response times and uptime statistics</p>
            </div>
            <div class="feature">
                <div class="feature-icon">👥</div>
                <h3>Multi-Admin Support</h3>
                <p>Multiple admins with independent URL management</p>
            </div>
        </div>
        <a href="https://t.me/your_bot_username" class="telegram-link">📱 Open Bot in Telegram</a>
        <div class="footer">
            <p>🚀 Deployed on Vercel | Built with Python & python-telegram-bot</p>
            <p>Keep your websites alive 24/7 with automated monitoring</p>
        </div>
    </div>
</body>
</html>"""


class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        path = self.path.split('?')[0]

        if path == '/health' or path == '/api/health':
            body = json.dumps({"status": "healthy", "service": "Telegram URL Monitor Bot"}).encode()
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(body)
            return

        if path == '/api/status':
            try:
                from config import Config
                from data_manager import DataManager
                config = Config()
                dm = DataManager()
                all_urls = dm.get_all_urls()
                body = json.dumps({
                    "status": "running",
                    "total_urls": len(all_urls),
                    "primary_admin": config.primary_admin_chat_id
                }).encode()
            except Exception as e:
                body = json.dumps({"status": "error", "error": str(e)}).encode()

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(body)
            return

        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(HTML_PAGE.encode('utf-8'))

    def log_message(self, format, *args):
        pass
