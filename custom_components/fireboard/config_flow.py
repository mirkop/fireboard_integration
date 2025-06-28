import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.const import CONF_USERNAME, CONF_PASSWORD
from .const import DOMAIN

DATA_SCHEMA = vol.Schema({
    vol.Required(CONF_USERNAME): str,
    vol.Required(CONF_PASSWORD): str,
    vol.Optional("update_interval", default=18): vol.All(vol.Coerce(int), vol.Range(min=18)),
})

class FireBoardConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            # Validate credentials
            from homeassistant.helpers.aiohttp_client import async_get_clientsession
            from .api import FireBoardApiClient
            session = async_get_clientsession(self.hass)
            api = FireBoardApiClient(
                user_input[CONF_USERNAME],
                user_input[CONF_PASSWORD],
                session,
                user_input.get("update_interval", 18),
            )
            try:
                await api.async_login()
                return self.async_create_entry(title=user_input[CONF_USERNAME], data=user_input)
            except Exception:
                errors["base"] = "auth"
        return self.async_show_form(step_id="user", data_schema=DATA_SCHEMA, errors=errors)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return FireBoardOptionsFlowHandler(config_entry)

class FireBoardOptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        errors = {}
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)
        options_schema = vol.Schema({
            vol.Optional("update_interval", default=self.config_entry.options.get("update_interval", 18)): vol.All(vol.Coerce(int), vol.Range(min=18)),
        })
        return self.async_show_form(step_id="init", data_schema=options_schema, errors=errors)
