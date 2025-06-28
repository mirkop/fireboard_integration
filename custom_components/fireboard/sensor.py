from homeassistant.helpers.entity import Entity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
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
            # Add drive data sensors if drive data is present
            drive_data = coordinator.drive_data.get(uuid)
            if drive_data:
                entities.append(FireBoardDrivePercentSensor(coordinator, device))
                entities.append(FireBoardDriveSetpointSensor(coordinator, device))
                entities.append(FireBoardDriveLidPausedSensor(coordinator, device))
                entities.append(FireBoardDriveControlChannelSensor(coordinator, device))
    except Exception as e:
        _LOGGER.error("FireBoard async_setup_entry failed: %s", e)
    async_add_entities(entities)

class FireBoardChannelSensor(CoordinatorEntity, Entity):
    def __init__(self, coordinator, device, channel):
        super().__init__(coordinator)
        self.coordinator = coordinator
        self._device = device
        self._channel = channel
        model = device.get("model")
        channel_label = channel.get("channel_label")
        channel_num = channel.get("channel")
        hardware_id = device.get("hardware_id")
        if model in ("FBX11", "FBX2", "FBX2D") and channel_label:
            self._attr_name = f"Ch {channel_num}: {channel_label}"
        else:
            self._attr_name = f"{device['title']} {channel_label or channel_num}"
        # entity_id: ch_<channel>_<hardware_id>
        self.entity_id = f"sensor.ch_{channel_num}_{hardware_id}"
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
            "identifiers": {(DOMAIN, self._device["uuid"], self._device.get("hardware_id"))},
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

class FireBoardBatterySensor(CoordinatorEntity, Entity):
    def __init__(self, coordinator, device):
        super().__init__(coordinator)
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
            "identifiers": {(DOMAIN, self._device["uuid"], self._device.get("hardware_id"))} ,
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

class FireBoardDrivePercentSensor(CoordinatorEntity, Entity):
    def __init__(self, coordinator, device):
        super().__init__(coordinator)
        self.coordinator = coordinator
        self._device = device
        self._attr_name = f"{device['title']} Drive %"
        self._attr_unique_id = f"{device['uuid']}_drive_per"

    @property
    def name(self):
        return self._attr_name

    @property
    def unique_id(self):
        return self._attr_unique_id

    @property
    def state(self):
        uuid = self._device["uuid"]
        drive_data = self.coordinator.drive_data.get(uuid) or {}
        value = drive_data.get("driveper")
        if value is None:
            return "--"
        try:
            percent = round(float(value) * 100, 1)
            if percent == 0:
                return "--"
            return percent
        except Exception:
            return value

    @property
    def unit_of_measurement(self):
        return "%"

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._device["uuid"], self._device.get("hardware_id"))} ,
            "name": self._device["title"],
            "model": self._device["model"],
            "manufacturer": "FireBoard",
        }

    @property
    def icon(self):
        return "mdi:fan"

class FireBoardDriveSetpointSensor(CoordinatorEntity, Entity):
    def __init__(self, coordinator, device):
        super().__init__(coordinator)
        self.coordinator = coordinator
        self._device = device
        self._attr_name = f"{device['title']} Drive Setpoint"
        self._attr_unique_id = f"{device['uuid']}_drive_setpoint"

    @property
    def name(self):
        return self._attr_name

    @property
    def unique_id(self):
        return self._attr_unique_id

    @property
    def state(self):
        uuid = self._device["uuid"]
        drive_data = self.coordinator.drive_data.get(uuid) or {}
        value = drive_data.get("setpoint")
        if value is None or value == 0:
            return "--"
        return value

    @property
    def unit_of_measurement(self):
        degreetype = self._device.get("degreetype", 2)
        return "°C" if degreetype == 1 else "°F"

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._device["uuid"], self._device.get("hardware_id"))} ,
            "name": self._device["title"],
            "model": self._device["model"],
            "manufacturer": "FireBoard",
        }

    @property
    def icon(self):
        return "mdi:fan"

class FireBoardDriveLidPausedSensor(CoordinatorEntity, Entity):
    def __init__(self, coordinator, device):
        super().__init__(coordinator)
        self.coordinator = coordinator
        self._device = device
        self._attr_name = f"{device['title']} Grill Lid"
        self._attr_unique_id = f"{device['uuid']}_drive_lidpaused"

    @property
    def name(self):
        return self._attr_name

    @property
    def unique_id(self):
        return self._attr_unique_id

    @property
    def state(self):
        uuid = self._device["uuid"]
        drive_data = self.coordinator.drive_data.get(uuid) or {}
        value = drive_data.get("lidpaused")
        if value is None:
            return "--"
        return "Open" if value else "Closed"

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._device["uuid"], self._device.get("hardware_id"))} ,
            "name": self._device["title"],
            "model": self._device["model"],
            "manufacturer": "FireBoard",
        }

    @property
    def icon(self):
        uuid = self._device["uuid"]
        drive_data = self.coordinator.drive_data.get(uuid) or {}
        value = drive_data.get("lidpaused")
        if value is True:
            return "mdi:grill-outline"
        return "mdi:grill"

class FireBoardDriveControlChannelSensor(CoordinatorEntity, Entity):
    def __init__(self, coordinator, device):
        super().__init__(coordinator)
        self.coordinator = coordinator
        self._device = device
        self._attr_name = f"{device['title']} Control Channel"
        self._attr_unique_id = f"{device['uuid']}_drive_control_channel"

    @property
    def name(self):
        return self._attr_name

    @property
    def unique_id(self):
        return self._attr_unique_id

    @property
    def state(self):
        uuid = self._device["uuid"]
        drive_data = self.coordinator.drive_data.get(uuid) or {}
        value = drive_data.get("tiedchannel")
        if value is None:
            return "--"
        return f"Ch {value}"

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._device["uuid"], self._device.get("hardware_id"))} ,
            "name": self._device["title"],
            "model": self._device["model"],
            "manufacturer": "FireBoard",
        }

    @property
    def icon(self):
        return "mdi:link-variant"
