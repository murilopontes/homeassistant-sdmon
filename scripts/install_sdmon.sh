#!/usr/bin/env bash
# Install sdmon binary for Home Assistant OS (aarch64/arm64).
set -euo pipefail

ARCH="$(uname -m)"
case "${ARCH}" in
  aarch64|arm64) ARCHIVE="sdmon-arm64.tar.gz" ;;
  armv7l|armhf) ARCHIVE="sdmon-armv7.tar.gz" ;;
  x86_64|amd64) ARCHIVE="sdmon-amd64.tar.gz" ;;
  i386|i686) ARCHIVE="sdmon-i386.tar.gz" ;;
  *)
    echo "Unsupported architecture: ${ARCH}" >&2
    exit 1
    ;;
esac

TARGET_DIR="${1:-/config/sdmon}"
URL="https://github.com/Ognian/sdmon/releases/download/latest/${ARCHIVE}"

mkdir -p "${TARGET_DIR}"
curl -fsSL "${URL}" | tar -xz -C "${TARGET_DIR}"
chmod +x "${TARGET_DIR}/sdmon"

echo "Installed sdmon to ${TARGET_DIR}/sdmon"
"${TARGET_DIR}/sdmon" /dev/mmcblk0 || true
