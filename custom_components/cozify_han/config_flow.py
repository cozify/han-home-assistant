import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST
from homeassistant.core import callback
from .const import DOMAIN

class CozifyHanConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Cozify HAN asennusvalikko."""
    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Palauttaa asetusten hallinnan."""
        return CozifyOptionsFlowHandler(config_entry)

    async def async_step_user(self, user_input=None):
        """Pyydetään käyttäjältä IP-osoite."""
        if user_input is not None:
            # Luodaan entry. Title on se, mikä näkyy integraatiolistassa.
            return self.async_create_entry(
                title=f"Cozify HAN ({user_input[CONF_HOST]})", 
                data=user_input
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_HOST): str,
            }),
        )
        
# Oletusarvo
DEFAULT_INTERVAL = 10

class CozifyOptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Optional(
                    "update_interval", 
                    default=self.config_entry.options.get("update_interval", DEFAULT_INTERVAL)
                ): vol.All(vol.Coerce(int), vol.Range(min=5, max=60)),
            })
        )
        
        
class CozifyOptionsFlowHandler(config_entries.OptionsFlow):
    """Käsittelee integraation asetusten muuttamista."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Alustetaan asetusten hallinta."""
        super().__init__() # Tämä on tärkeä, jotta isäntäluokka toimii
        # Meidän ei tarvitse asettaa self.config_entryä, super hoitaa sen

    async def async_step_init(self, user_input=None):
        """Ensimmäinen vaihe asetuksissa."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        # Haetaan nykyinen arvo. Huom: self.config_entry on nyt käytettävissä superin kautta
        current_interval = self.config_entry.options.get("update_interval", 5)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Optional(
                    "update_interval", 
                    default=current_interval
                ): vol.All(vol.Coerce(int), vol.Range(min=5, max=60)),
            })
        )
