"""Sensor platform for SDmon."""

from __future__ import annotations

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    ATTR_CARD_TYPE,
    ATTR_DEVICE_PATH,
    ATTR_ERROR,
    ATTR_SDMON_VERSION,
    DOMAIN,
    SENSOR_DEFINITIONS,
)
from .coordinator import SDmonCoordinator
from .parser import metric_value


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: SDmonCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities: list[SDmonSensor] = [
        SDmonStatusSensor(coordinator, entry),
        SDmonHealthSensor(coordinator, entry),
    ]

    for sensor_id, definition in SENSOR_DEFINITIONS.items():
        if sensor_id in {"health"}:
            continue
        entities.append(SDmonMetricSensor(coordinator, entry, sensor_id, definition))

    async_add_entities(entities)


class SDmonEntity(CoordinatorEntity[SDmonCoordinator], SensorEntity):
    """Base SDmon sensor."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: SDmonCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._entry = entry
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": entry.data[CONF_NAME],
            "manufacturer": "SDmon",
            "model": "Industrial SD Card",
        }

    @property
    def available(self) -> bool:
        return self.coordinator.last_update_success

    @property
    def extra_state_attributes(self) -> dict:
        data = self.coordinator.data or {}
        raw = data.get("raw") or {}
        attrs = {
            ATTR_CARD_TYPE: data.get("card_type"),
            ATTR_DEVICE_PATH: data.get("device") or self.coordinator.device,
            ATTR_SDMON_VERSION: data.get("sdmon_version"),
        }
        if data.get("error"):
            attrs[ATTR_ERROR] = data["error"]
        if raw.get("productString"):
            attrs["product"] = str(raw["productString"]).strip()
        return {key: value for key, value in attrs.items() if value is not None}


class SDmonStatusSensor(SDmonEntity):
    """Operational status of the sdmon reading."""

    _attr_translation_key = "status"
    _attr_icon = "mdi:sd"

    def __init__(self, coordinator: SDmonCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_status"

    @property
    def native_value(self) -> str | None:
        data = self.coordinator.data
        if not data:
            return None
        return "ok" if data.get("success") else "error"


class SDmonHealthSensor(SDmonEntity):
    """Remaining health percentage."""

    _attr_translation_key = "health"
    _attr_native_unit_of_measurement = "%"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:heart-pulse"

    def __init__(self, coordinator: SDmonCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_health"

    @property
    def native_value(self) -> float | None:
        data = self.coordinator.data
        if not data:
            return None
        return data.get("health")

    @property
    def available(self) -> bool:
        return (
            super().available
            and self.coordinator.data is not None
            and self.coordinator.data.get("health") is not None
        )


class SDmonMetricSensor(SDmonEntity):
    """Generic metric sensor mapped from sdmon JSON."""

    def __init__(
        self,
        coordinator: SDmonCoordinator,
        entry: ConfigEntry,
        sensor_id: str,
        definition: dict,
    ) -> None:
        super().__init__(coordinator, entry)
        self._sensor_id = sensor_id
        self._definition = definition
        self._attr_unique_id = f"{entry.entry_id}_{sensor_id}"
        self._attr_translation_key = sensor_id
        self._attr_icon = definition.get("icon")
        if definition.get("unit"):
            self._attr_native_unit_of_measurement = definition["unit"]
        if definition.get("device_class"):
            self._attr_device_class = SensorDeviceClass(definition["device_class"])
        if definition.get("state_class"):
            self._attr_state_class = SensorStateClass(definition["state_class"])

    @property
    def native_value(self) -> str | float | int | None:
        raw = (self.coordinator.data or {}).get("raw") or {}
        return metric_value(raw, self._definition)

    @property
    def available(self) -> bool:
        return super().available and self.native_value is not None
