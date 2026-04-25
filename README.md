[![Current release](https://img.shields.io/github/v/release/cozify/han-home-assistant?style=plastic&label=Current%20release&include_prereleases)](https://github.com/cozify/han-home-assistant)
[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg?style=plastic)](https://github.com/hacs/integration)
[![Stars](https://img.shields.io/github/stars/cozify/han-home-assistant?style=plastic)](https://github.com/cozify/han-home-assistant/stargazers)
[![Last Commit](https://img.shields.io/github/last-commit/cozify/han-home-assistant?style=plastic)](https://github.com/cozify/han-home-assistant/commits/main)
[![License](https://img.shields.io/github/license/cozify/han-home-assistant?style=plastic)](https://github.com/cozify/han-home-assistant/blob/main/LICENSE)
<br />

If you find this integration useful, we would be grateful if you could add a star ⭐. You can do it here: <https://github.com/cozify/han-home-assistant>

## NOTE! - Change in version 1.0.14

Sensor "Cozify HAN Power MAX" will be deprecated in future versions and replaced by "Cozify HAN Power Import MAX" and "Cozify HAN Power Export MAX". Also "Cozify HAN Power Total" and "Cozify HAN Power L1-L3" will be deprecated and removed in future versions and replaced similarily with "Cozify HAN Power Import" & "Cozify HAN Power Import L1-L3" and "Cozify HAN Power Export" and "Cozify HAN Power Export L1-L3"

# Cozify HAN for Home Assistant

Custom integration for Home Assistant to fetch real-time energy data from the Cozify HAN (HAN/P1 meter). The full Cozify HAN API is available at <https://cozify.github.io/han-firmware/han-1.0.html> Using it, you can create additional integrations or other solutions even without Home Assistant. Please note that starting from FW version 1.0.1.7, the Cozify HAN device also includes a local user interface at <http://HAN-IP/ui>

## Features

- **Real-time Power:** Total and phase-specific (L1, L2, L3) power consumption.
- **Voltage & Current:** Per-phase monitoring.
- **Reactive Power:** Support for reactive power monitoring (VAr).
- **Energy Statistics:** Total imported and exported energy for Home Assistant Energy Dashboard.

## Installation

### Cozify HAN installation (HACS Default)

1. Open HACS from the Home Assistant sidebar.
2. Type into the search field at the top (Search) or click the + (Plus) button in the bottom-right corner and search for: Cozify HAN.
3. Click the Cozify HAN search result.
4. Select Integration as the category and click Add.
5. Click Download in the bottom-right corner.
6. Restart Home Assistant so that the new files are loaded.

### Step 2: Enable integration

1. Go to Settings -> Devices and services.
2. Click Add integration.
3. Search for "Cozify HAN".
4. Enter the IP address of your device (e.g. 192.168.1.10) and click Submit.

![Example view of the Cozify HAN Home Assistant page](images/Cozify_HAN_Home_Assistant_INFO.png)

## Electricity Price Tracking (Example)

You can use the `sensor.cozify_han_power_total` sensor created by the integration to calculate the electricity price in real time. We recommend using the **Riemann sum integral** sensor to convert the instantaneous price (c/h) into cumulative consumption (c), which you can track with **Utility Meter** on a daily, weekly, and monthly basis.

## Automation - Blueprints

- Download via Home Automation Settings - Automation & scenes - Blueprints - Import Blueprint - "Enter the following address"

- Blueprint base for automation that warns when any phase exceeds the specified current limit. <https://github.com/cozify/han-home-assistant/blob/main/blueprints/overcurrent_notification.yaml>
- Blueprint base for automation that warns when any phase exceeds the specified power limit. <https://github.com/cozify/han-home-assistant/blob/main/blueprints/total_power_notification.yaml>

## Cozify HAN

Cozify HAN is a Nordic, Finnish key-flag product that brings real-time data from the electricity meter's HAN/P1 interface to the local network, cloud and smart systems. It is designed specifically for northern conditions, easy self-installation and extensive integration (RestAPI, MQTT and Modbus) for energy optimization, load management and automation.

### Key features

- Real-time measurement data: instantaneous power (W/kW), voltage (V), current (A) and cumulative consumption figures (kWh) per phase, all data coming from the HAN/P1 bus

- Supports Ethernet (RJ45) and WiFi connection; possibility to replace the original antenna with an RP-SMA external antenna for better range
- Built-in HTTP OpenAPI server (/meter), MQTT broadcast and Modbus (TCP) interfaces for B2B integrations
- Works with Android and iOS applications, OTA firmware updates ensure further development and security
- Designed to operate in Nordic conditions –40 °C … +60 °C and with the same IP rating as the electricity meter

### What the device offers to the user

- Accurate real-time visibility into electricity consumption and production

- Phase-specific load views make it easy to identify overload risks and balance loads
- Better opportunity to utilize hourly and quarter-hourly prices and real-time control in smart charging and heating
- Integrates with existing home automation platforms (e.g. Home Assistant) and energy management systems (EVCC.io, etc.). Integration possibilities are limitless via Modbus (TCP), MQTT and RestAPI interfaces. More interfaces in the future.

### Technical data

- Connections: RJ12 (HAN/P1), RJ45 (Ethernet), WiFi , USB‑C (additional power), RP-SMA (additional WiFi antenna)

- Interfaces: OpenAPI (HTTP, /meter), MQTT (JSON‑payload), Modbus TCP (registers)
- Operating environment: −40 °C … +60 °C; housing and connections according to electricity meter class

### Installation and commissioning

- Self-installation; placed next to the electricity meter and attached with e.g. double-sided tape

- If the meter is in a metal cabinet, an Ethernet connection or an external RP-SMA antenna is recommended to ensure a reliable connection.

### Development and Support

This is a community-driven integration. If you find any bugs or want to improve it further, please create an "Issue" on GitHub.

---
*Note: This integration is officially supported by Cozify Oy.*
