"""Constants for the SDmon integration."""

from __future__ import annotations

from typing import Final

DOMAIN: Final = "sdmon"
DEFAULT_NAME: Final = "SD Card"

CONF_ADD_DELAY: Final = "add_delay"
CONF_BINARY_PATH: Final = "binary_path"
CONF_DEVICE: Final = "device"
CONF_FILE_PATH: Final = "file_path"
CONF_SCAN_INTERVAL: Final = "scan_interval"
CONF_SOURCE: Final = "source"

SOURCE_FILE: Final = "file"
SOURCE_SUBPROCESS: Final = "subprocess"

DEFAULT_DEVICE: Final = "/dev/mmcblk0"
DEFAULT_BINARY_PATH: Final = "/config/sdmon/sdmon"
DEFAULT_FILE_PATH: Final = "/share/sdmon_status.json"
DEFAULT_SCAN_INTERVAL: Final = 300

ATTR_CARD_TYPE: Final = "card_type"
ATTR_DEVICE_PATH: Final = "device_path"
ATTR_ERROR: Final = "error"
ATTR_RAW: Final = "raw"
ATTR_SDMON_VERSION: Final = "sdmon_version"

HEALTH_KEY_ENDURANCE: Final = "enduranceRemainLifePercent"
HEALTH_KEY_USED: Final = "healthStatusPercentUsed"

SENSOR_DEFINITIONS: Final = {
    "health": {
        "key": "_health",
        "name": "Health",
        "unit": "%",
        "icon": "mdi:sd",
        "state_class": "measurement",
    },
    "total_erase_count": {
        "key": "totalEraseCount",
        "name": "Total Erase Count",
        "unit": "cycles",
        "icon": "mdi:counter",
        "state_class": "total_increasing",
    },
    "avg_erase_count": {
        "key": "avgEraseCount",
        "name": "Average Erase Count",
        "unit": "cycles",
        "icon": "mdi:counter",
        "state_class": "measurement",
    },
    "max_erase_count": {
        "key": "maxEraseCount",
        "name": "Max Erase Count",
        "unit": "cycles",
        "icon": "mdi:counter",
        "state_class": "measurement",
    },
    "power_up_count": {
        "key": "powerUpCount",
        "name": "Power-Up Count",
        "unit": "cycles",
        "icon": "mdi:power",
        "state_class": "total_increasing",
    },
    "abnormal_poweroff_count": {
        "key": "abnormalPowerOffCount",
        "name": "Abnormal Power-Off Count",
        "unit": "events",
        "icon": "mdi:power-plug-off",
        "state_class": "total_increasing",
    },
    "bad_block_count": {
        "key": "laterBadBlockCount",
        "name": "Bad Block Count",
        "unit": "blocks",
        "icon": "mdi:close-circle",
        "state_class": "measurement",
    },
    "power_on_count": {
        "key": "powerOnTimes",
        "name": "Power-On Count",
        "unit": "cycles",
        "icon": "mdi:power",
        "state_class": "total_increasing",
    },
    "manufacture_date": {
        "key": "manufactureYYMMDD",
        "name": "Manufacture Date",
        "unit": None,
        "icon": "mdi:calendar",
        "state_class": None,
    },
    "good_block_rate": {
        "key": "goodBlockRatePercent",
        "name": "Good Block Rate",
        "unit": "%",
        "icon": "mdi:check-circle",
        "state_class": "measurement",
    },
}
