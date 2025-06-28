def async_setup_services(hass, api):
    """Register FireBoard services."""
    async def async_refresh_service(call):
        await api.async_get_devices()
        # Optionally refresh all sensors
    hass.services.async_register(
        "fireboard", "refresh", async_refresh_service
    )
