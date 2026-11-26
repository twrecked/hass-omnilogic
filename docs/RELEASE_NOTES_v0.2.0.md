# Release Notes — v0.2.0

Version `0.2.0` adds native ColorLogic light controls and fixes backyard relay control. Home Assistant can now control both without an AppDaemon bridge or virtual switches.

## What's Changed

- **ColorLogic lights:** Discover native on/off `light` entities. V1 lights turn on with Cloud White; V2 lights use Warm White at speed 4 and brightness 2. The entities do not expose adjustable brightness or effects.
- **Backyard relays:** Recognize `relayState` telemetry while retaining support for `switchState`. Use pool ID `0` for backyard relays and the actual body-of-water ID for pool-scoped relays.
- **State confirmation:** After Hayward accepts a command, Home Assistant displays the requested state while waiting for a fresh poll to confirm it. If confirmation times out, the entity falls back to the last reported state. ColorLogic turn-off allows up to 60 seconds; ColorLogic turn-on and relay commands allow up to 30 seconds. This prevents stale telemetry from immediately reversing the displayed state without changing how quickly the controller operates the lights.

## Upgrade and Migration

1. Update to `0.2.0` in HACS, or run `./scripts/install go /path/to/homeassistant/config`, then restart Home Assistant.
2. Test the new light and relay entities directly before changing automations. If an automation expects a `light` entity for a relay-controlled light, wrap the relay switch with Home Assistant's **Change device type of a switch** helper.
3. Update automations and dashboards to use the new entities. Once verified, disable the old AppDaemon bridge and retire any virtual entities that are no longer referenced.
