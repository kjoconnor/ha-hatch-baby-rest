from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import HatchBabyRestEntity
from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities([HatchBabyRestSwitch(coordinator)], True)


class HatchBabyRestSwitch(HatchBabyRestEntity, SwitchEntity):
    @property
    def is_on(self) -> bool | None:
        return getattr(self._device, "power", None)

    async def async_turn_on(self, **_):
        """Turn on the Hatch Rest device."""
        if not self.is_on:
            await self._device.power_on()
            self._device.power = True

        self.async_write_ha_state()

    async def async_turn_off(self, **_):
        """Turn off the Hatch Rest device."""
        if self.is_on:
            await self._device.power_off()
            self._device.power = False

        self.async_write_ha_state()
