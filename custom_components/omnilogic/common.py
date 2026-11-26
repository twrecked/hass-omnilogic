"""Common classes and elements for Omnilogic Integration."""

from asyncio import Lock
from collections.abc import Callable
from datetime import datetime
import logging
from time import monotonic
from typing import Any

from homeassistant.core import callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.event import async_call_later
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import OmniLogicUpdateCoordinator

COMMAND_CONFIRMATION_TIMEOUT = 30
_LOGGER = logging.getLogger(__name__)


class OmniLogicEntity(CoordinatorEntity[OmniLogicUpdateCoordinator]):
    """Defines the base OmniLogic entity."""

    def __init__(
        self,
        coordinator: OmniLogicUpdateCoordinator,
        kind: str,
        name: str,
        item_id: tuple,
        icon: str | None,
    ) -> None:
        """Initialize the OmniLogic Entity."""
        super().__init__(coordinator)

        bow_id = None
        entity_data = coordinator.data[item_id]

        backyard_id = item_id[:2]
        if len(item_id) == 6:
            bow_id = item_id[:4]

        msp_system_id = coordinator.data[backyard_id]["systemId"]
        entity_friendly_name = f"{coordinator.data[backyard_id]['BackyardName']} "
        unique_id = f"{msp_system_id}"

        if bow_id is not None:
            unique_id = f"{unique_id}_{coordinator.data[bow_id]['systemId']}"

            if kind != "Heaters":
                entity_friendly_name = (
                    f"{entity_friendly_name}{coordinator.data[bow_id]['Name']} "
                )
            else:
                entity_friendly_name = f"{entity_friendly_name}{coordinator.data[bow_id]['Operation']['VirtualHeater']['Name']} "

        unique_id = f"{unique_id}_{coordinator.data[item_id]['systemId']}_{kind}"

        if entity_data.get("Name") is not None:
            entity_friendly_name = f"{entity_friendly_name} {entity_data['Name']}"

        entity_friendly_name = f"{entity_friendly_name} {name}"

        unique_id = unique_id.replace(" ", "_")

        self._kind = kind
        self._name = entity_friendly_name
        self._unique_id = unique_id
        self._item_id = item_id
        self._icon = icon
        self._attrs: dict[str, Any] = {}
        self._msp_system_id = msp_system_id
        self._backyard_name = coordinator.data[backyard_id]["BackyardName"]

    @property
    def unique_id(self) -> str:
        """Return a unique, Home Assistant friendly identifier for this entity."""
        return self._unique_id

    @property
    def name(self) -> str:
        """Return the name of the entity."""
        return self._name

    @property
    def icon(self):
        """Return the icon for the entity."""
        return self._icon

    @property
    def extra_state_attributes(self):
        """Return the attributes."""
        return self._attrs

    @property
    def device_info(self) -> DeviceInfo:
        """Define the device as back yard/MSP System."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._msp_system_id)},
            manufacturer="Hayward",
            model="OmniLogic",
            name=self._backyard_name,
        )


class OmniLogicOnOffEntity(OmniLogicEntity):
    """Hold an accepted on/off command until telemetry catches up."""

    def __init__(
        self,
        coordinator: OmniLogicUpdateCoordinator,
        kind: str,
        name: str,
        icon: str | None,
        item_id: tuple,
        state_key: str,
    ) -> None:
        """Initialize command and confirmation tracking."""
        super().__init__(coordinator, kind, name, item_id, icon)
        self._state_key = state_key
        self._command_lock = Lock()
        self._pending_state: bool | None = None
        self._command_accepted_at = 0.0
        self._cancel_confirmation: Callable[[], None] | None = None

    @property
    def is_on(self) -> bool | None:
        """Return the accepted command state while telemetry catches up."""
        if self._pending_state is not None:
            return self._pending_state
        return self._reported_state()

    def _reported_state(self) -> bool | None:
        """Read the on/off state from the latest telemetry."""
        state = self.coordinator.data.get(self._item_id, {}).get(self._state_key)
        if state in ("1", 1):
            return True
        if state in ("0", 0):
            return False
        return None

    @callback
    def _async_clear_pending_state(self) -> None:
        """Stop holding the accepted state and cancel its expiry timer."""
        self._pending_state = None
        if self._cancel_confirmation is not None:
            self._cancel_confirmation()
            self._cancel_confirmation = None

    @callback
    def _async_confirmation_expired(self, _now: datetime) -> None:
        """Return to telemetry even if no new poll has confirmed the command."""
        _LOGGER.debug(
            "%s: no confirmation after %.1f seconds (requested %s, reported %s)",
            self.entity_id,
            monotonic() - self._command_accepted_at,
            self._pending_state,
            self._reported_state(),
        )
        self._cancel_confirmation = None
        self._pending_state = None
        self.async_write_ha_state()

    @callback
    def _handle_coordinator_update(self) -> None:
        """Confirm only with a poll started after the command was accepted."""
        if (
            self._pending_state is not None
            and self.coordinator.last_update_success
            and self.coordinator.telemetry_started_at >= self._command_accepted_at
            and self._reported_state() == self._pending_state
        ):
            self._async_clear_pending_state()
        super()._handle_coordinator_update()

    async def async_will_remove_from_hass(self) -> None:
        """Cancel the confirmation timer when the entity is removed."""
        self._async_clear_pending_state()
        await super().async_will_remove_from_hass()

    async def _async_set_state(self, is_on: bool) -> None:
        """Send the command and hold the requested state only on success."""
        async with self._command_lock:
            await self._async_send_command(is_on)
            self._async_clear_pending_state()
            self._pending_state = is_on
            self._command_accepted_at = monotonic()
            self._cancel_confirmation = async_call_later(
                self.hass,
                self._confirmation_timeout(is_on),
                self._async_confirmation_expired,
            )
            self.async_write_ha_state()
        await self.coordinator.async_request_refresh()

    def _confirmation_timeout(self, is_on: bool) -> int:
        """Return the seconds to wait for command confirmation."""
        return COMMAND_CONFIRMATION_TIMEOUT

    async def _async_send_command(self, is_on: bool) -> None:
        """Send the device-specific command or raise if it fails."""
        raise NotImplementedError


def check_guard(state_key, item, entity_setting):
    """Validate that this entity passes the defined guard conditions defined at setup."""

    if state_key not in item:
        return True

    for guard_condition in entity_setting["guard_condition"]:
        if guard_condition and all(
            item.get(guard_key) == guard_value
            for guard_key, guard_value in guard_condition.items()
        ):
            return True

    return False
