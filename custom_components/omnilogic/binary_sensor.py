"""Definition and setup of the Omnilogic Binary Sensors for Home Assistant."""
from typing import Any
import logging

from homeassistant.components.binary_sensor import BinarySensorDeviceClass, BinarySensorEntity

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .common import OmniLogicEntity, check_guard
from .const import COORDINATOR, DOMAIN
from .coordinator import OmniLogicUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
        hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the sensor platform."""

    coordinator: OmniLogicUpdateCoordinator = hass.data[DOMAIN][entry.entry_id][
        COORDINATOR
    ]
    entities = []

    for item_id, item in coordinator.data.items():
        id_len = len(item_id)
        item_kind = item_id[-2]
        entity_settings = SENSOR_TYPES.get((id_len, item_kind))

        if not entity_settings:
            continue

        for entity_setting in entity_settings:
            entity_classes: dict[str, type] = entity_setting["entity_classes"]
            for state_key, entity_class in entity_classes.items():
                if check_guard(state_key, item, entity_setting):
                    continue

                entity = entity_class(
                    coordinator=coordinator,
                    state_key=state_key,
                    name=entity_setting["name"],
                    kind=entity_setting["kind"],
                    item_id=item_id,
                    device_class=entity_setting["device_class"],
                    icon=entity_setting["icon"]
                )

                entities.append(entity)

    async_add_entities(entities)


class OmnilogicBinarySensor(OmniLogicEntity, BinarySensorEntity):
    """Defines an Omnilogic sensor entity."""

    def __init__(
            self,
            coordinator: OmniLogicUpdateCoordinator,
            kind: str,
            name: str,
            device_class: str,
            icon: str,
            item_id: tuple,
            state_key: str,
    ) -> None:
        """Initialize Entities."""
        super().__init__(
            coordinator=coordinator,
            kind=kind,
            name=name,
            item_id=item_id,
            icon=icon,
        )

        self._device_class = device_class
        self._state_key = state_key
        self._attr_is_on = False

    @property
    def device_class(self):
        """Return the device class of the entity."""
        return self._device_class

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        new_is_on = int(self.coordinator.data[self._item_id][self._state_key]) != 0
        if self._attr_is_on != new_is_on:
            self._attr_is_on = new_is_on
            _LOGGER.debug(f"Updated {self._attr_is_on}")
            self.async_write_ha_state()


SENSOR_TYPES: dict[tuple[int, str], list[dict[str, Any]]] = {
    (6, "Heaters"): [
        {
            "entity_classes": {"heaterState": OmnilogicBinarySensor},
            "name": "Heater",
            "kind": "heater",
            "device_class": BinarySensorDeviceClass.HEAT,
            "icon": None,
            "guard_condition": [{}],
        }
    ],
}
