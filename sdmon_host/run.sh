#!/usr/bin/with-contenv bashio
set -euo pipefail

DEVICE="$(bashio::config 'device')"
ADD_DELAY="$(bashio::config 'add_delay')"
SCAN_INTERVAL="$(bashio::config 'scan_interval')"
OUTPUT="$(bashio::config 'output_file')"

CMD=(/usr/local/bin/sdmon "${DEVICE}")
if [[ "${ADD_DELAY}" == "true" ]]; then
  CMD+=("-a")
fi

bashio::log.info "Starting sdmon host runner on ${DEVICE}"
mkdir -p "$(dirname "${OUTPUT}")"

while true; do
  if OUTPUT_TEXT="$("${CMD[@]}" 2>&1)"; then
    printf '%s\n' "${OUTPUT_TEXT}" > "${OUTPUT}.tmp"
    mv "${OUTPUT}.tmp" "${OUTPUT}"
    bashio::log.info "Updated ${OUTPUT}"
  else
    bashio::log.warning "sdmon failed: ${OUTPUT_TEXT}"
    rm -f "${OUTPUT}.tmp"
  fi
  sleep "${SCAN_INTERVAL}"
done
