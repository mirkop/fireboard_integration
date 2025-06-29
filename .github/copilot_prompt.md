# GitHub Copilot Custom Prompt for FireBoard Cloud

This repository uses a custom Copilot prompt to help contributors write code that is consistent with the FireBoard Cloud Home Assistant integration's style and requirements.

## Copilot Prompt

- Use Home Assistant's best practices for custom integrations.
- Make code compatible with Home Assistant version 2025.1 and later.
- Prefer async methods and non-blocking I/O.
- Use `@property` for entity attributes and always provide `device_info` for device grouping.
- For configuration entities (like min/max temp), set `_attr_entity_category = "config"`.
- When a value is not set, display `--` instead of `None` or `Unknown`.
- Use clear, descriptive names for entities and unique IDs.
- Follow the structure and conventions already present in the codebase.
- Write concise, well-documented code and avoid unnecessary complexity.
- Ensure all new entities are properly associated with their parent device.
- Use `mdi:` icons for Home Assistant entities.
- Version numbers should be in the format `YYYY.MM.DD.HHMM` for commits.
- Zero pad the month and day in the version number if necessary.
- The version's `HHMM` is the *current* UTC hour and minute, zero-padded (24-hour format). Always use UTC, not your local time. For example, if the current UTC time is 08:25, use `0825`; if it is 20:32, use `2032`.
- Update the version number in the `hacs.json` and `manifest.json` files with each commit. Do not update this file.

## Example FireBoard JSON Files
- `json/device-real-time-temperature-data.jsonc` Contains real-time temperature data for FireBoard devices.
- `json/device-real-time-drive-data.jsonc` Contains real-time drive data for FireBoard devices.

## References
- [FireBoard Cloud API Documentation](https://docs.fireboard.io/app/api.html)
- [Home Assistant Developer Documentation](https://developers.home-assistant.io/)
- [Home Assistant Custom Integration Guide](https://developers.home-assistant.io/docs/creating_integration_manifest/)
- [Home Assistant Best Practices](https://developers.home-assistant.io/docs/integration_best_practices/)

## Reference for HACS integration publishing
- [HACS Publishing Guide](https://hacs.xyz/docs/publish/)
- [HACS Start Guide](https://hacs.xyz/docs/publish/start/)
- [HACS GitHub Action Guide](https://hacs.xyz/docs/publish/action/)
- [HACS Include Guide](https://hacs.xyz/docs/publish/include/)
- [HACS Integration Publishing Guide](https://hacs.xyz/docs/publish/integration/)

---

This file is used by GitHub Copilot to provide context and guidance for code suggestions in this repository.
