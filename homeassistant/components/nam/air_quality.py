"""Support for the Nettigo Air Monitor air_quality service."""
from __future__ import annotations

from homeassistant.components.air_quality import AirQualityEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import NAMDataUpdateCoordinator
from .const import (
    AIR_QUALITY_SENSORS,
    ATTR_MHZ14A_CARBON_DIOXIDE,
    DEFAULT_NAME,
    DOMAIN,
    SUFFIX_P1,
    SUFFIX_P2,
)

PARALLEL_UPDATES = 1


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Add a Nettigo Air Monitor entities from a config_entry."""
    coordinator: NAMDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[NAMAirQuality] = []
    for sensor in AIR_QUALITY_SENSORS:
        if f"{sensor}{SUFFIX_P1}" in coordinator.data:
            entities.append(NAMAirQuality(coordinator, sensor))

    async_add_entities(entities, False)


class NAMAirQuality(CoordinatorEntity, AirQualityEntity):
    """Define an Nettigo Air Monitor air quality."""

    coordinator: NAMDataUpdateCoordinator

    def __init__(self, coordinator: NAMDataUpdateCoordinator, sensor_type: str) -> None:
        """Initialize."""
        super().__init__(coordinator)
        self._attr_device_info = coordinator.device_info
        self._attr_name = f"{DEFAULT_NAME} {AIR_QUALITY_SENSORS[sensor_type]}"
        self._attr_unique_id = f"{coordinator.unique_id}-{sensor_type}"
        self.sensor_type = sensor_type

    @property
    def particulate_matter_2_5(self) -> StateType:
        """Return the particulate matter 2.5 level."""
        return round_state(
            getattr(self.coordinator.data, f"{self.sensor_type}{SUFFIX_P2}")
        )

    @property
    def particulate_matter_10(self) -> StateType:
        """Return the particulate matter 10 level."""
        return round_state(
            getattr(self.coordinator.data, f"{self.sensor_type}{SUFFIX_P1}")
        )

    @property
    def carbon_dioxide(self) -> StateType:
        """Return the particulate matter 10 level."""
        return round_state(
            getattr(self.coordinator.data, ATTR_MHZ14A_CARBON_DIOXIDE, None)
        )

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        available = super().available

        # For a short time after booting, the device does not return values for all
        # sensors. For this reason, we mark entities for which data is missing as
        # unavailable.
        return available and bool(
            getattr(self.coordinator.data, f"{self.sensor_type}{SUFFIX_P2}", None)
        )


def round_state(state: StateType) -> StateType:
    """Round state."""
    if isinstance(state, float):
        return round(state)

    return state
