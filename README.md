# Hayward OmniLogic (Custom Component)

Custom component fork of the built-in Home Assistant [OmniLogic integration](https://www.home-assistant.io/integrations/omnilogic).

This custom integration overrides the core `omnilogic` component in Home Assistant to provide additional features and fixes ahead of upstream inclusion.

## Features & Additions

Compared to core Home Assistant OmniLogic:
* **Heater Binary Sensors**: Adds binary sensor entities (`heaterState`) for heater operation.
* **Instant Salt Level Sensor**: Adds instant salt level sensor support.
* **Temperature Sensor Fixes**: Handles negative temperature values appropriately.
* **Configurable Polling Interval**: Option to configure the polling interval from integration options.

## Installation

### Via HACS (Recommended)

1. In Home Assistant, open **HACS** > **Integrations**.
2. Click the three dots in the top right corner and select **Custom repositories**.
3. Add repository URL: `https://github.com/twrecked/hass-omnilogic`
4. Category: **Integration**
5. Click **Add**, then find **Hayward OmniLogic (Custom)** and click **Download**.
6. Restart Home Assistant.

### Manual Installation

1. Use the install script to copy the files to your Home Assistant config directory:
   ```bash
   ./scripts/install go <path_to_ha_config>
   ```
   *(Running `./scripts/install <path_to_ha_config>` without `go` performs a dry run).*
2. Restart Home Assistant.

## Keeping in Sync with Upstream

This repository tracks core Home Assistant's `homeassistant/components/omnilogic` component using a vendor `upstream` branch:
* `upstream`: Pristine mirror of core Home Assistant's `omnilogic` component.
* `main`: Active development branch with custom enhancements.

To pull in updates from core:
```bash
./scripts/sync-upstream.sh
git merge upstream
```
