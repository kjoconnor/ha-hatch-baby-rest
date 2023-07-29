from datetime import timedelta
import logging

import async_timeout
from bleak import BleakError
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)
from pyhatchbabyrest import PyHatchBabyRestAsync

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class HatchBabyRestUpdateCoordinator(DataUpdateCoordinator):
    def __init__(
        self, hass: HomeAssistant, unique_id: str | None, device: PyHatchBabyRestAsync
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name="hatchbabyrest",
            update_interval=timedelta(seconds=30),
        )
        self.unique_id = unique_id
        self.device = device

    async def _async_update_data(self) -> None:
        try:
            async with async_timeout.timeout(10):
                await self.device.refresh_data()
        except TimeoutError as exc:
            raise UpdateFailed(
                "Connection timed out while fetching data from device"
            ) from exc
        except BleakError as exc:
            raise UpdateFailed("Failed getting data from device") from exc


class HatchBabyRestEntity(CoordinatorEntity):
    def __init__(self, coordinator: HatchBabyRestUpdateCoordinator) -> None:
        super().__init__(coordinator)
        self._device = coordinator.device
        self._attr_unique_id = coordinator.unique_id

    @property
    def device_name(self):
        return self._device.name

    @property
    def device_info(self) -> DeviceInfo:
        if not all((self._device.address, self.unique_id)):
            raise ValueError("Missing bluetooth address for hatch rest device")

        assert self._device.address
        assert self.unique_id

        device_name = self.device_name

        return {
            "identifiers": {(DOMAIN, self.unique_id)},
            "connections": {
                (device_registry.CONNECTION_BLUETOOTH, self._device.address)
            },
            "name": device_name,
            "manufacturer": "Hatch",
            "model": "Rest",
        }
