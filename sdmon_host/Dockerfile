ARG BUILD_FROM
FROM ${BUILD_FROM}

ARG BUILD_ARCH
RUN \
  case "${BUILD_ARCH}" in \
    aarch64|arm64) ARCHIVE="sdmon-arm64.tar.gz" ;; \
    armv7|armhf) ARCHIVE="sdmon-armv7.tar.gz" ;; \
    amd64|x86_64) ARCHIVE="sdmon-amd64.tar.gz" ;; \
    *) echo "Unsupported arch: ${BUILD_ARCH}" >&2; exit 1 ;; \
  esac \
  && curl -fsSL "https://github.com/Ognian/sdmon/releases/download/latest/${ARCHIVE}" \
    | tar xz -C /usr/local/bin sdmon \
  && chmod +x /usr/local/bin/sdmon

COPY run.sh /
RUN chmod +x /run.sh

CMD [ "/run.sh" ]
