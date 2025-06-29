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
    # Set up coordinator and store for switch platform
    from .coordinator import FireBoardCoordinator
    update_interval = getattr(api, 'update_interval', 18)
    coordinator = FireBoardCoordinator(hass, api, update_interval)
    hass.data[DOMAIN][f"coordinator_{entry.entry_id}"] = coordinator
    await coordinator.async_config_entry_first_refresh()
    # Forward setup to sensor and switch platforms (plural)
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor", "switch"])
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    await hass.config_entries.async_forward_entry_unload(entry, "sensor")
    await hass.config_entries.async_forward_entry_unload(entry, "switch")
    hass.data[DOMAIN].pop(entry.entry_id)
    hass.data[DOMAIN].pop(f"coordinator_{entry.entry_id}", None)
    return True
