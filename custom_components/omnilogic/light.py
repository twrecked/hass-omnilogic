"""Native ColorLogic lights for OmniLogic."""

from typing import Any

from omnilogic import OmniLogicException

from homeassistant.components.light import ColorMode, LightEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .common import OmniLogicOnOffEntity
from .const import COORDINATOR, DOMAIN
from .coordinator import OmniLogicUpdateCoordinator

V1_SHOW_CLOUD_WHITE = 6
V2_SHOW_WARM_WHITE = 25
V2_DEFAULT_SPEED = 4
V2_DEFAULT_BRIGHTNESS = 2


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up ColorLogic lights from OmniLogic telemetry."""
    coordinator: OmniLogicUpdateCoordinator = hass.data[DOMAIN][entry.entry_id][
        COORDINATOR
    ]
    async_add_entities(
        OmniLogicLight(coordinator, item_id)
        for item_id, item in coordinator.data.items()
        if len(item_id) == 6 and item_id[-2] == "Lights" and "lightState" in item
    )


class OmniLogicLight(OmniLogicOnOffEntity, LightEntity):
    """Control a ColorLogic light using a fixed turn-on preset."""

    _attr_color_mode = ColorMode.ONOFF
    _attr_supported_color_modes = {ColorMode.ONOFF}

    def __init__(
        self, coordinator: OmniLogicUpdateCoordinator, item_id: tuple
    ) -> None:
        """Initialize a ColorLogic light for its body of water."""
        super().__init__(coordinator, "light", "", "mdi:pool", item_id, "lightState")
        self._address = (int(item_id[1]), int(item_id[3]), int(item_id[-1]))

    async def _async_send_command(self, is_on: bool) -> None:
        """Send the off command or turn on with the generation's white preset."""
        api = self.coordinator.api
        action = "on" if is_on else "off"
        try:
            if not is_on:
                success = await api.set_relay_valve(*self._address, 0)
            elif self.coordinator.data.get(self._item_id, {}).get("V2") == "yes":
                success = await api.set_lightshowv2(
                    *self._address,
                    V2_SHOW_WARM_WHITE,
                    V2_DEFAULT_SPEED,
                    V2_DEFAULT_BRIGHTNESS,
                )
            else:
                success = await api.set_lightshow(*self._address, V1_SHOW_CLOUD_WHITE)
        except OmniLogicException as error:
            raise HomeAssistantError(
                f"Could not turn {action} the OmniLogic light"
            ) from error
        if not success:
            raise HomeAssistantError(
                f"OmniLogic rejected the light turn-{action} command"
            )

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on the light with its generation's white preset."""
        await self._async_set_state(True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the light without changing the preset."""
        await self._async_set_state(False)
