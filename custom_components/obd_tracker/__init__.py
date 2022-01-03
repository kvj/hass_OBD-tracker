from __future__ import annotations
from .constants import DOMAIN, PLATFORMS
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, CoordinatorEntity
from homeassistant.helpers.network import get_url
from homeassistant.components import webhook

import logging
from datetime import timedelta

_LOGGER = logging.getLogger(__name__)

BRIDGE_HOOK = "obd_tracker_"

def get_coordinator(hass, entry):
    return hass.data[DOMAIN][entry.entry_id]

async def async_setup_entry(hass, entry):
    _LOGGER.debug("Setup platform: %s", entry)
    entry.async_on_unload(entry.add_update_listener(update_listener))
    coordinator = Coordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()
    hass.data[DOMAIN][entry.entry_id] = coordinator
    for p in PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, p))
    return True

async def update_listener(hass, entry):
    await get_coordinator(hass, entry).async_request_refresh()


async def async_unload_entry(hass, entry):
    for p in PLATFORMS:
        await hass.config_entries.async_forward_entry_unload(entry, p)
    hass.data[DOMAIN].pop(entry.entry_id)
    return True


async def async_setup(hass, config) -> bool:
    hass.data[DOMAIN] = dict()
    return True

class Coordinator(DataUpdateCoordinator):

    def __init__(self, hass, entry) -> None:
        super().__init__(
            hass, 
            _LOGGER, 
            name="OBD Tracker", 
            update_method=self.async_update, 
        )
        self.entry = entry
        webhook.async_unregister(hass, self.hook_path())
        webhook.async_register(
            hass,
            DOMAIN,
            "obd_tracker",
            self.hook_path(),
            handler=self.async_hook_callback,
        )


    def hook_path(self):
        return "%s_%s" % (BRIDGE_HOOK, self.entry.entry_id)

    def hook_url(self):
        url = get_url(self.hass, prefer_external=True, prefer_cloud=True)
        return "{}{}".format(url, webhook.async_generate_path(self.hook_path()))

    async def async_update(self):
        _LOGGER.debug("Coordinator update: %s", self.entry.as_dict())
        return self.entry.as_dict()

    async def async_hook_callback(self, hass, hook_id, request):
        body = await request.json()
        _LOGGER.debug(f"hook_handler: {body}")
        await self.async_update_data({"last": body})

    async def async_update_data(self, new_data):
        data = {**self.data.get("data", {}), **new_data}
        _LOGGER.debug("update_data: %s", data)
        self.hass.config_entries.async_update_entry(self.entry, data=data)
        await self.async_request_refresh()

    @property
    def options(self):
        return self.data.get("options", {})

    @property
    def device_name(self):
        return self.data.get("data", {}).get("name")

    @property
    def last_data(self):
        return self.data.get("data", {}).get("last", {})

    def is_available(self, id):
        return self.options.get(id) == True

class BaseEntity(CoordinatorEntity):

    def __init__(self, entry, coordinator):
        super().__init__(coordinator)
        self._entry = entry
        self._id = entry.entry_id
        self._coordinator = coordinator
        _LOGGER.debug("New BaseEntity: %s, %s, %s", self._id, self.data, self.options)

    @property
    def options(self):
        return self._coordinator.options

    @property
    def data(self):
        return self._coordinator.last_data

    @property
    def sub_data(self):
        return self.data.get("data", {})
    
    def set_ids(self, id: str, name: str):
        self.id_suffix = id
        self.name_suffix = name

    @property
    def name(self) -> str:
        return ("%s %s" % (self._coordinator.device_name, self.name_suffix)).strip()

    @property
    def unique_id(self) -> str:
        return "%s-%s" % (self._id, self.id_suffix)

    @property
    def available(self):
        return self._coordinator.is_available(self.id_suffix)

    @property
    def device_info(self):
        return {
            "identifiers": {("id", self._id)},
            "name": self._coordinator.device_name,
        }
