# Release Notes — v0.1.0

Initial custom component release of Hayward OmniLogic for Home Assistant, providing custom features and sensor additions ahead of core Home Assistant.

---

## What's Changed

### 1. Heater State Binary Sensor
* Added binary sensor entity support (`heaterState`) targeting pool and spa heaters.
* Uses `BinarySensorDeviceClass.HEAT` to indicate when the heater is actively running and heating.

### 2. Instant Salt Level Sensor
* Added dedicated sensor entity exposing the instantaneous salt reading (`instantSaltLevel`) in ppm / metric equivalents, complementing the standard calculated average salt level.

### 3. Below-Freezing Temperature Reading Fix
* Fixed handling of negative and below-freezing temperature readings wrapped as unsigned 8-bit integers (> 127) reported by Hayward telemetry.

### 4. Configurable Polling Interval
* Preserved user-configurable polling interval in integration Options Flow to reduce Hayward cloud traffic and avoid rate limits.

### 5. HACS & Upstream Sync Support
* Added HACS custom repository configuration (`hacs.json`).
* Added git vendor branch tracking and sync automation (`scripts/sync-upstream.sh`) to easily merge core Home Assistant updates.

---

## Installation & Upgrade

### HACS
1. Open **HACS** > **Integrations** > Three dots (top right) > **Custom repositories**.
2. Add `https://github.com/twrecked/hass-omnilogic` as an **Integration**.
3. Download `v0.1.0` and restart Home Assistant.

### Manual / Script
Run `./scripts/install go /path/to/homeassistant/config` and restart Home Assistant.
