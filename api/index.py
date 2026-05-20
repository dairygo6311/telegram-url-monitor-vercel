import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, Response
import json

app = Flask(__name__)

HTML_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Telegram URL Monitor Bot</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', sans-serif;
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
        @keyframes pulse { 0%,100%{transform:scale(1)} 50%{transform:scale(1.05)} }
        h1 { font-size: 2.5rem; margin-bottom: 20px; font-weight: 700; }
        .subtitle { font-size: 1.2rem; margin-bottom: 30px; opacity: 0.9; }
        .features { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px,1fr)); gap: 20px; margin: 40px 0; }
        .feature { background: rgba(255,255,255,0.1); padding: 20px; border-radius: 15px; border: 1px solid rgba(255,255,255,0.2); }
        .feature-icon { font-size: 2rem; margin-bottom: 10px; }
        .status { background: rgba(46,204,113,0.2); border: 2px solid #2ecc71; padding: 15px; border-radius: 10px; margin: 30px 0; font-weight: bold; }
        .footer { margin-top: 40px; opacity: 0.7; font-size: 0.9rem; }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">🤖📊</div>
        <h1>Telegram URL Monitor Bot</h1>
        <p class="subtitle">Advanced URL monitoring with real-time alerts and keep-alive pings</p>
        <div class="status">✅ Bot is running and monitoring your URLs!</div>
        <div class="features">
            <div class="feature"><div class="feature-icon">⚡</div><h3>Real-time Monitoring</h3><p>URL health checks every minute</p></div>
            <div class="feature"><div class="feature-icon">🔔</div><h3>Smart Alerts</h3><p>Instant Telegram notifications</p></div>
            <div class="feature"><div class="feature-icon">📈</div><h3>Analytics</h3><p>Response times & uptime stats</p></div>
            <div class="feature"><div class="feature-icon">👥</div><h3>Multi-Admin</h3><p>Independent URL management</p></div>
        </div>
        <div class="footer">
            <p>🚀 Deployed on Vercel | Built with Python & python-telegram-bot</p>
        </div>
    </div>
</body>
</html>"""


@app.route('/', methods=['GET'])
def index():
    return Response(HTML_PAGE, mimetype='text/html')


@app.route('/health', methods=['GET'])
def health():
    return Response('{"status":"healthy"}', mimetype='application/json')


@app.route('/status', methods=['GET'])
def status():
    try:
        from data_manager import DataManager
        dm = DataManager()
        all_urls = dm.get_all_urls()
        body = json.dumps({"status": "running", "total_urls": len(all_urls)})
    except Exception as e:
        body = json.dumps({"status": "error", "error": str(e)})
    return Response(body, mimetype='application/json')
