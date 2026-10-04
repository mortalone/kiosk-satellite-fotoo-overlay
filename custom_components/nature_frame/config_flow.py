from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.util import slugify

from .const import DOMAIN
from .profile import PROFILE_ID, PROFILE_NAME, SCREEN_RATIO, entry_profile_id


class NatureFrameConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    @staticmethod
    def async_get_options_flow(config_entry):
        return NatureFrameOptionsFlow()

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            name = str(user_input[PROFILE_NAME]).strip()
            profile_id = slugify(name) or "screen"

            if any(
                entry_profile_id(entry) == profile_id
                for entry in self._async_current_entries()
            ):
                return self.async_abort(reason="already_configured")

            await self.async_set_unique_id(f"{DOMAIN}_{profile_id}")
            self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title=f"Nature Frame · {name}",
                data={
                    PROFILE_NAME: name,
                    PROFILE_ID: profile_id,
                    SCREEN_RATIO: str(user_input[SCREEN_RATIO]),
                },
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(PROFILE_NAME, default="Default"): str,
                    vol.Required(SCREEN_RATIO, default="16:9"): vol.In(
                        ["16:9", "16:10", "4:3", "3:2"]
                    ),
                }
            ),
        )



class NatureFrameOptionsFlow(config_entries.OptionsFlow):
    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current = self.config_entry.options.get(
            SCREEN_RATIO,
            self.config_entry.data.get(SCREEN_RATIO, "16:9"),
        )
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(SCREEN_RATIO, default=current): vol.In(
                        ["16:9", "16:10", "4:3", "3:2"]
                    ),
                }
            ),
        )
