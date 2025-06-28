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
        self._polling_state = {}  # hardware_id: bool
        self._empty_temp_count = {}  # hardware_id: int
        self._switch_entities = {}  # hardware_id: switch entity

    def set_polling(self, hardware_id, enabled):
        self._polling_state[hardware_id] = enabled
        if enabled:
            self._empty_temp_count[hardware_id] = 0

    def is_polling(self, hardware_id):
        # Default to True if not set
        return self._polling_state.get(hardware_id, True)

    def register_switch_entity(self, hardware_id, switch_entity):
        self._switch_entities[hardware_id] = switch_entity

    async def _async_update_data(self):
        try:
            self.devices = await self.api.async_get_devices()
            # Fetch temps and drive data for all devices
            self.channel_temps = {}
            self.drive_data = {}
            for device in self.devices:
                uuid = device.get("uuid")
                hardware_id = device.get("hardware_id")
                if not self.is_polling(hardware_id):
                    continue  # Skip polling for this device
                temps = await self.api.async_get_channel_temps(uuid)
                self.channel_temps[uuid] = temps
                drive = await self.api.async_get_drive_data(uuid)
                self.drive_data[uuid] = drive
                # Check for empty temp data
                if not temps:
                    self._empty_temp_count[hardware_id] = self._empty_temp_count.get(hardware_id, 0) + 1
                    if self._empty_temp_count[hardware_id] >= 3:
                        self.set_polling(hardware_id, False)
                        # Notify switch entity to turn off
                        switch = self._switch_entities.get(hardware_id)
                        if switch:
                            switch.auto_turn_off()
                else:
                    self._empty_temp_count[hardware_id] = 0
            return {
                "devices": self.devices,
                "channel_temps": self.channel_temps,
                "drive_data": self.drive_data
            }
        except Exception as err:
            raise UpdateFailed(f"Error updating FireBoard data: {err}")
