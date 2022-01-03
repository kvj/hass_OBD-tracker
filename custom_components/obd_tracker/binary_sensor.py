from homeassistant.components.binary_sensor import BinarySensorEntity

import logging

from . import BaseEntity, get_coordinator
from .constants import DOMAIN

from datetime import datetime

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    _LOGGER.debug("Setup binary sensor: %s", entry)
    coordinator = get_coordinator(hass, entry)
    entities = []
    entities.append(MIL(entry, coordinator))
    entities.append(DTC(entry, coordinator))
    async_add_entities(entities)
    return True


class MIL(BaseEntity, BinarySensorEntity):

    def __init__(self, entry, coordinator):
        super().__init__(entry, coordinator)
        self.set_ids("mil", "Malfunction Indicator Lamp")
        self._attr_state_class = "measurement"
        self._attr_device_class = "problem"
        # self._attr_icon = "mdi:counter"

    @property
    def is_on(self):
        return self.sub_data.get("mil")

    @property
    def available(self):
        return True


class DTC(BaseEntity, BinarySensorEntity):

    def __init__(self, entry, coordinator):
        super().__init__(entry, coordinator)
        self.set_ids("dtc", "Diagnostic Trouble Code")
        self._attr_state_class = "measurement"
        self._attr_device_class = "problem"
        self._attr_icon = "mdi:car-wrench"

    @property
    def is_on(self):
        return self.sub_data.get("dtc") > 0

    @property
    def available(self):
        return True
