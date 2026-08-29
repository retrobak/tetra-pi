#!/bin/sh
set -e
export PYTHONPATH=/opt/tetra-pi
export TETRA_PPM="${TETRA_PPM:-0}"
export TETRA_HOST="${TETRA_HOST:-0.0.0.0}"
export TETRA_PORT="${TETRA_PORT:-5000}"
cd /opt/tetra-pi
exec /usr/bin/python3 -m tetra_pi.app
