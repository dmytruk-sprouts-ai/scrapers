#!/usr/bin/env bash
set -e

# ----------------------------
# Default configuration values
# ----------------------------
DISPLAY_NUM="${DISPLAY_NUM:-:99}"
SCREEN_RESOLUTION="${SCREEN_RESOLUTION:-1920x1080x24}"
VNC_PORT="${VNC_PORT:-5900}"
NOVNC_PORT="${NOVNC_PORT:-6080}"

DISPLAY_N="${DISPLAY_NUM#:}"  # strip the colon → "99"

# Remove stale lock from a previous container run
rm -f "/tmp/.X${DISPLAY_N}-lock"

# Start virtual X server
Xvfb "${DISPLAY_NUM}" -screen 0 "${SCREEN_RESOLUTION}" &

# Wait for X socket
until [ -e "/tmp/.X11-unix/X${DISPLAY_N}" ]; do
    sleep 0.1
done

# Start VNC server
x11vnc -display "${DISPLAY_NUM}" -forever -nopw -rfbport "${VNC_PORT}" -quiet &

# Start noVNC web bridge
websockify --web /usr/share/novnc "${NOVNC_PORT}" "localhost:${VNC_PORT}" &

# Run user command inside virtual display
DISPLAY="${DISPLAY_NUM}" exec "$@"