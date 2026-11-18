# Release Notes — v0.1.1

Version `0.1.1` delivers critical reliability fixes for cloud authentication recovery, updates the underlying library, and modernizes service and sensor implementations to align with recent Home Assistant core standards.

---

## What's Changed

### 1. Automatic Token Re-login Recovery
* Fixed an issue where expired Hayward cloud session tokens caused all entities to remain permanently in an `Unavailable` state until an integration reload or Home Assistant restart.
* The coordinator now immediately clears expired tokens on update failure, allowing the next scheduled poll to seamlessly re-authenticate with Hayward.

### 2. Dependency Update
* Bumped underlying `omnilogic` Python library requirement from `0.4.5` to `0.4.9`.

### 3. Dedicated Service Registration
* Moved `set_pump_speed` service registration out of platform setup into a dedicated `services` module (`custom_components/omnilogic/services.py`).
* Eliminates platform service registration deprecation warnings in newer Home Assistant versions.
* Updated `icons.json` service schema.

### 4. Setup Error Handling
* Setup now raises `ConfigEntryError` on login failures, presenting a clean authentication error status in the Home Assistant UI.

### 5. Sensor Modernization
* Migrated ratio and concentration sensor units to Home Assistant `UnitOfRatio` enums with backward-compatible fallback for older versions.
* Added `single_config_entry: true` manifest flag.

### 6. Installation Tooling
* Added `./scripts/install` helper script for dry-run and direct local installation into Home Assistant configuration directories.

---

## Upgrade Instructions

### HACS
1. Open **HACS** > **Integrations** > **Hayward OmniLogic (Custom)**.
2. Select **Update** (or **Redownload**) and choose version `0.1.1`.
3. Restart Home Assistant.

### Manual / Script
Run `./scripts/install go /path/to/homeassistant/config` and restart Home Assistant.
