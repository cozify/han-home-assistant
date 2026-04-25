import logging
from datetime import timedelta
from homeassistant.helpers.entity import EntityCategory
from homeassistant.util import dt as dt_util

from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.const import (
    UnitOfPower,
    UnitOfEnergy,
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    CONF_HOST,
)
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import async_timeout

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    # Set all the sensors
    host = entry.data[CONF_HOST]
    session = async_get_clientsession(hass)

    # 1. Preliminary data fetch
    device_info_init = {}
    try:
        async with async_timeout.timeout(5):
            response = await session.get(f"http://{host}/han", ssl=False)
            if response.status == 200:
                device_info_init = await response.json()
    except Exception as err:
        _LOGGER.warning("Laitetietojen haku epäonnistui alustuksessa: %s", err)

    # 2. Cordinator retrieves data from different endpoints
    async def async_update_data():
        combined_data = {}
        try:
            async with async_timeout.timeout(10):
                # Mittaukset
                r_meter = await session.get(f"http://{host}/meter", ssl=False)
                combined_data["realtime"] = await r_meter.json()

                # Konfiguraatio
                r_conf = await session.get(f"http://{host}/configuration", ssl=False)
                combined_data["config"] = await r_conf.json()

                # Status
                r_han = await session.get(f"http://{host}/han", ssl=False)
                combined_data["status"] = await r_han.json()

                # Sähkömittarin identity (muuttuu harvoin)
                try:
                    r_meter_id = await session.get(f"http://{host}/meter/id", ssl=False)
                    if r_meter_id.status == 200:
                        combined_data["meter_id"] = await r_meter_id.json()
                    else:
                        combined_data["meter_id"] = {}
                except Exception as err:
                    _LOGGER.debug("Mittarin identity-haku epäonnistui: %s", err)
                    combined_data["meter_id"] = {}

                return combined_data
        except Exception as err:
            _LOGGER.error("Datan haku epäonnistui: %s", err)
            raise UpdateFailed(f"Yhteysvirhe laitteeseen: {err}")

    scan_interval = entry.options.get("update_interval", 5)

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="Cozify HAN sensor",
        update_method=async_update_data,
        update_interval=timedelta(seconds=scan_interval),
    )

    await coordinator.async_config_entry_first_refresh()

    sensors = [
        # --- ENERGY (kWh) ---
        CozifyEnergySensor(coordinator, entry, "ic", "Total Power Imported", device_info_init),
        CozifyEnergySensor(coordinator, entry, "ec", "Total Power Exported", device_info_init),

        # --- POWER (W) ---
        CozifyArraySensor(coordinator, entry, "p", 0, "DEPRECATED Power Total", UnitOfPower.WATT, device_info_init),
        CozifyArraySensor(coordinator, entry, "p", 1, "DEPRECATED Power L1", UnitOfPower.WATT, device_info_init),
        CozifyArraySensor(coordinator, entry, "p", 2, "DEPRECATED Power L2", UnitOfPower.WATT, device_info_init),
        CozifyArraySensor(coordinator, entry, "p", 3, "DEPRECATED Power L3", UnitOfPower.WATT, device_info_init),
        
        CozifyArraySensor(coordinator, entry, "pi", 0, "Power Import Total", UnitOfPower.WATT, device_info_init),
        CozifyArraySensor(coordinator, entry, "pi", 1, "Power Import L1", UnitOfPower.WATT, device_info_init),
        CozifyArraySensor(coordinator, entry, "pi", 2, "Power Import L2", UnitOfPower.WATT, device_info_init),
        CozifyArraySensor(coordinator, entry, "pi", 3, "Power Import L3", UnitOfPower.WATT, device_info_init),
        
        CozifyArraySensor(coordinator, entry, "pe", 0, "Power Export Total", UnitOfPower.WATT, device_info_init),
        CozifyArraySensor(coordinator, entry, "pe", 1, "Power Export L1", UnitOfPower.WATT, device_info_init),
        CozifyArraySensor(coordinator, entry, "pe", 2, "Power Export L2", UnitOfPower.WATT, device_info_init),
        CozifyArraySensor(coordinator, entry, "pe", 3, "Power Export L3", UnitOfPower.WATT, device_info_init),

        # --- CURRENT (V) ---
        CozifyArraySensor(coordinator, entry, "u", 0, "Voltage L1", UnitOfElectricPotential.VOLT, device_info_init),
        CozifyArraySensor(coordinator, entry, "u", 1, "Voltage L2", UnitOfElectricPotential.VOLT, device_info_init),
        CozifyArraySensor(coordinator, entry, "u", 2, "Voltage L3", UnitOfElectricPotential.VOLT, device_info_init),

        # --- AMP (A) ---
        CozifyArraySensor(coordinator, entry, "i", 0, "Current L1", UnitOfElectricCurrent.AMPERE, device_info_init),
        CozifyArraySensor(coordinator, entry, "i", 1, "Current L2", UnitOfElectricCurrent.AMPERE, device_info_init),
        CozifyArraySensor(coordinator, entry, "i", 2, "Current L3", UnitOfElectricCurrent.AMPERE, device_info_init),

        # --- REACTIVE (var) ---
        CozifyArraySensor(coordinator, entry, "r", 0, "Reactive Power Total", "var", device_info_init),
        CozifyArraySensor(coordinator, entry, "r", 1, "Reactive Power L1", "var", device_info_init),
        CozifyArraySensor(coordinator, entry, "r", 2, "Reactive Power L2", "var", device_info_init),
        CozifyArraySensor(coordinator, entry, "r", 3, "Reactive Power L3", "var", device_info_init),

        # --- KONFIGURAATION AND DIAGNOSTICS ---
        CozifyHANConfigSensor(coordinator, entry, "v", "Firmware Version", None, "mdi:git", EntityCategory.DIAGNOSTIC, device_info_init),
        CozifyHANConfigSensor(coordinator, entry, "price", "Fixed Electricity Price", "c/kWh", "mdi:cash", EntityCategory.DIAGNOSTIC, device_info_init),
        CozifyHANConfigSensor(coordinator, entry, "timezone", "Timezone", None, "mdi:clock-outline", EntityCategory.DIAGNOSTIC, device_info_init),
        CozifyHANConfigSensor(coordinator, entry, "online", "Cloud Connection", None, "mdi:cloud-check", EntityCategory.DIAGNOSTIC, device_info_init),
        CozifyHANConfigSensor(coordinator, entry, "fuse", "Main Fuse Size", "A", "mdi:fuse", EntityCategory.DIAGNOSTIC, device_info_init),
        CozifyHANConfigSensor(coordinator, entry, "eth_active", "Ethernet Active", None, "mdi:lan", EntityCategory.DIAGNOSTIC, device_info_init),
        CozifyHANConfigSensor(coordinator, entry, "eth_mode", "Ethernet Mode", None, "mdi:lan-check", EntityCategory.DIAGNOSTIC, device_info_init),
        CozifyHANConfigSensor(coordinator, entry, "wifi_active", "WiFi Active", None, "mdi:wifi", EntityCategory.DIAGNOSTIC, device_info_init),
        CozifyHANConfigSensor(coordinator, entry, "wifi_ssid", "WiFi SSID", None, "mdi:wifi-settings", EntityCategory.DIAGNOSTIC, device_info_init),
        CozifyHANConfigSensor(coordinator, entry, "wifi_mode", "WiFi Mode", None, "mdi:wifi-cog", EntityCategory.DIAGNOSTIC, device_info_init),
        CozifyHANConfigSensor(coordinator, entry, "wifi_channel", "WiFi Channel", None, "mdi:wifi-star", EntityCategory.DIAGNOSTIC, device_info_init),
        CozifyHANConfigSensor(coordinator, entry, "wifi_beacon", "WiFi Beacon Active", None, "mdi:broadcast", EntityCategory.DIAGNOSTIC, device_info_init),
        CozifyHANConfigSensor(coordinator, entry, "channel", "Update Channel", None, "mdi:package-variant", EntityCategory.DIAGNOSTIC, device_info_init),
        CozifyHANConfigSensor(coordinator, entry, "wifiIp", "WiFi IP Address", None, "mdi:wifi", EntityCategory.DIAGNOSTIC, device_info_init),
        CozifyHANConfigSensor(coordinator, entry, "ethIp", "Ethernet IP Address", None, "mdi:lan", EntityCategory.DIAGNOSTIC, device_info_init),

        # --- LASKENNALLISET MAKSIMIT ---
        CozifyMaxCurrentSensor(coordinator, entry, "Current Max L1", 0, device_info_init),
        CozifyMaxCurrentSensor(coordinator, entry, "Current Max L2", 1, device_info_init),
        CozifyMaxCurrentSensor(coordinator, entry, "Current Max L3", 2, device_info_init),
        CozifyPeakPowerSensor(coordinator, entry, device_info_init),
        CozifyPeakImportPowerSensor(coordinator, entry, device_info_init),
        CozifyPeakExportPowerSensor(coordinator, entry, device_info_init),

        # --- JÄRJESTELMÄTIEDOT ---
        CozifyTimestampSensor(coordinator, entry, device_info_init),
        CozifyDiagnosticSensor(coordinator, entry, "MAC Address", device_info_init.get("mac"), device_info_init),
        CozifyDiagnosticSensor(coordinator, entry, "Serial Number", device_info_init.get("serial"), device_info_init),
        CozifyDiagnosticSensor(coordinator, entry, "IP Address", host, device_info_init),
    ]
    async_add_entities(sensors)


