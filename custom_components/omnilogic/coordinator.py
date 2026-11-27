"""Coordinator for the Omnilogic Integration."""

from collections.abc import Callable
from datetime import datetime, timedelta
import logging
from time import monotonic
from typing import Any

from omnilogic import OmniLogic, OmniLogicException

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.event import async_call_later
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import ALL_ITEM_KINDS

_LOGGER = logging.getLogger(__name__)
CONFIRMATION_POLL_INTERVAL = 10


class OmniLogicUpdateCoordinator(DataUpdateCoordinator[dict[tuple, dict[str, Any]]]):
    """Class to manage fetching update data from single endpoint."""

    def __init__(
        self,
        hass: HomeAssistant,
        api: OmniLogic,
        name: str,
        config_entry: ConfigEntry,
        polling_interval: int,
    ) -> None:
        """Initialize the global Omnilogic data updater."""
        self.api = api
        self.config_entry = config_entry
        self.telemetry_started_at = 0.0
        self._pending_confirmations: set[tuple] = set()
        self._cancel_confirmation_poll: Callable[[], None] | None = None
        self._confirmation_poll_running = False

        super().__init__(
            hass=hass,
            logger=_LOGGER,
            name=name,
            update_interval=timedelta(seconds=polling_interval),
        )

    @callback
    def async_set_confirmation_pending(self, item_id: tuple, pending: bool) -> None:
        """Share follow-up polling across entities waiting for confirmation."""
        if pending:
            self._pending_confirmations.add(item_id)
            self._async_schedule_confirmation_poll()
        else:
            self._pending_confirmations.discard(item_id)
            if not self._pending_confirmations and self._cancel_confirmation_poll:
                self._cancel_confirmation_poll()
                self._cancel_confirmation_poll = None

    @callback
    def _async_schedule_confirmation_poll(self) -> None:
        """Schedule one follow-up when regular polling is not already faster."""
        delay = timedelta(seconds=CONFIRMATION_POLL_INTERVAL)
        if (
            self._pending_confirmations
            and self._cancel_confirmation_poll is None
            and not self._confirmation_poll_running
            and (self.update_interval is None or self.update_interval > delay)
        ):
            self._cancel_confirmation_poll = async_call_later(
                self.hass, delay, self._async_confirmation_poll
            )

    async def _async_confirmation_poll(self, _now: datetime) -> None:
        """Request fresh telemetry and retry only while a command is pending."""
        self._cancel_confirmation_poll = None
        if not self._pending_confirmations:
            return
        self._confirmation_poll_running = True
        try:
            await self.async_request_refresh()
        finally:
            self._confirmation_poll_running = False
            self._async_schedule_confirmation_poll()

    async def _async_update_data(self):
        """Fetch data from OmniLogic."""
        started_at = monotonic()
        try:
            data = await self.api.get_telemetry_data()

        except OmniLogicException as error:
            # The library only logs in again without a token, so drop a
            # possibly rejected one to have the next update log in again.
            self.api.token = None
            raise UpdateFailed(f"Error updating from OmniLogic: {error}") from error

        parsed_data = {}

        def get_item_data(item, item_kind, current_id, data):
            """Get data per kind of Omnilogic API item."""
            if isinstance(item, list):
                for single_item in item:
                    data = get_item_data(single_item, item_kind, current_id, data)

            if "systemId" in item:
                system_id = item["systemId"]
                current_id = (*current_id, item_kind, system_id)
                data[current_id] = item

            for kind in ALL_ITEM_KINDS:
                if kind in item:
                    data = get_item_data(item[kind], kind, current_id, data)

            return data

        parsed_data = get_item_data(data, "Backyard", (), parsed_data)
        self.telemetry_started_at = started_at
        return parsed_data
