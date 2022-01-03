from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers import config_validation as cv, entity_platform
import voluptuous as vol

import logging

from . import BaseEntity, get_coordinator
from .constants import DOMAIN

from datetime import datetime

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    _LOGGER.debug("Setup sensor: %s", entry)
    coordinator = get_coordinator(hass, entry)
    entities = []
    # platform = entity_platform.async_get_current_platform()
    entities.append(Odometer(entry, coordinator))
    entities.append(DTC(entry, coordinator))
    if coordinator.is_available("ambient_temp"):
        entities.append(AmbientTemp(entry, coordinator))
    if coordinator.is_available("rpm"):
        entities.append(RPM(entry, coordinator))
    if coordinator.is_available("speed"):
        entities.append(Speed(entry, coordinator))
    if coordinator.is_available("fuel"):
        entities.append(Fuel(entry, coordinator))
    # entities.append(Webhook(entry, coordinator))
    async_add_entities(entities)
    return True


class Odometer(BaseEntity, SensorEntity):

    def __init__(self, entry, coordinator):
        super().__init__(entry, coordinator)
        self.set_ids("odometer", "Odometer")
        self._attr_state_class = "measurement"
        self._attr_icon = "mdi:counter"

    @property
    def native_unit_of_measurement(self):
        return "km"

    @property
    def native_value(self):
        return self.data.get("odometer")

    @property
    def state(self):
        return self.native_value

    @property
    def available(self):
        return True

    @property
    def extra_state_attributes(self):
        return {
            "webhook": self._coordinator.hook_url()
        }

class AmbientTemp(BaseEntity, SensorEntity):

    def __init__(self, entry, coordinator):
        super().__init__(entry, coordinator)
        self.set_ids("ambient_temp", "Ambient Temperature")
        self._attr_state_class = "measurement"
        self._attr_device_class = "temperature"

    @property
    def native_unit_of_measurement(self):
        return "°C"

    @property
    def native_value(self):
        return self.sub_data.get("ambient_temp")

    @property
    def state(self):
        return self.native_value

class RPM(BaseEntity, SensorEntity):

    def __init__(self, entry, coordinator):
        super().__init__(entry, coordinator)
        self.set_ids("rpm", "Engine RPM")
        self._attr_state_class = "measurement"
        self._attr_icon = "mdi:engine"

    @property
    def native_unit_of_measurement(self):
        return "rpm"

    @property
    def native_value(self):
        return self.sub_data.get("rpm")

    @property
    def state(self):
        return self.native_value

class Speed(BaseEntity, SensorEntity):

    def __init__(self, entry, coordinator):
        super().__init__(entry, coordinator)
        self.set_ids("speed", "Current Speed")
        self._attr_state_class = "measurement"
        self._attr_icon = "mdi:speedometer"

    @property
    def native_unit_of_measurement(self):
        return "km/h"

    @property
    def native_value(self):
        return self.sub_data.get("speed")

    @property
    def state(self):
        return self.native_value

class Fuel(BaseEntity, SensorEntity):

    def __init__(self, entry, coordinator):
        super().__init__(entry, coordinator)
        self.set_ids("fuel", "Fuel Tank Level")
        self._attr_state_class = "measurement"
        self._attr_icon = "mdi:gas-station"

    @property
    def native_unit_of_measurement(self):
        return "%"

    @property
    def native_value(self):
        return self.sub_data.get("fuel")

    @property
    def state(self):
        return self.native_value

class DTC(BaseEntity, SensorEntity):

    def __init__(self, entry, coordinator):
        super().__init__(entry, coordinator)
        self.set_ids("dtcs", "Diagnostic Trouble Codes")
        self._attr_state_class = "measurement"
        self._attr_icon = "mdi:car-wrench"

    @property
    def native_value(self):
        return self.sub_data.get("dtc")

    @property
    def state(self):
        return self.native_value

    @property
    def available(self):
        return True

    @property
    def entity_category(self):
        return "diagnostic"
