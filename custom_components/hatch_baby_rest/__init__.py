import logging

from homeassistant import config_entries, core
from homeassistant.const import CONF_ADDRESS, Platform
from homeassistant.components.bluetooth import async_ble_device_from_address
from homeassistant.exceptions import ConfigEntryNotReady

from pyhatchbabyrest import PyHatchBabyRestAsync, connect_async

from .const import DOMAIN
from .coordinator import HatchBabyRestUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.SWITCH, Platform.LIGHT, Platform.MEDIA_PLAYER]


async def async_setup_entry(
    hass: core.HomeAssistant, entry: config_entries.ConfigEntry
) -> bool:
    address = entry.data[CONF_ADDRESS]
    ble_device = async_ble_device_from_address(hass, address.upper())
    if not ble_device:
        raise ConfigEntryNotReady(
            f"Could not find Hatch Baby Rest device with address {address}"
        )

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = HatchBabyRestUpdateCoordinator(
        hass,
        entry.unique_id,
        await connect_async(ble_device, scan_now=False, refresh_now=False),
    )
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "switch")
    )
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "light")
    )
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "media_player")
    )

    return True


async def options_update_listener(
    hass: core.HomeAssistant, config_entry: config_entries.ConfigEntry
):
    await hass.config_entries.async_reload(config_entry.entry_id)
