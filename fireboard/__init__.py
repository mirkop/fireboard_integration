from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from .const import DOMAIN, CONF_USERNAME, CONF_PASSWORD
from .api import FireBoardApiClient

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the FireBoard component from configuration.yaml."""
    hass.data.setdefault(DOMAIN, {})
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up FireBoard from a config entry."""
    session = async_get_clientsession(hass)
    api = FireBoardApiClient(
        entry.data[CONF_USERNAME],
        entry.data[CONF_PASSWORD],
        session,
    )
    hass.data[DOMAIN][entry.entry_id] = api
    # Forward setup to sensor platform (use correct method for recent Home Assistant)
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    await hass.config_entries.async_forward_entry_unload(entry, "sensor")
    hass.data[DOMAIN].pop(entry.entry_id)
    return True
