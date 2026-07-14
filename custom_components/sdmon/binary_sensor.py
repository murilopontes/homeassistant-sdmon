"""Binary sensor platform for SDmon."""

from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTR_ERROR, DOMAIN
from .coordinator import SDmonCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: SDmonCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([SDmonHealthyBinarySensor(coordinator, entry)])


class SDmonHealthyBinarySensor(CoordinatorEntity[SDmonCoordinator], BinarySensorEntity):
    """True when the latest sdmon reading was successful."""

    _attr_has_entity_name = True
    _attr_translation_key = "healthy"
    _attr_device_class = BinarySensorDeviceClass.PROBLEM
    _attr_icon = "mdi:sd"

    def __init__(self, coordinator: SDmonCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_healthy"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": entry.data[CONF_NAME],
            "manufacturer": "SDmon",
            "model": "Industrial SD Card",
        }

    @property
    def is_on(self) -> bool | None:
        data = self.coordinator.data
        if not data:
            return None
        return not data.get("success")

    @property
    def extra_state_attributes(self) -> dict:
        data = self.coordinator.data or {}
        attrs = {}
        if data.get("error"):
            attrs[ATTR_ERROR] = data["error"]
        return attrs
