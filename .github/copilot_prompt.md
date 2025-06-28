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
