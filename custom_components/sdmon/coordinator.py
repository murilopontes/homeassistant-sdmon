"""Data update coordinator for SDmon."""

from __future__ import annotations

import asyncio
import json
import logging
from datetime import timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    CONF_ADD_DELAY,
    CONF_BINARY_PATH,
    CONF_DEVICE,
    CONF_FILE_PATH,
    CONF_SCAN_INTERVAL,
    CONF_SOURCE,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    SOURCE_FILE,
    SOURCE_SUBPROCESS,
)
from .parser import parse_sdmon_payload

_LOGGER = logging.getLogger(__name__)


class SDmonCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Fetch sdmon health data."""

    config_entry: ConfigEntry

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        scan_interval = entry.options.get(
            CONF_SCAN_INTERVAL,
            entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
        )
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=scan_interval),
        )
        self.config_entry = entry
        self.source = entry.data[CONF_SOURCE]
        self.device = entry.data.get(CONF_DEVICE)
        self.binary_path = entry.data.get(CONF_BINARY_PATH)
        self.file_path = entry.data.get(CONF_FILE_PATH)
        self.add_delay = entry.data.get(CONF_ADD_DELAY, False)

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            if self.source == SOURCE_SUBPROCESS:
                payload = await self._read_subprocess()
            else:
                payload = await self._read_file()
        except OSError as err:
            raise UpdateFailed(f"Failed to read sdmon data: {err}") from err
        except json.JSONDecodeError as err:
            raise UpdateFailed(f"Invalid sdmon JSON: {err}") from err

        parsed = parse_sdmon_payload(payload)
        if not parsed["success"] and parsed["error"]:
            _LOGGER.debug("sdmon reported error: %s", parsed["error"])
        return parsed

    async def _read_file(self) -> dict[str, Any]:
        if not self.file_path:
            raise UpdateFailed("File path is not configured")

        return await self.hass.async_add_executor_job(self._load_json_file, self.file_path)

    @staticmethod
    def _load_json_file(path: str) -> dict[str, Any]:
        with open(path, encoding="utf-8") as file:
            content = file.read()
        start = content.find("{")
        if start == -1:
            raise json.JSONDecodeError("Expected JSON object", content, 0)
        data = json.loads(content[start:])
        if not isinstance(data, dict):
            raise json.JSONDecodeError("Expected JSON object", content, 0)
        return data

    async def _read_subprocess(self) -> dict[str, Any]:
        if not self.binary_path:
            raise UpdateFailed("sdmon binary path is not configured")
        if not self.device:
            raise UpdateFailed("Device path is not configured")

        command = [self.binary_path, self.device]
        if self.add_delay:
            command.append("-a")

        process = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()
        output = stdout.decode("utf-8", errors="replace").strip()
        if not output:
            err = stderr.decode("utf-8", errors="replace").strip()
            raise HomeAssistantError(err or "sdmon returned no output")

        data = json.loads(output)
        if not isinstance(data, dict):
            raise json.JSONDecodeError("Expected JSON object", output, 0)
        return data
