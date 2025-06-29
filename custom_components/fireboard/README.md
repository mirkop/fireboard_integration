# FireBoard Home Assistant Integration

## Features
- UI-based config flow for credentials and update interval
- Sensors for each device channel (temperature)
- Sensors for battery (as percentage), WiFi signal (dBm), and onboard temperature (°F or °C)
- Min/Max temperature configuration entities for each channel (shown in device configuration section)
- Session sensors: total session count, last session info (with attributes), and last session chart data
- Real-time drive data sensors: drive percent, setpoint, grill lid (open/closed), control channel
- Channel temperature entity_id uses `ch_<channel>_<hardware_id>` for uniqueness
- Device info includes hardware ID for all entities
- Rate limit enforcement (200 calls/hour, minimum 18s update interval)
- Error handling and diagnostics
- Localization support (English)
- Home Assistant services:
  - `fireboard.refresh`: Refresh device/channel data
  - `fireboard.refresh_sessions`: Refresh session data
  - `fireboard.refresh_last_session_chart`: Refresh last session chart data
- All sensors and services are robust to API/network errors and respect FireBoard Cloud API best practices
- All entities are grouped with their parent device for a clean UI
- Compatible with Home Assistant 2021.6 and later

## Installation
1. Copy the `fireboard` folder to your `custom_components` directory.
2. Restart Home Assistant.
3. Add the integration via the UI (Configuration > Devices & Services > Add Integration > FireBoard).

## Configuration Options
- Username and password for FireBoard Cloud
- Update interval (minimum 18 seconds, enforced by API rate limit)

## Entities Provided
- **Channel Sensors:** One per channel, shows live temperature (°F or °C), entity_id is `ch_<channel>_<hardware_id>`
- **Min/Max Temp Numbers:** One pair per channel, shown as configuration entities, grouped with device
- **Battery Sensor:** One per device, shows last battery reading as percentage (%)
- **WiFi Signal Sensor:** One per device, shows WiFi signal level (dBm)
- **Onboard Temperature Sensor:** One per device, shows onboard temperature (°F or °C)
- **Session Count Sensor:** Shows total number of sessions
- **Last Session Sensor:** Shows most recent session info (title, duration, times, description, devices)
- **Last Session Chart Sensor:** Shows number of chart data points and exposes chart data as attributes
- **Drive Percent Sensor:** Shows current drive fan percent
- **Drive Setpoint Sensor:** Shows current drive setpoint
- **Grill Lid Sensor:** Shows grill lid state (Open/Closed)
- **Control Channel Sensor:** Shows which channel is controlling the drive

## Entity Attributes
- **Battery Sensor:**
  - `state_class: measurement`
  - `unit_of_measurement: %`
  - `device_class: battery`
  - `icon`: dynamic based on charge level
- **WiFi Signal Sensor:**
  - `state_class: measurement`
  - `unit_of_measurement: dBm`
  - `device_class: signal_strength`
  - `icon: mdi:wifi`
- **Onboard Temperature Sensor:**
  - `state_class: measurement`
  - `unit_of_measurement: °F` or `°C`
  - `device_class: temperature`
  - `icon: mdi:thermometer`
- **Min/Max Temp Numbers:**
  - Shown as configuration entities in the device page
  - Display `--` if unset
  - Grouped with their parent device

## Services Provided
- `fireboard.refresh`: Refresh all device/channel data
- `fireboard.refresh_sessions`: Refresh session data
- `fireboard.refresh_last_session_chart`: Refresh last session chart data

## Best Practices
- Do not set update interval below 18 seconds (API rate limit)
- If you see errors about rate limits, wait 30 minutes before retrying
- Spread out queries evenly to avoid traffic spikes
- Use Home Assistant's best practices for custom integrations
- All new entities should be associated with their parent device

## Troubleshooting
- Check Home Assistant logs for error messages
- Ensure your FireBoard credentials are correct
- If you change your password, reconfigure the integration
- If you hit the API rate limit, wait 30 minutes before retrying

## Contributing
Pull requests and issues are welcome!

## License
Apache License 2.0. See [LICENSE](../LICENSE) for details.
