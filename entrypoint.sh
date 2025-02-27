#!/bin/bash
set -e

# Fix ownership of mounted volumes (only if running as root)
if [ "$(id -u)" = "0" ]; then
    chown -R anonymousbot:anonymousbot /home/anonymousbot
    exec su anonymousbot -c "$*"
else
    exec "$@"
fi
