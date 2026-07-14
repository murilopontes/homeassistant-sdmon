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
  if "${CMD[@]}" > "${OUTPUT}.tmp"; then
    mv "${OUTPUT}.tmp" "${OUTPUT}"
    bashio::log.info "Updated ${OUTPUT}"
  else
    bashio::log.warning "sdmon failed; keeping previous output"
    rm -f "${OUTPUT}.tmp"
  fi
  sleep "${SCAN_INTERVAL}"
done
