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
    JSON_TEXT=$(printf '%s\n' "${OUTPUT_TEXT}" | sed -n '/^{/,$p')
    if [[ -z "${JSON_TEXT}" ]]; then
      bashio::log.warning "sdmon output did not contain JSON"
      rm -f "${OUTPUT}.tmp"
    else
      printf '%s\n' "${JSON_TEXT}" > "${OUTPUT}.tmp"
      mv "${OUTPUT}.tmp" "${OUTPUT}"
      bashio::log.info "Updated ${OUTPUT}"
    fi
  else
    bashio::log.warning "sdmon failed: ${OUTPUT_TEXT}"
    rm -f "${OUTPUT}.tmp"
  fi
  sleep "${SCAN_INTERVAL}"
done
