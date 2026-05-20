"""
URL monitoring service with keep-alive pings and status tracking
"""

import asyncio
import aiohttp
import logging
from datetime import datetime
from typing import Optional, Dict, Any
from data_manager import DataManager

logger = logging.getLogger(__name__)

class URLMonitor:
    def __init__(self, ping_interval: int = 60, request_timeout: int = 30):
        self.ping_interval = ping_interval
        self.request_timeout = request_timeout
        self.data_manager = DataManager()
        self.is_running = False
        self.bot_instance = None
        self.admin_chat_id = None

    def set_bot_instance(self, bot):
        self.bot_instance = bot

    def set_admin_chat_id(self, chat_id):
        self.admin_chat_id = chat_id

    async def ping_url(self, url: str) -> Dict[str, Any]:
        start_time = datetime.now()
        try:
            timeout = aiohttp.ClientTimeout(total=self.request_timeout)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url, allow_redirects=True) as response:
                    end_time = datetime.now()
                    response_time = (end_time - start_time).total_seconds()
                    success = 200 <= response.status < 400
                    return {
                        "url": url,
                        "status_code": response.status,
                        "response_time": response_time,
                        "success": success,
                        "timestamp": start_time.isoformat(),
                        "error": None
                    }
        except asyncio.TimeoutError:
            end_time = datetime.now()
            response_time = (end_time - start_time).total_seconds()
            return {
                "url": url,
                "status_code": 408,
                "response_time": response_time,
                "success": False,
                "timestamp": start_time.isoformat(),
                "error": "Request timeout"
            }
        except Exception as e:
            end_time = datetime.now()
            response_time = (end_time - start_time).total_seconds()
            return {
                "url": url,
                "status_code": 0,
                "response_time": response_time,
                "success": False,
                "timestamp": start_time.isoformat(),
                "error": str(e)
            }

    async def ping_all_urls(self) -> Dict[str, Dict[str, Any]]:
        url_to_admin = self.data_manager.get_all_urls()

        if not url_to_admin:
            return {}

        ping_tasks = [self.ping_url(url) for url in url_to_admin.keys()]
        results = await asyncio.gather(*ping_tasks, return_exceptions=True)

        ping_results = {}
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Ping task failed: {result}")
                continue

            url = result["url"]
            ping_results[url] = result
            admin_id = url_to_admin[url]

            self.data_manager.update_url_status(
                url=url,
                admin_chat_id=admin_id,
                status_code=result["status_code"],
                response_time=result["response_time"],
                success=result["success"]
            )

            if not result["success"]:
                await self._send_alert(result, admin_id)

        return ping_results

    async def ping_admin_urls(self, admin_chat_id: str) -> Dict[str, Dict[str, Any]]:
        admin_urls = self.data_manager.get_urls(admin_chat_id)

        if not admin_urls:
            return {}

        ping_tasks = [self.ping_url(url) for url in admin_urls.keys()]
        results = await asyncio.gather(*ping_tasks, return_exceptions=True)

        ping_results = {}
        for result in results:
            if isinstance(result, Exception):
                continue

            url = result["url"]
            ping_results[url] = result

            self.data_manager.update_url_status(
                url=url,
                admin_chat_id=admin_chat_id,
                status_code=result["status_code"],
                response_time=result["response_time"],
                success=result["success"]
            )

            if not result["success"]:
                await self._send_alert(result, admin_chat_id)

        return ping_results

    async def _send_alert(self, ping_result: Dict[str, Any], admin_chat_id: str):
        if not self.bot_instance:
            return

        url = ping_result["url"]
        status_code = ping_result["status_code"]
        error = ping_result.get("error", "Unknown error")
        response_time = ping_result["response_time"]

        alert_msg = f"🚨 **URL DOWN ALERT** 🚨\n\n"
        alert_msg += f"**URL:** `{url}`\n"
        alert_msg += f"**Status Code:** {status_code}\n"
        alert_msg += f"**Response Time:** {response_time:.3f}s\n"
        alert_msg += f"**Error:** {error}\n"
        alert_msg += f"**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        alert_msg += "Please check the URL status immediately."

        try:
            await self.bot_instance.send_message(
                chat_id=admin_chat_id,
                text=alert_msg,
                parse_mode='Markdown'
            )
        except Exception as e:
            logger.error(f"Failed to send alert for {url} to admin {admin_chat_id}: {e}")

    def get_monitoring_status(self) -> Dict[str, Any]:
        urls = self.data_manager.get_all_urls()
        return {
            "is_running": self.is_running,
            "total_urls": len(urls),
            "ping_interval": self.ping_interval,
            "request_timeout": self.request_timeout,
            "urls": {}
        }

    def add_url(self, url: str, admin_chat_id: str) -> bool:
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        return self.data_manager.add_url(url, admin_chat_id)

    def remove_url(self, url: str, admin_chat_id: str) -> bool:
        return self.data_manager.remove_url(url, admin_chat_id)

    def get_urls(self, admin_chat_id: str) -> Dict[str, Dict[str, Any]]:
        return self.data_manager.get_urls(admin_chat_id)

    def get_uptime_stats(self, url: str, admin_chat_id: str, hours: int = 24) -> Dict[str, Any]:
        return self.data_manager.get_uptime_stats(url, admin_chat_id, hours)