class CozifyBaseEntity(CoordinatorEntity):
    def __init__(self, coordinator, entry, device_info_data=None):
        super().__init__(coordinator)
        self._entry = entry
        self._device_info_data = device_info_data or {}

    @property
    def device_info(self):
        data = self.coordinator.data or {}
        conf = data.get("config") or {}
        meter_id = data.get("meter_id") or {}

        version = conf.get("v") or self._device_info_data.get("version")
        serial = self._device_info_data.get("serial")
        mac = self._device_info_data.get("mac", self._entry.entry_id)

        manufacturer_id = meter_id.get("manufacturerId")
        device_type = meter_id.get("deviceType")
        fuse = (conf.get("m") or {}).get("f")

        # model: pelkkä HAN Reader
        model = "HAN Reader"

        # hw_version: valmistaja, tyyppi ja sulake
        hw_parts = []
        if manufacturer_id:
            hw_parts.append(manufacturer_id)
        if device_type:
            hw_parts.append(f"type {device_type}")
        if fuse:
            hw_parts.append(f"fuse {fuse}A")
        hw_version = ", ".join(hw_parts) or None

        return {
            "identifiers": {(DOMAIN, mac)},
            "name": self._device_info_data.get("name", "Cozify HAN"),
            "manufacturer": "Cozify",
            "model": model,
            "sw_version": version,
            "serial_number": serial,  # Tämä tuo sarjanumeron näkyviin listaukseen
            "configuration_url": f"http://{self._entry.data[CONF_HOST]}/ui",
        }


