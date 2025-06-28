import aiohttp
import async_timeout
from .const import LOGIN_URL, API_BASE, USER_AGENT
import logging
from datetime import datetime, timedelta

_LOGGER = logging.getLogger(__name__)

API_RATE_LIMIT = 200  # max calls per hour
MIN_UPDATE_INTERVAL = int(3600 / API_RATE_LIMIT)  # seconds

class FireBoardApiClient:
    def __init__(self, username, password, session, update_interval=None):
        self._username = username
        self._password = password
        self._session = session
        self._token = None
        self._call_times = []  # track API call timestamps
        # Enforce minimum update interval
        if update_interval is None or update_interval < MIN_UPDATE_INTERVAL:
            self.update_interval = MIN_UPDATE_INTERVAL
        else:
            self.update_interval = update_interval
        self._blocked_until = None

    async def _rate_limit_check(self):
        now = datetime.utcnow()
        # Remove calls older than 1 hour
        self._call_times = [t for t in self._call_times if (now - t).total_seconds() < 3600]
        if self._blocked_until and now < self._blocked_until:
            raise RuntimeError(f"API rate limit exceeded. Blocked until {self._blocked_until}.")
        if len(self._call_times) >= API_RATE_LIMIT:
            self._blocked_until = now + timedelta(minutes=30)
            _LOGGER.error("FireBoard API rate limit exceeded. Blocking calls for 30 minutes.")
            raise RuntimeError(f"API rate limit exceeded. Blocked until {self._blocked_until}.")
        self._call_times.append(now)

    async def async_login(self):
        await self._rate_limit_check()
        headers = {
            "Content-Type": "application/json",
            "User-Agent": USER_AGENT,
        }
        payload = {
            "username": self._username,
            "password": self._password,
        }
        try:
            async with async_timeout.timeout(10):
                async with self._session.post(LOGIN_URL, json=payload, headers=headers) as resp:
                    resp.raise_for_status()
                    data = await resp.json()
                    self._token = data["key"]
        except Exception as e:
            _LOGGER.error("FireBoard login failed: %s", e)
            raise

    def get_auth_headers(self):
        if not self._token:
            raise RuntimeError("Not authenticated")
        return {
            "Authorization": f"Token {self._token}",
            "User-Agent": USER_AGENT,
        }

    async def async_get_devices(self):
        await self._rate_limit_check()
        if not self._token:
            await self.async_login()
        headers = self.get_auth_headers()
        url = "https://fireboard.io/api/v1/devices.json"
        try:
            async with async_timeout.timeout(10):
                async with self._session.get(url, headers=headers) as resp:
                    resp.raise_for_status()
                    return await resp.json()
        except Exception as e:
            _LOGGER.error("FireBoard get_devices failed: %s", e)
            return []

    async def async_discover_entities(self):
        try:
            devices = await self.async_get_devices()
        except Exception as e:
            _LOGGER.error("FireBoard discover_entities failed: %s", e)
            return []
        entities = []
        for device in devices:
            device_info = {
                "uuid": device.get("uuid"),
                "id": device.get("id"),
                "title": device.get("title"),
                "model": device.get("model_name", device.get("model")),
                "hardware_id": device.get("hardware_id"),
                "degreetype": device.get("degreetype"),
            }
            for channel in device.get("channels", []):
                entity = {
                    "device": device_info,
                    "channel_id": channel.get("id"),
                    "channel_label": channel.get("channel_label"),
                    "channel_number": channel.get("channel"),
                    "enabled": channel.get("enabled", True),
                    "color_hex": channel.get("color_hex"),
                }
                entities.append(entity)
        return entities

    async def async_get_channel_temps(self, device_uuid):
        await self._rate_limit_check()
        if not self._token:
            await self.async_login()
        headers = self.get_auth_headers()
        url = f"https://fireboard.io/api/v1/devices/{device_uuid}/temps.json"
        try:
            async with async_timeout.timeout(10):
                async with self._session.get(url, headers=headers) as resp:
                    resp.raise_for_status()
                    data = await resp.json()
                    return {ch["channel"]: ch.get("temp") for ch in data}
        except Exception as e:
            _LOGGER.error("FireBoard get_channel_temps failed for %s: %s", device_uuid, e)
            return {}

    async def async_get_drive_data(self, device_uuid):
        await self._rate_limit_check()
        if not self._token:
            await self.async_login()
        headers = self.get_auth_headers()
        url = f"https://fireboard.io/api/v1/devices/{device_uuid}/drivelog.json"
        try:
            async with async_timeout.timeout(10):
                async with self._session.get(url, headers=headers) as resp:
                    resp.raise_for_status()
                    data = await resp.json()
                    return data if data else None
        except Exception as e:
            _LOGGER.error("FireBoard get_drive_data failed for %s: %s", device_uuid, e)
            return None
