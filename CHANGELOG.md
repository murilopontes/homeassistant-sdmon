# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2026-07-14

### Added

- `sensor.*_total_bytes_written` — total host bytes written (`bytesWrittenCount` or `writeAllSectNum × 512`)
- `sensor.*_physical_bytes_written` — physical NAND bytes written (parses values like `0.58TB` from `phyWrGBNum`)

### Changed

- Sensor definitions with multiple JSON field candidates now resolve the first available value
- Data-size sensors use Home Assistant `device_class: data_size` for automatic unit formatting

## [1.0.0] - 2026-07-14

### Added

- Home Assistant integration for [sdmon](https://github.com/Ognian/sdmon) SD card health monitoring
- Config flow with subprocess or file data source
- Sensors: health, status, erase counts, power-on counts, bad blocks, manufacture date, and more when supported by the card
- `binary_sensor.*_health_problem` when health data is missing or below threshold
- Longsys card support via `remainLifeTime` health parsing
- Tolerance for non-JSON text before `{` in status files (e.g. `Trying sandisk...` prefix)
- Privileged `sdmon_host` Home Assistant add-on for HAOS SD card access (`/share/sdmon_status.json`)
- Install scripts for HAOS (`scripts/install_sdmon.sh`, `scripts/haos_sdmon_cron.sh`)

[1.1.0]: https://github.com/murilopontes/homeassistant-sdmon/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/murilopontes/homeassistant-sdmon/releases/tag/v1.0.0
