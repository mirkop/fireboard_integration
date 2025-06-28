def async_get_diagnostics(hass, config_entry):
    api = hass.data["fireboard"][config_entry.entry_id]
    return {
        "update_interval": api.update_interval,
        "last_api_calls": [str(t) for t in getattr(api, '_call_times', [])],
        "blocked_until": str(getattr(api, '_blocked_until', None)),
    }
