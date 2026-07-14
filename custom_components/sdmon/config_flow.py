"""Config flow for SDmon."""

from __future__ import annotations

import asyncio
import json
import logging
import os
import re
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector

from .const import (
    CONF_ADD_DELAY,
    CONF_BINARY_PATH,
    CONF_DEVICE,
    CONF_FILE_PATH,
    CONF_SCAN_INTERVAL,
    CONF_SOURCE,
    DEFAULT_BINARY_PATH,
    DEFAULT_DEVICE,
    DEFAULT_FILE_PATH,
    DEFAULT_NAME,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    SOURCE_FILE,
    SOURCE_SUBPROCESS,
)

_LOGGER = logging.getLogger(__name__)

SOURCE_OPTIONS = [
    selector.SelectOptionDict(value=SOURCE_SUBPROCESS, label="Run sdmon binary"),
    selector.SelectOptionDict(value=SOURCE_FILE, label="Read JSON file"),
]


class SDmonConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for SDmon."""

    VERSION = 1

    def __init__(self) -> None:
        self._data: dict[str, Any] = {}

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            self._data = user_input
            if user_input[CONF_SOURCE] == SOURCE_SUBPROCESS:
                return await self.async_step_subprocess()
            return await self.async_step_file()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_NAME, default=DEFAULT_NAME): str,
                    vol.Required(CONF_SOURCE, default=SOURCE_SUBPROCESS): selector.SelectSelector(
                        selector.SelectSelectorConfig(options=SOURCE_OPTIONS)
                    ),
                }
            ),
            description_placeholders={
                "sdmon": "[sdmon](https://github.com/Ognian/sdmon)",
            },
        )

    async def async_step_subprocess(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            binary_path = user_input[CONF_BINARY_PATH]
            device = user_input[CONF_DEVICE]
            add_delay = user_input[CONF_ADD_DELAY]

            if not await self.hass.async_add_executor_job(os.path.isfile, binary_path):
                errors[CONF_BINARY_PATH] = "binary_not_found"
            elif not await self.hass.async_add_executor_job(os.access, binary_path, os.X_OK):
                errors[CONF_BINARY_PATH] = "binary_not_executable"
            else:
                try:
                    await self._test_subprocess(binary_path, device, add_delay)
                except json.JSONDecodeError:
                    errors["base"] = "invalid_json"
                except OSError as err:
                    _LOGGER.debug("sdmon subprocess test failed: %s", err)
                    errors["base"] = "cannot_connect"
                except Exception as err:  # noqa: BLE001
                    _LOGGER.exception("Unexpected sdmon test error: %s", err)
                    errors["base"] = "unknown"

            if not errors:
                return await self._create_entry(
                    {
                        **self._data,
                        CONF_BINARY_PATH: binary_path,
                        CONF_DEVICE: device,
                        CONF_ADD_DELAY: add_delay,
                        CONF_SCAN_INTERVAL: user_input[CONF_SCAN_INTERVAL],
                    }
                )

        return self.async_show_form(
            step_id="subprocess",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_BINARY_PATH, default=DEFAULT_BINARY_PATH): str,
                    vol.Required(CONF_DEVICE, default=DEFAULT_DEVICE): str,
                    vol.Required(CONF_ADD_DELAY, default=False): bool,
                    vol.Required(
                        CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL
                    ): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=60,
                            max=86400,
                            step=60,
                            mode=selector.NumberSelectorMode.BOX,
                            unit_of_measurement="s",
                        )
                    ),
                }
            ),
            errors=errors,
        )

    async def async_step_file(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            file_path = user_input[CONF_FILE_PATH]
            if not await self.hass.async_add_executor_job(os.path.isfile, file_path):
                errors[CONF_FILE_PATH] = "file_not_found"
            else:
                try:
                    await self.hass.async_add_executor_job(self._load_json_file, file_path)
                except (OSError, json.JSONDecodeError):
                    errors[CONF_FILE_PATH] = "invalid_json"

            if not errors:
                return await self._create_entry(
                    {
                        **self._data,
                        CONF_FILE_PATH: file_path,
                        CONF_SCAN_INTERVAL: user_input[CONF_SCAN_INTERVAL],
                    }
                )

        return self.async_show_form(
            step_id="file",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_FILE_PATH, default=DEFAULT_FILE_PATH): str,
                    vol.Required(
                        CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL
                    ): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=60,
                            max=86400,
                            step=60,
                            mode=selector.NumberSelectorMode.BOX,
                            unit_of_measurement="s",
                        )
                    ),
                }
            ),
            errors=errors,
        )

    async def _create_entry(self, data: dict[str, Any]) -> FlowResult:
        unique_id = self._build_unique_id(data)
        await self.async_set_unique_id(unique_id)
        self._abort_if_unique_id_configured()
        return self.async_create_entry(title=data[CONF_NAME], data=data)

    @staticmethod
    def _build_unique_id(data: dict[str, Any]) -> str:
        if data[CONF_SOURCE] == SOURCE_SUBPROCESS:
            return re.sub(r"[^a-zA-Z0-9]+", "_", data.get(CONF_DEVICE, DEFAULT_DEVICE))
        return re.sub(r"[^a-zA-Z0-9]+", "_", data.get(CONF_FILE_PATH, DEFAULT_FILE_PATH))

    @staticmethod
    def _load_json_file(path: str) -> dict[str, Any]:
        with open(path, encoding="utf-8") as file:
            data = json.load(file)
        if not isinstance(data, dict):
            raise json.JSONDecodeError("Expected JSON object", str(data), 0)
        return data

    async def _test_subprocess(self, binary_path: str, device: str, add_delay: bool) -> None:
        command = [binary_path, device]
        if add_delay:
            command.append("-a")
        process = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, _stderr = await process.communicate()
        output = stdout.decode("utf-8", errors="replace").strip()
        if not output:
            raise OSError("sdmon returned no output")
        data = json.loads(output)
        if not isinstance(data, dict):
            raise json.JSONDecodeError("Expected JSON object", output, 0)

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> SDmonOptionsFlow:
        return SDmonOptionsFlow(config_entry)


class SDmonOptionsFlow(config_entries.OptionsFlow):
    """Handle options."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self._config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current = self._config_entry.options.get(
            CONF_SCAN_INTERVAL,
            self._config_entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
        )
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_SCAN_INTERVAL, default=current): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=60,
                            max=86400,
                            step=60,
                            mode=selector.NumberSelectorMode.BOX,
                            unit_of_measurement="s",
                        )
                    ),
                }
            ),
        )
