"""The Kostal piko integration."""


import logging

from kostalpyko.kostalpyko import Piko


from homeassistant.const import (
    CONF_USERNAME,
    CONF_PASSWORD,
    CONF_HOST,
    CONF_MONITORED_CONDITIONS,
)

from homeassistant.helpers.entity import Entity
from homeassistant.util import Throttle


from .const import SENSOR_TYPES, MIN_TIME_BETWEEN_UPDATES, DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    """Add an Kostal piko entry."""
    # Add the needed sensors to hass
    piko = Piko(
        entry.data[CONF_HOST], entry.data[CONF_USERNAME], entry.data[CONF_PASSWORD]
    )
    data = PikoData(piko, hass)

    entities = []

    for sensor in entry.data[CONF_MONITORED_CONDITIONS]:
        entities.append(PikoInverter(data, sensor, entry.title))
    async_add_entities(entities)


class PikoInverter(Entity):
    """Representation of a Piko inverter."""

    def __init__(self, piko_data, sensor_type, name):
        """Initialize the sensor."""
        self._sensor = SENSOR_TYPES[sensor_type][0]
        self._name = name
        self.type = sensor_type
        self.piko = piko_data
        self._state = None
        self._unit_of_measurement = SENSOR_TYPES[self.type][1]
        self._icon = SENSOR_TYPES[self.type][2]
        self.serial_number = None
        self.model = None
        self.update()

    @property
    def name(self):
        """Return the name of the sensor."""
        return "{} {}".format(self._name, self._sensor)

    @property
    def state(self):
        """Return the state of the device."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement this sensor expresses itself in."""
        return self._unit_of_measurement

    @property
    def icon(self):
        """Return icon."""
        return self._icon

    @property
    def unique_id(self):
        """Return unique id based on device serial and variable."""
        return "{} {}".format(self.serial_number, self._sensor)

    @property
    def device_info(self):
        """Return information about the device."""
        return {
            "identifiers": {(DOMAIN, self.serial_number)},
            "name": self._name,
            "manufacturer": "Kostal",
            "model": self.model,
        }

    def update(self):
        """Update data."""
        self.piko.update()
        data = self.piko.data
        ba_data = self.piko.ba_data
        self.serial_number = self.piko.info[0]
        self.model = self.piko.info[1]
        if ba_data is not None:
            if self.type == "solar_generator_power":
                if len(ba_data) > 1:
                    self._state = ba_data[5]
                else:
                    return "No BA sensor installed"
            elif self.type == "consumption_phase_1":
                if len(ba_data) > 1:
                    self._state = ba_data[8]
                else:
                    return "No BA sensor installed"
            elif self.type == "consumption_phase_2":
                if len(ba_data) > 1:
                    self._state = ba_data[9]
                else:
                    return "No BA sensor installed"
            elif self.type == "consumption_phase_3":
                if len(ba_data) > 1:
                    self._state = ba_data[10]
                else:
                    return "No BA sensor installed"
        if data is not None:
            if self.type == "current_power":
                if len(data) > 1:
                    self._state = data[0]
                else:
                    return None
            elif self.type == "total_energy":
                if len(data) > 1:
                    self._state = data[1]
                else:
                    return None
            elif self.type == "daily_energy":
                if len(data) > 1:
                    self._state = data[2]
                else:
                    return None
            elif self.type == "string1_voltage":
                if len(data) > 1:
                    self._state = data[3]
                else:
                    return None
            elif self.type == "string1_current":
                if len(data) > 1:
                    self._state = data[5]
            elif self.type == "string2_voltage":
                if len(data) > 1:
                    self._state = data[7]
                else:
                    return None
            elif self.type == "string2_current":
                if len(data) > 1:
                    self._state = data[9]
                else:
                    return None
            elif self.type == "string3_voltage":
                if len(data) > 1:
                    if len(data) < 15:
                        # String 3 not installed
                        return None
                    else:
                        # 3 Strings
                        self._state = data[11]
                else:
                    return None
            elif self.type == "string3_current":
                if len(data) > 1:
                    if len(data) < 15:
                        # String 3 not installed
                        return None
                    else:
                        # 3 Strings
                        self._state = data[13]
                else:
                    return None
            elif self.type == "l1_voltage":
                if len(data) > 1:
                    self._state = data[4]
                else:
                    return None
            elif self.type == "l1_power":
                if len(data) > 1:
                    self._state = data[6]
                else:
                    return None
            elif self.type == "l2_voltage":
                if len(data) > 1:
                    self._state = data[8]
                else:
                    return None
            elif self.type == "l2_power":
                if len(data) > 1:
                    self._state = data[10]
                else:
                    return None
            elif self.type == "l3_voltage":
                if len(data) > 1:
                    if len(data) < 15:
                        # 2 Strings
                        self._state = data[11]
                    else:
                        # 3 Strings
                        self._state = data[12]
                else:
                    return None
            elif self.type == "l3_power":
                if len(data) > 1:
                    if len(data) < 15:
                        # 2 Strings
                        self._state = data[12]
                    else:
                        # 3 Strings
                        self._state = data[14]
                else:
                    return None
            elif self.type == "status":
                if len(data) > 1:
                    if len(data) < 15:
                        # 2 Strings
                        self._state = data[13]
                    else:
                        # 3 Strings
                        self._state = data[15]

                else:
                    return None


class PikoData(Entity):
    """Representation of a Piko inverter."""

    def __init__(self, piko, hass):
        """Initialize the data object."""
        self.piko = piko
        self.hass = hass
        self.data = []
        self.ba_data = []
        self.info = None
        self.info_update()

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def update(self):
        """Update inverter data."""
        # pylint: disable=protected-access
        self.data = self.piko._get_raw_content()
        self.ba_data = self.piko._get_content_of_own_consumption()
        _LOGGER.debug(self.data)
        _LOGGER.debug(self.ba_data)

    def info_update(self):
        """Update inverter info."""
        # pylint: disable=protected-access
        self.info = self.piko._get_info()
        _LOGGER.debug(self.info)
