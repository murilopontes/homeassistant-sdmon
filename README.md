# SDmon SD Card Health

Home Assistant custom integration for monitoring industrial SD card health with [sdmon](https://github.com/Ognian/sdmon).

Supports Apacer, Kingston, SanDisk Industrial, Western Digital Purple, and other sdmon-compatible cards. Consumer cards usually do not expose CMD56 health data.

## Installation

### HACS

1. **HACS → Integrations → ⋮ → Custom repositories**
2. URL: `https://github.com/murilopontes/homeassistant-sdmon`
3. Category: **Integration**
4. Install **SDmon SD Card Health** and restart Home Assistant
5. **Settings → Devices & services → Add integration → SDmon SD Card Health**

### Manual

Copy `custom_components/sdmon` to `config/custom_components/` and restart.

## Home Assistant OS

The Core container cannot access `/dev/mmcblk0` directly. Use file mode:

```bash
curl -fsSL https://raw.githubusercontent.com/murilopontes/homeassistant-sdmon/main/scripts/install_sdmon.sh | bash
mkdir -p /config/scripts
curl -fsSL https://raw.githubusercontent.com/murilopontes/homeassistant-sdmon/main/scripts/haos_sdmon_cron.sh -o /config/scripts/haos_sdmon_cron.sh
chmod +x /config/scripts/haos_sdmon_cron.sh
```

On the host (`login` via the SSH add-on), schedule the script (e.g. every 5 minutes) and configure the integration with `/share/sdmon_status.json`.

## Options

| Option | Default |
|--------|---------|
| Data source | subprocess or file |
| sdmon binary | `/config/sdmon/sdmon` |
| Device | `/dev/mmcblk0` |
| `-a` delay | `false` |
| JSON file | `/share/sdmon_status.json` |
| Scan interval | `300` s |

## Entities

- `sensor.*_health` — remaining health (%)
- `sensor.*_status` — `ok` or `error`
- `sensor.*_total_bytes_written` — total bytes written by the host
- `sensor.*_physical_bytes_written` — physical NAND bytes written
- `binary_sensor.*_health_problem` — on when a problem is reported
- Additional metrics when supported by the card (erase counts, power-on, etc.)

## Changelog

See [CHANGELOG.md](CHANGELOG.md).

## License

GPL-2.0
