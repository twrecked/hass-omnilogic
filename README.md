# Hayward OmniLogic (Custom Component)

Custom component fork of the built-in Home Assistant [OmniLogic integration](https://www.home-assistant.io/integrations/omnilogic).

This custom integration overrides the core `omnilogic` component in Home Assistant to provide additional features and fixes ahead of upstream inclusion.

## Features & Additions

Compared to core Home Assistant OmniLogic:
* **Heater Binary Sensors**: Adds binary sensor entities (`heaterState`) for heater operation.
* **Instant Salt Level Sensor**: Adds instant salt level sensor support.
* **Temperature Sensor Fixes**: Handles negative temperature values appropriately.
* **Configurable Polling Interval**: Option to configure the polling interval from integration options.
* **Native Light Controls**: ColorLogic lights appear as on/off `light` entities. They turn on with Warm White (speed 4, brightness 2) on V2 hardware or Cloud White on V1 hardware. Relay-controlled lights remain `switch` entities.

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

## Polling and Light Confirmation

Set the idle polling interval under **Settings → Devices & services → OmniLogic → Configure**. Saving the options reloads the integration. Version `0.2.1` honors the saved interval; earlier releases could fall back to polling every 6 seconds even when a longer interval was configured.

After Hayward accepts a light or relay command, Home Assistant displays the requested state and asks for a refresh. If Hayward hasn't confirmed it yet, the integration shares follow-up polls about every 10 seconds, unless regular polling is already that frequent. These follow-ups stop when all pending commands are confirmed or time out. Turn-on allows 30 seconds; turn-off allows 60 seconds. Changes made directly in the Hayward app are picked up on the next poll.

See the [v0.2.1 release notes](docs/RELEASE_NOTES_v0.2.1.md) for upgrade and verification steps.

## Keeping in Sync with Upstream

This repository tracks core Home Assistant's `homeassistant/components/omnilogic` component using a vendor `upstream` branch:
* `upstream`: Pristine mirror of core Home Assistant's `omnilogic` component.
* `main`: Active development branch with custom enhancements.

To pull in updates from core:
```bash
./scripts/sync-upstream.sh
git merge upstream
```