class CozifyEnergySensor(CozifyBaseEntity, SensorEntity):
    def __init__(self, coordinator, entry, key, name, device_info_data):
        super().__init__(coordinator, entry, device_info_data)
        self._key = key
        self._attr_name = f"Cozify HAN {name}"
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self._attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR
        self._attr_device_class = SensorDeviceClass.ENERGY
        self._attr_state_class = SensorStateClass.TOTAL_INCREASING

    @property
    def native_value(self):
        if not self.coordinator.data:
            return None
        try:
            return float(self.coordinator.data.get("realtime", {}).get(self._key, 0))
        except Exception:
            return None


class CozifyArraySensor(CozifyBaseEntity, SensorEntity):
    def __init__(self, coordinator, entry, key, idx, name, unit, device_info_data):
        super().__init__(coordinator, entry, device_info_data)
        self._key, self._idx = key, idx
        self._attr_name = f"Cozify HAN {name}"
        self._attr_unique_id = f"{entry.entry_id}_{key}_{idx}"
        self._attr_native_unit_of_measurement = unit
        self._attr_state_class = SensorStateClass.MEASUREMENT
        if unit == UnitOfPower.WATT:
            self._attr_device_class = SensorDeviceClass.POWER
        elif unit == UnitOfElectricPotential.VOLT:
            self._attr_device_class = SensorDeviceClass.VOLTAGE
        elif unit == UnitOfElectricCurrent.AMPERE:
            self._attr_device_class = SensorDeviceClass.CURRENT

    @property
    def native_value(self):
        if not self.coordinator.data:
            return None
        arr = self.coordinator.data.get("realtime", {}).get(self._key, [])
        try:
            return float(arr[self._idx]) if len(arr) > self._idx else 0.0
        except Exception:
            return 0.0


