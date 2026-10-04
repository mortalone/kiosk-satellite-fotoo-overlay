from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.util import slugify

from .const import DOMAIN
from .profile import (
    DEFAULT_FILL_BLUR_RADIUS,
    DEFAULT_FILL_SAMPLE_SIZE,
    FILL_BLUR_RADIUS,
    FILL_EDGE_BLUR,
    FILL_METHOD,
    FILL_METHODS,
    FILL_SAMPLE_SIZE,
    PROFILE_ID,
    PROFILE_NAME,
    SCREEN_RATIO,
    entry_fill_blur_radius,
    entry_fill_method,
    entry_fill_sample_size,
    entry_profile_id,
    entry_screen_ratio,
)


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
                    FILL_METHOD: str(user_input[FILL_METHOD]),
                    FILL_SAMPLE_SIZE: int(user_input[FILL_SAMPLE_SIZE]),
                    FILL_BLUR_RADIUS: int(user_input[FILL_BLUR_RADIUS]),
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
                    vol.Required(FILL_METHOD, default=FILL_EDGE_BLUR): vol.In(
                        FILL_METHODS
                    ),
                    vol.Required(
                        FILL_SAMPLE_SIZE,
                        default=DEFAULT_FILL_SAMPLE_SIZE,
                    ): vol.All(vol.Coerce(int), vol.Range(min=1, max=32)),
                    vol.Required(
                        FILL_BLUR_RADIUS,
                        default=DEFAULT_FILL_BLUR_RADIUS,
                    ): vol.All(vol.Coerce(int), vol.Range(min=0, max=30)),
                }
            ),
        )


class NatureFrameOptionsFlow(config_entries.OptionsFlow):
    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        SCREEN_RATIO,
                        default=entry_screen_ratio(self.config_entry),
                    ): vol.In(["16:9", "16:10", "4:3", "3:2"]),
                    vol.Required(
                        FILL_METHOD,
                        default=entry_fill_method(self.config_entry),
                    ): vol.In(FILL_METHODS),
                    vol.Required(
                        FILL_SAMPLE_SIZE,
                        default=entry_fill_sample_size(self.config_entry),
                    ): vol.All(vol.Coerce(int), vol.Range(min=1, max=32)),
                    vol.Required(
                        FILL_BLUR_RADIUS,
                        default=entry_fill_blur_radius(self.config_entry),
                    ): vol.All(vol.Coerce(int), vol.Range(min=0, max=30)),
                }
            ),
        )
