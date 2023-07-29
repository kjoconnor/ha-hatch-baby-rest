from typing import Any
from homeassistant.components.light import (
    ColorMode,
    LightEntity,
    ATTR_BRIGHTNESS,
    ATTR_RGB_COLOR,
)
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
    async_add_entities([HatchBabyRestLight(coordinator)], True)


class HatchBabyRestLight(HatchBabyRestEntity, LightEntity):
    @property
    def color_mode(self) -> ColorMode | str | None:
        return ColorMode.RGB

    @property
    def supported_color_modes(self) -> set[ColorMode] | set[str] | None:
        return set([ColorMode.RGB])

    @property
    def brightness(self) -> int | None:
        return self._device.brightness

    @property
    def rgb_color(self) -> tuple[int, int, int] | None:
        return self._device.color

    async def async_turn_on(self, **kwargs: Any) -> None:
        brightness = kwargs.get(ATTR_BRIGHTNESS)
        rgb = kwargs.get(ATTR_RGB_COLOR)

        if brightness:
            await self._device.set_brightness(brightness)
        if rgb:
            await self._device.set_color(*rgb)

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self._device.set_brightness(0)
