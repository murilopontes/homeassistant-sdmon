#!/usr/bin/env bash
# Cron helper for Home Assistant OS: write sdmon JSON for file-based integration mode.
set -euo pipefail

DEVICE="${SDMON_DEVICE:-/dev/mmcblk0}"
BINARY="${SDMON_BINARY:-/config/sdmon/sdmon}"
OUTPUT="${SDMON_OUTPUT:-/share/sdmon_status.json}"
DELAY="${SDMON_DELAY:-}"

mkdir -p "$(dirname "${OUTPUT}")"
CMD=("${BINARY}" "${DEVICE}")
if [[ "${DELAY}" == "1" || "${DELAY}" == "true" ]]; then
  CMD+=("-a")
fi

"${CMD[@]}" > "${OUTPUT}.tmp"
mv "${OUTPUT}.tmp" "${OUTPUT}"
