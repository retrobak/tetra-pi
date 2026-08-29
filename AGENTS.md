# AGENTS.md

Compact guidance for working in this repository. Verify against `docs/project.md` first.

## What this project is
- Low-cost, portable **TETRA RSSI receiver/visualizer** built on a **Raspberry Pi 2B + RTL-SDR (RTL2832U) dongle + WS2812B 8-LED strip**.
- **RSSI detection only** — no decoding of TETRA payloads, no map/positional data. Do not add TETRA protocol decoding unless scope changes.
- Output: a Flask webserver for visualization + LED-strip feedback (boot sequence + live RSSI levels), with automatic RSSI calibration. Reference tuning target is a nearby ~900 MHz phone signal.

## Target environment (drives every decision)
- **Raspberry Pi 2B** (ARM, limited RAM/CPU) — keep code lightweight; avoid heavy deps.
- **Minimal Raspbian on a read-only filesystem** — code must run read-only; write config/cache to tmpfs or make persistence explicit. Reboot/reflash is the normal "reset".
- Required system packages: `rtl-sdr`, `python3`, `flask`.
- Required Python packages: `numpy`, `rpi_ws281x`.

## Hardware/setup gotchas an agent will likely miss
- **RTL-SDR dongle**: the default Linux DVB-T kernel module claims the device. It must be blacklisted (`dvb_usb_rtl28xxu`) and udev permissions set so `rtl-sdr` userspace tools can open it. Verify the dongle is detected (`rtl_test`) before assuming SDR code works.
- **WS2812B / `rpi_ws281x`**: needs root (or `gpio` group) and precise GPIO timing; the LED library typically takes over the PWM peripheral. Don't assume it runs unprivileged or alongside other PWM users.
- **Calibration is automatic** per the MVP — prefer deriving thresholds from sampled signal ranges rather than hardcoding dBm values.

## Architecture (as implemented)
- Single Python package `tetra_pi/`, run as one process: `python3 -m tetra_pi.app`.
- A background **sampler thread** drives `rtl_power_fftw` (subprocess), parses its two-column
  `freq power` stdout (lines starting with `#` and blank lines separate scans), and feeds a
  peak-per-scan value into the **NoiseFloor** calibrator (`tetra_pi/calibration.py`). RSSI value
  is the max PSD in the 380.5–383.0 MHz band, averaged over the 4s integration window.
- `tetra_pi/state.py` holds the shared `RSSIState` (thread-safe). A **LED thread**
  (`tetra_pi/leds.py`) renders live level; the **Flask app** (`tetra_pi/web.py`, route
  `/api/state`) serves visualization. `flask` and `rpi_ws281x` are optional guarded imports, so
  `python3 -m tetra_pi.app --demo` runs the whole pipeline with simulated input (no hardware).
- `tetra_pi/config.py` reads all tuning from `TETRA_*` env vars (important on the read-only fs:
  configure at image-build time, not at runtime).

## Conventions
- Document hardware setup, LED wiring, and Wi-Fi provisioning (part of MVP deliverable) in `docs/`.
- Keep the RSSI-only scope: no TETRA decoding. Add new signal processing in `tetra_pi/calibration.py`
  or `tetra_pi/parser.py`, not in the web/LED layer.
- Core logic (parser, calibration, config, LED mapping) is stdlib-only and unit-tested under
  `tests/`; run with `python3 -m unittest discover -s tests`. Do not add deps that break those tests.
