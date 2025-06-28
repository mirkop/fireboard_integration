from homeassistant.helpers.entity import Entity
from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.components.number import NumberEntity
from .const import DOMAIN
from .coordinator import FireBoardCoordinator
import logging

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    api = hass.data[DOMAIN][entry.entry_id]
    update_interval = getattr(api, 'update_interval', 18)
    coordinator = FireBoardCoordinator(hass, api, update_interval)
    await coordinator.async_config_entry_first_refresh()
    entities = []
    try:
        for device in coordinator.devices:
            uuid = device.get("uuid")
            for channel in device.get("channels", []):
                entities.append(FireBoardChannelSensor(coordinator, device, channel))
            entities.append(FireBoardBatterySensor(coordinator, device))
    except Exception as e:
        _LOGGER.error("FireBoard async_setup_entry failed: %s", e)
    async_add_entities(entities)

class FireBoardChannelSensor(Entity):
    def __init__(self, coordinator, device, channel):
        self.coordinator = coordinator
        self._device = device
        self._channel = channel
        model = device.get("model")
        channel_label = channel.get("channel_label")
        channel_num = channel.get("channel")
        if model in ("FBX11", "FBX2", "FBX2D") and channel_label:
            self._attr_name = f"Ch {channel_num}: {channel_label}"
        else:
            self._attr_name = f"{device['title']} {channel_label or channel_num}"
        self._attr_unique_id = f"{device['uuid']}_ch{channel.get('id')}"
        self._degreetype = device.get("degreetype", 2)  # 1 = C, 2 = F

    @property
    def name(self):
        return self._attr_name

    @property
    def unique_id(self):
        return self._attr_unique_id

    @property
    def state(self):
        temps = self.coordinator.channel_temps.get(self._device["uuid"], {})
        value = temps.get(self._channel.get("channel"))
        if value is None:
            return "--"
        return value

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._device["uuid"])} ,
            "name": self._device["title"],
            "model": self._device["model"],
            "manufacturer": "FireBoard",
        }

    @property
    def extra_state_attributes(self):
        return {
            "channel_label": self._channel.get("channel_label"),
            "color_hex": self._channel.get("color_hex"),
            "enabled": self._channel.get("enabled"),
            "state_class": "measurement",
            "device_class": "temperature",
            "icon": "mdi:thermometer",
        }

    @property
    def state_class(self):
        return "measurement"

    @property
    def device_class(self):
        return "temperature"

    @property
    def icon(self):
        return "mdi:thermometer"

    @property
    def unit_of_measurement(self):
        return "°C" if self._degreetype == 1 else "°F"

    async def async_update(self):
        await self.coordinator.async_request_refresh()

class FireBoardBatterySensor(Entity):
    def __init__(self, coordinator, device):
        self.coordinator = coordinator
        self._device = device
        self._attr_name = f"{device['title']} Battery"
        self._attr_unique_id = f"{device['uuid']}_battery"

    @property
    def name(self):
        return self._attr_name

    @property
    def unique_id(self):
        return self._attr_unique_id

    @property
    def state(self):
        value = self._device.get("last_battery_reading")
        if value is None:
            return None
        try:
            percent = round(float(value) * 100, 1)
            return percent
        except Exception:
            return None

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._device["uuid"])} ,
            "name": self._device["title"],
            "model": self._device["model"],
            "manufacturer": "FireBoard",
        }

    @property
    def state_class(self):
        return "measurement"

    @property
    def unit_of_measurement(self):
        return "%"

    @property
    def device_class(self):
        return "battery"

    @property
    def icon(self):
        value = self.state
        if value is None:
            return "mdi:battery-unknown"
        try:
            value = int(value)
        except Exception:
            return "mdi:battery-unknown"
        if value >= 95:
            return "mdi:battery"
        elif value >= 90:
            return "mdi:battery-90"
        elif value >= 80:
            return "mdi:battery-80"
        elif value >= 70:
            return "mdi:battery-70"
        elif value >= 60:
            return "mdi:battery-60"
        elif value >= 50:
            return "mdi:battery-50"
        elif value >= 40:
            return "mdi:battery-40"
        elif value >= 30:
            return "mdi:battery-30"
        elif value >= 20:
            return "mdi:battery-20"
        elif value >= 10:
            return "mdi:battery-10"
        else:
            return "mdi:battery-outline"
