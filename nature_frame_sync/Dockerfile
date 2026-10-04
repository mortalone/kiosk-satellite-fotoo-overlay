FROM ghcr.io/home-assistant/base:3.23

ARG BUILD_VERSION="0.2.0"
ARG BUILD_ARCH=""

RUN apk add --no-cache python3 py3-pillow ca-certificates

COPY run.sh /run.sh
COPY sync.py /app/sync.py
RUN chmod a+x /run.sh

LABEL \
    io.hass.version="${BUILD_VERSION}" \
    io.hass.type="app" \
    io.hass.arch="${BUILD_ARCH}" \
    org.opencontainers.image.title="Nature Frame Sync" \
    org.opencontainers.image.description="Sync curated nature illustrations into Home Assistant Media." \
    org.opencontainers.image.source="https://github.com/mortalone/kiosk-satellite-fotoo-overlay" \
    org.opencontainers.image.licenses="MIT"

CMD ["/run.sh"]