class CozifyMaxCurrentSensor(CozifyBaseEntity, SensorEntity):
    def __init__(self, coordinator, entry, name, idx, device_info_data):
        super().__init__(coordinator, entry, device_info_data)
        self._idx = idx
        self._attr_name = f"Cozify HAN {name}"
        self._attr_unique_id = f"{entry.entry_id}_max_i_{idx}"
        self._attr_native_unit_of_measurement = UnitOfElectricCurrent.AMPERE
        self._attr_device_class = SensorDeviceClass.CURRENT
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._max_val, self._day = 0.0, dt_util.now().day

    @property
    def native_value(self):
        if not self.coordinator.data:
            return self._max_val
        now = dt_util.now()
        if now.day != self._day:
            self._max_val, self._day = 0.0, now.day
        try:
            val = float(self.coordinator.data.get("realtime", {}).get("i", [])[self._idx])
            if val > self._max_val:
                self._max_val = val
        except Exception:
            pass
        return self._max_val


class CozifyPeakPowerSensor(CozifyBaseEntity, SensorEntity):
    def __init__(self, coordinator, entry, device_info_data):
        super().__init__(coordinator, entry, device_info_data)
        self._attr_name = "Cozify HAN DEPRECATED Power MAX"
        self._attr_unique_id = f"{entry.entry_id}_peak_p"
        self._attr_native_unit_of_measurement = UnitOfPower.WATT
        self._attr_device_class = SensorDeviceClass.POWER
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._max_p, self._day = 0.0, dt_util.now().day

    @property
    def native_value(self):
        if not self.coordinator.data:
            return self._max_p
        now = dt_util.now()
        if now.day != self._day:
            self._max_p, self._day = 0.0, now.day
        try:
            p_list = self.coordinator.data.get("realtime", {}).get("p", [])
            val = float(p_list[0]) if p_list else 0.0
            if val > self._max_p:
                self._max_p = val
        except Exception:
            pass
        return self._max_p

class CozifyPeakImportPowerSensor(CozifyBaseEntity, SensorEntity):
    def __init__(self, coordinator, entry, device_info_data):
        super().__init__(coordinator, entry, device_info_data)
        self._attr_name = "Cozify HAN Power Import MAX"
        self._attr_unique_id = f"{entry.entry_id}_peak_pi"
        self._attr_native_unit_of_measurement = UnitOfPower.WATT
        self._attr_device_class = SensorDeviceClass.POWER
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._max_pi, self._day = 0.0, dt_util.now().day

    @property
    def native_value(self):
        if not self.coordinator.data:
            return self._max_pi
        now = dt_util.now()
        if now.day != self._day:
            self._max_pi, self._day = 0.0, now.day
        try:
            p_list = self.coordinator.data.get("realtime", {}).get("pi", [])
            val = float(p_list[0]) if p_list else 0.0
            if val > self._max_pi:
                self._max_pi = val
        except Exception:
            pass
        return self._max_pi

