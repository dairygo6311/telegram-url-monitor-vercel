"""
Utility functions for the Telegram URL Monitor Bot
"""

import re
import logging
from datetime import datetime
from typing import Dict, Any, List
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

def validate_url(url: str) -> bool:
    try:
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False

def format_url_list(urls: Dict[str, Dict[str, Any]]) -> str:
    if not urls:
        return "📭 No URLs are currently being monitored."

    message = f"📋 **Monitored URLs ({len(urls)})**\n\n"

    for url, data in urls.items():
        status = data.get("status", "pending")
        last_check = data.get("last_check")
        response_time = data.get("response_time")

        if status == "online":
            status_icon = "🟢"
            status_text = "Online"
        elif status == "offline":
            status_icon = "🔴"
            status_text = "Offline"
        else:
            status_icon = "⏳"
            status_text = "Pending"

        message += f"{status_icon} **{status_text}**\n"
        message += f"   `{url}`\n"

        if last_check:
            try:
                check_time = datetime.fromisoformat(last_check)
                time_str = check_time.strftime("%H:%M:%S")
                message += f"   Last check: {time_str}"
            except:
                message += f"   Last check: {last_check}"
        else:
            message += "   Last check: Never"

        if response_time is not None:
            message += f" | {response_time:.3f}s"

        message += "\n\n"

    return message

def format_uptime_message(url: str, stats: Dict[str, Any]) -> str:
    uptime = stats.get("uptime_percentage", 0)
    total_pings = stats.get("total_pings", 0)
    successful_pings = stats.get("successful_pings", 0)
    failed_pings = stats.get("failed_pings", 0)
    avg_response_time = stats.get("avg_response_time")

    if uptime >= 99:
        status_icon = "🟢"
    elif uptime >= 95:
        status_icon = "🟡"
    else:
        status_icon = "🔴"

    message = f"{status_icon} **{uptime}% Uptime**\n"
    message += f"   `{url}`\n"

    if total_pings > 0:
        message += f"   Checks: {successful_pings}✅ / {failed_pings}❌ (Total: {total_pings})\n"
        if avg_response_time is not None:
            message += f"   Avg Response: {avg_response_time:.3f}s\n"
    else:
        message += "   No ping data available\n"

    return message

def format_duration(seconds: float) -> str:
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    elif seconds < 86400:
        hours = seconds / 3600
        return f"{hours:.1f}h"
    else:
        days = seconds / 86400
        return f"{days:.1f}d"

def truncate_url(url: str, max_length: int = 50) -> str:
    if len(url) <= max_length:
        return url
    parsed = urlparse(url)
    domain = parsed.netloc
    if len(domain) < max_length - 3:
        return f"{domain}...{url[-(max_length - len(domain) - 3):]}"
    else:
        return url[:max_length - 3] + "..."

def get_status_emoji(status: str) -> str:
    status_emojis = {
        "online": "🟢",
        "offline": "🔴",
        "pending": "⏳",
        "unknown": "⚪"
    }
    return status_emojis.get(status.lower(), "⚪")

def parse_command_args(text: str, command: str) -> List[str]:
    if text.startswith(f"/{command}"):
        args_text = text[len(f"/{command}"):].strip()
        if args_text:
            return args_text.split()
    return []

def is_valid_http_status(status_code: int) -> bool:
    return 200 <= status_code < 400

def format_timestamp(timestamp_str: str, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    try:
        dt = datetime.fromisoformat(timestamp_str)
        return dt.strftime(format_str)
    except:
        return timestamp_str

def sanitize_url(url: str) -> str:
    return url.replace("_", "\\_").replace("*", "\\*").replace("[", "\\[").replace("]", "\\]")

def create_url_keyboard(urls: List[str], action_prefix: str):
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    keyboard = []
    for url in urls:
        display_url = truncate_url(url, 30)
        callback_data = f"{action_prefix}:{url}"
        if len(callback_data) > 64:
            import hashlib
            url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
            callback_data = f"{action_prefix}:{url_hash}"
        keyboard.append([InlineKeyboardButton(display_url, callback_data=callback_data)])
    return InlineKeyboardMarkup(keyboard)

def format_error_message(error: Exception, context: str = "") -> str:
    error_msg = "❌ **An error occurred**\n\n"
    if context:
        error_msg += f"**Context:** {context}\n"
    error_msg += f"**Error:** {str(error)}\n\n"
    error_msg += "Please try again or contact the administrator if the problem persists."
    return error_msg
