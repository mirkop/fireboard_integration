from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    api = hass.data[DOMAIN][entry.entry_id]
    coordinator = hass.data[DOMAIN][f"coordinator_{entry.entry_id}"]
    entities = []
    for device in coordinator.devices:
        hardware_id = device.get("hardware_id")
        switch = FireBoardPollingSwitch(coordinator, device, hardware_id)
        coordinator.register_switch_entity(hardware_id, switch)
        entities.append(switch)
    async_add_entities(entities)

class FireBoardPollingSwitch(CoordinatorEntity, SwitchEntity):
    def __init__(self, coordinator, device, hardware_id):
        super().__init__(coordinator)
        self._device = device
        self._hardware_id = hardware_id
        self._attr_name = "FireBoard Updates"
        self.entity_id = f"switch.fireboard_updates_{hardware_id}"
        self._attr_unique_id = f"{device['uuid']}_polling_switch"
        # Default to polling enabled
        self._is_on = True

    @property
    def is_on(self):
        return self._is_on

    async def async_turn_on(self, **kwargs):
        self._is_on = True
        self.coordinator.set_polling(self._hardware_id, True)
        await self.coordinator.async_request_refresh()
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        self._is_on = False
        self.coordinator.set_polling(self._hardware_id, False)
        self.async_write_ha_state()

    def auto_turn_off(self):
        self._is_on = False
        self.async_write_ha_state()

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._device["uuid"], self._hardware_id)},
            "name": self._device["title"],
            "model": self._device["model"],
            "manufacturer": "FireBoard",
        }