class CozifyPeakExportPowerSensor(CozifyBaseEntity, SensorEntity):
    def __init__(self, coordinator, entry, device_info_data):
        super().__init__(coordinator, entry, device_info_data)
        self._attr_name = "Cozify HAN Power Export MAX"
        self._attr_unique_id = f"{entry.entry_id}_peak_pe"
        self._attr_native_unit_of_measurement = UnitOfPower.WATT
        self._attr_device_class = SensorDeviceClass.POWER
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._max_pe, self._day = 0.0, dt_util.now().day

    @property
    def native_value(self):
        if not self.coordinator.data:
            return self._max_pe
        now = dt_util.now()
        if now.day != self._day:
            self._max_pe, self._day = 0.0, now.day
        try:
            p_list = self.coordinator.data.get("realtime", {}).get("pe", [])
            val = float(p_list[0]) if p_list else 0.0
            if val > self._max_pe:
                self._max_pe = val
        except Exception:
            pass
        return self._max_pe

class CozifyHANConfigSensor(CozifyBaseEntity, SensorEntity):
    def __init__(self, coordinator, entry, key, name, unit, icon, cat, device_info_data):
        super().__init__(coordinator, entry, device_info_data)
        self._key = key
        self._attr_name = f"Cozify HAN {name}"
        self._attr_unique_id = f"{entry.entry_id}_conf_{key}"
        self._attr_native_unit_of_measurement = unit
        self._attr_icon = icon
        self._attr_entity_category = cat

    @property
    def native_value(self):
        if not self.coordinator.data:
            return None
        status_data = self.coordinator.data.get("status", {})
        if self._key in ["online", "channel", "wifiIp", "ethIp"]:
            val = status_data.get(self._key)
            if self._key == "online":
                return "Online" if val is True else "Offline"
            return val
        c = self.coordinator.data.get("config", {})
        if self._key == "price":
            return float(c.get("p", 0))
        if self._key == "timezone":
            return c.get("t")
        if self._key == "fuse":
            return c.get("m", {}).get("f")
        if self._key == "eth_active":
            return c.get("e", {}).get("e") is True
        if self._key == "eth_mode":
            return c.get("e", {}).get("n", {}).get("m")
        if self._key == "wifi_active":
            return c.get("w", {}).get("e") is True
        if self._key == "wifi_ssid":
            return c.get("w", {}).get("s")
        if self._key == "wifi_mode":
            return c.get("w", {}).get("n", {}).get("m")
        if self._key == "wifi_channel":
            return c.get("w", {}).get("z")
        if self._key == "wifi_beacon":
            return c.get("w", {}).get("b")
        return c.get(self._key)


class CozifyTimestampSensor(CozifyBaseEntity, SensorEntity):
    def __init__(self, coordinator, entry, device_info_data):
        super().__init__(coordinator, entry, device_info_data)
        self._attr_name = "Cozify HAN Last Update"
        self._attr_unique_id = f"{entry.entry_id}_ts"
        self._attr_device_class = SensorDeviceClass.TIMESTAMP
        self._attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def native_value(self):
        ts = self.coordinator.data.get("realtime", {}).get("ts") if self.coordinator.data else None
        try:
            return dt_util.utc_from_timestamp(float(ts)) if ts else None
        except Exception:
            return None


class CozifyDiagnosticSensor(CozifyBaseEntity, SensorEntity):
    def __init__(self, coordinator, entry, name, val, device_info_data):
        super().__init__(coordinator, entry, device_info_data)
        self._attr_name = f"Cozify HAN {name}"
        self._attr_unique_id = f"{entry.entry_id}_{name.lower().replace(' ', '_')}"
        self._val = val
        self._attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def native_value(self):
        return self._val
