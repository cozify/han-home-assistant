from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .const import DOMAIN
# Lisätään tämä rivi, jotta sensor.py ladataan heti muistiin
from . import sensor 

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Asetetaan integraatio."""
    
    # Rekisteröidään kuuntelija
    entry.async_on_unload(entry.add_update_listener(update_listener))

    # TÄRKEÄÄ: Koska importtasimme 'sensor' ylhäällä, tämä ei enää "blokkaa"
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    
    return True

async def update_listener(hass: HomeAssistant, entry: ConfigEntry):
    """Päivittää asetukset lennosta."""
    await hass.config_entries.async_reload(entry.entry_id)

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Poistetaan integraatio."""
    return await hass.config_entries.async_unload_platforms(entry, ["sensor"])
