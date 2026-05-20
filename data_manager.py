"""
Data persistence manager for URL monitoring data
Vercel-compatible version - uses /tmp for storage
"""

import json
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

DATA_DIR = "/tmp"

class DataManager:
    def __init__(self, data_file: str = None):
        if data_file is None:
            data_file = os.path.join(DATA_DIR, "urls_data.json")
        self.data_file = data_file
        os.makedirs(DATA_DIR, exist_ok=True)
        self.data = self._load_data()

    def _load_data(self) -> Dict[str, Any]:
        default_data = {
            "admin_data": {},
            "urls": {},
            "ping_history": {},
            "downtime_incidents": {}
        }

        if not os.path.exists(self.data_file):
            self._save_data(default_data)
            return default_data

        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for key in default_data:
                    if key not in data:
                        data[key] = default_data[key]
                data = self._migrate_legacy_data(data)
                return data
        except (json.JSONDecodeError, FileNotFoundError) as e:
            logger.error(f"Error loading data file: {e}")
            self._save_data(default_data)
            return default_data

    def _save_data(self, data: Optional[Dict[str, Any]] = None):
        try:
            os.makedirs(DATA_DIR, exist_ok=True)
            data_to_save = data if data is not None else self.data
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data_to_save, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving data: {e}")

    def _migrate_legacy_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        if "admin_data" not in data:
            data["admin_data"] = {}

        if data.get("urls") or data.get("ping_history") or data.get("downtime_incidents"):
            primary_admin_id = str(os.getenv("ADMIN_CHAT_ID", "1691680798"))

            if primary_admin_id not in data["admin_data"]:
                data["admin_data"][primary_admin_id] = {
                    "urls": data.get("urls", {}),
                    "ping_history": data.get("ping_history", {}),
                    "downtime_incidents": data.get("downtime_incidents", {})
                }

            data["urls"] = {}
            data["ping_history"] = {}
            data["downtime_incidents"] = {}
            self._save_data(data)

        return data

    def _ensure_admin_data(self, admin_chat_id: str):
        if admin_chat_id not in self.data["admin_data"]:
            self.data["admin_data"][admin_chat_id] = {
                "urls": {},
                "ping_history": {},
                "downtime_incidents": {}
            }

    def add_url(self, url: str, admin_chat_id: str) -> bool:
        self._ensure_admin_data(admin_chat_id)
        admin_data = self.data["admin_data"][admin_chat_id]

        admin_data["urls"][url] = {
            "added_at": datetime.now().isoformat(),
            "last_check": None,
            "status": "pending",
            "response_time": None
        }

        if url not in admin_data["ping_history"]:
            admin_data["ping_history"][url] = []

        if url not in admin_data["downtime_incidents"]:
            admin_data["downtime_incidents"][url] = []

        self._save_data()
        return True

    def remove_url(self, url: str, admin_chat_id: str) -> bool:
        self._ensure_admin_data(admin_chat_id)
        admin_data = self.data["admin_data"][admin_chat_id]

        if url not in admin_data["urls"]:
            return False

        del admin_data["urls"][url]

        if url in admin_data["ping_history"]:
            del admin_data["ping_history"][url]

        if url in admin_data["downtime_incidents"]:
            del admin_data["downtime_incidents"][url]

        self._save_data()
        return True

    def get_urls(self, admin_chat_id: str) -> Dict[str, Dict[str, Any]]:
        self._ensure_admin_data(admin_chat_id)
        return self.data["admin_data"][admin_chat_id]["urls"].copy()

    def get_all_urls(self) -> Dict[str, str]:
        all_urls = {}
        for admin_id, admin_data in self.data["admin_data"].items():
            for url in admin_data["urls"]:
                all_urls[url] = admin_id
        return all_urls

    def update_url_status(self, url: str, admin_chat_id: str, status_code: int, response_time: float, success: bool):
        self._ensure_admin_data(admin_chat_id)
        admin_data = self.data["admin_data"][admin_chat_id]

        if url not in admin_data["urls"]:
            return

        now = datetime.now()

        admin_data["urls"][url].update({
            "last_check": now.isoformat(),
            "status": "online" if success else "offline",
            "response_time": response_time
        })

        ping_record = {
            "timestamp": now.isoformat(),
            "status_code": status_code,
            "response_time": response_time,
            "success": success
        }

        admin_data["ping_history"][url].append(ping_record)

        if len(admin_data["ping_history"][url]) > 1000:
            admin_data["ping_history"][url] = admin_data["ping_history"][url][-1000:]

        self._update_downtime_incidents(url, admin_chat_id, success, now)
        self._save_data()

    def _update_downtime_incidents(self, url: str, admin_chat_id: str, success: bool, timestamp: datetime):
        admin_data = self.data["admin_data"][admin_chat_id]
        incidents = admin_data["downtime_incidents"][url]

        if not success:
            if not incidents or (incidents[-1].get("end_time") is not None):
                incidents.append({
                    "start_time": timestamp.isoformat(),
                    "end_time": None,
                    "duration": None
                })
        else:
            if incidents and incidents[-1].get("end_time") is None:
                start_time = datetime.fromisoformat(incidents[-1]["start_time"])
                duration = (timestamp - start_time).total_seconds()
                incidents[-1].update({
                    "end_time": timestamp.isoformat(),
                    "duration": duration
                })

    def get_uptime_stats(self, url: str, admin_chat_id: str, hours: int = 24) -> Dict[str, Any]:
        self._ensure_admin_data(admin_chat_id)
        admin_data = self.data["admin_data"][admin_chat_id]

        if url not in admin_data.get("ping_history", {}):
            return {"uptime_percentage": 0, "total_pings": 0, "successful_pings": 0}

        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_pings = [
            ping for ping in admin_data["ping_history"][url]
            if datetime.fromisoformat(ping["timestamp"]) > cutoff_time
        ]

        if not recent_pings:
            return {"uptime_percentage": 0, "total_pings": 0, "successful_pings": 0}

        total_pings = len(recent_pings)
        successful_pings = sum(1 for ping in recent_pings if ping["success"])
        uptime_percentage = (successful_pings / total_pings) * 100

        successful_response_times = [
            ping["response_time"] for ping in recent_pings
            if ping["success"] and ping["response_time"] is not None
        ]
        avg_response_time = (
            sum(successful_response_times) / len(successful_response_times)
            if successful_response_times else 0
        )

        return {
            "uptime_percentage": round(uptime_percentage, 2),
            "total_pings": total_pings,
            "successful_pings": successful_pings,
            "failed_pings": total_pings - successful_pings,
            "avg_response_time": round(avg_response_time, 3) if avg_response_time else None
        }

    def get_recent_incidents(self, url: str, admin_chat_id: str, hours: int = 24) -> List[Dict[str, Any]]:
        self._ensure_admin_data(admin_chat_id)
        admin_data = self.data["admin_data"][admin_chat_id]

        if url not in admin_data.get("downtime_incidents", {}):
            return []

        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_incidents = []

        for incident in admin_data["downtime_incidents"][url]:
            start_time = datetime.fromisoformat(incident["start_time"])
            if start_time > cutoff_time:
                recent_incidents.append(incident)

        return recent_incidents
