from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from datetime import timedelta
import logging

_LOGGER = logging.getLogger(__name__)

class FireBoardCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, api_client, update_interval):
        super().__init__(
            hass,
            _LOGGER,
            name="FireBoard Data Coordinator",
            update_interval=timedelta(seconds=update_interval),
        )
        self.api = api_client
        self.devices = []
        self.channel_temps = {}
        self.drive_data = {}

    async def _async_update_data(self):
        try:
            self.devices = await self.api.async_get_devices()
            # Fetch temps and drive data for all devices
            self.channel_temps = {}
            self.drive_data = {}
            for device in self.devices:
                uuid = device.get("uuid")
                temps = await self.api.async_get_channel_temps(uuid)
                self.channel_temps[uuid] = temps
                drive = await self.api.async_get_drive_data(uuid)
                self.drive_data[uuid] = drive
            return {
                "devices": self.devices,
                "channel_temps": self.channel_temps,
                "drive_data": self.drive_data
            }
        except Exception as err:
            raise UpdateFailed(f"Error updating FireBoard data: {err}")
