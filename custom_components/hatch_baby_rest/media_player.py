from homeassistant.components.media_player import (
    MediaPlayerDeviceClass,
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
    MediaPlayerState,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from pyhatchbabyrest.constants import PyHatchBabyRestSound

from .coordinator import HatchBabyRestEntity
from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities([HatchBabyRestMediaPlayer(coordinator)], True)


class HatchBabyRestMediaPlayer(HatchBabyRestEntity, MediaPlayerEntity):
    @property
    def supported_features(self) -> MediaPlayerEntityFeature:
        return (
            MediaPlayerEntityFeature.PLAY
            | MediaPlayerEntityFeature.PAUSE
            | MediaPlayerEntityFeature.VOLUME_SET
            | MediaPlayerEntityFeature.SELECT_SOURCE
        )

    @property
    def device_class(self) -> MediaPlayerDeviceClass | None:
        return MediaPlayerDeviceClass.SPEAKER

    @property
    def source_list(self) -> list[str] | None:
        return [sound.name.capitalize() for sound in PyHatchBabyRestSound]

    async def async_set_volume_level(self, volume: float) -> None:
        await self._device.set_volume(int(255 * volume))
        self.async_write_ha_state()

    async def async_select_source(self, source: str) -> None:
        source_number = [
            val for val in PyHatchBabyRestSound if val.name == source.lower()
        ][0]
        self._previous_sound = PyHatchBabyRestSound(source_number)
        await self._device.set_sound(source_number)
        self.async_write_ha_state()

    @property
    async def state(self) -> MediaPlayerState | None:
        if not getattr(self._device, "power"):
            await self._device.refresh_data()

        if self._device.power is False:
            return MediaPlayerState.OFF

        if self._device.sound == PyHatchBabyRestSound.none:
            return MediaPlayerState.PAUSED

        return MediaPlayerState.PLAYING

    @property
    def source(self) -> str | None:
        return self._device.sound.name.capitalize()

    @property
    def volume_level(self) -> float | None:
        return float(self._device.volume / 255)

    async def async_media_pause(self) -> None:
        self._previous_sound = self._device.sound
        await self._device.set_sound(PyHatchBabyRestSound.none)
        self.async_write_ha_state()

    async def async_media_play(self) -> None:
        if previous_sound := getattr(self, "_previous_sound"):
            await self._device.set_sound(previous_sound)
        self.async_write_ha_state()
