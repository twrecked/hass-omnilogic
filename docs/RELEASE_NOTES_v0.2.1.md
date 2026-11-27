# Release Notes — v0.2.1

Version `0.2.1` honors the configured idle polling interval while keeping light and relay state responsive after commands.

## What's Changed

- **Polling options:** Read the interval saved in Home Assistant's integration options. Saving changes reloads OmniLogic so the new interval takes effect without restarting Home Assistant.
- **Configure dialog:** Fix the HTTP 500 error on Home Assistant versions that expose the options flow's config entry as read-only.
- **Command follow-up polling:** After Hayward accepts a light or relay command, request a refresh and, if needed, share follow-up polls about every 10 seconds until confirmation or timeout. No extra follow-ups are scheduled if regular polling is already that frequent.
- **Slow turn-off:** Relays now have the same 60-second turn-off confirmation window as ColorLogic lights. Both still allow 30 seconds for turn-on. If the command is not confirmed in time, Home Assistant falls back to the last reported state.

## Upgrade and Verify

1. Update to `0.2.1` in HACS, or run `./scripts/install go /path/to/homeassistant/config`, then restart Home Assistant.
2. Open **Settings → Devices & services → OmniLogic → Configure** and verify the saved polling interval. A longer interval that was previously ignored will now take effect.
3. Test the light and relay controls. Idle refreshes should follow the configured interval, with temporary follow-up polls only while a command awaits confirmation.

No entity renames or automation changes are required when upgrading from `0.2.0`.
