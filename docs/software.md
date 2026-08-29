# Required software

Sources of truth: `docs/project.md`, cross-referenced with the community BluPi scanner
(`github.com/jj15warrior/blupi`, RTL-SDR branch) the project is based on. Target is a
**Raspberry Pi 2B** on **minimal Raspbian / read-only filesystem** — build anything from
source at image-build time, not at runtime.

## SDR scanning frontend (this is what actually produces RSSI)
- `rtl_power_fftw` — C++ scanner used as the frontend to rtl-sdr; emits power/RSSI per
  frequency bin that the Python side filters and averages. **Build from source**
  (`github.com/AD-Vega/rtl-power-fftw`). This is the component `project.md` did not name.
- Build dependencies for `rtl_power_fftw`:
  - `libfftw3-dev`
  - `libtclap-dev`
  - `librtlsdr-dev`
  - `libusb-1.0-0-dev`
  - `cmake`
- `rtl-sdr` (librtlsdr + userspace tools `rtl_test`, `rtl_sdr`). BluPi recommends the
  keenerd experimental branch (`github.com/keenerd/rtl-sdr`); the standard package may
  suffice — verify against `rtl_test`.

## System (apt) packages — from project.md
- `rtl-sdr`
- `python3`

## Python (pip) packages — from project.md
- `flask` — webserver serving the RSSI visualization.
- `numpy` — computes the 4-second RSSI average (default TETRA handheld pulse interval).
- `rpi_ws281x` — drives the WS2812B 8-LED strip (boot sequence + live RSSI levels).

## Setup notes / gotchas
- RTL-SDR dongle: blacklist the `dvb_usb_rtl28xxu` kernel module and set udev permissions,
  otherwise `rtl-sdr` userspace tools can't open the device.
- Run `rtl_test -p` for a few minutes to measure the receiver's PPM error correction and
  feed it into the scanner config.
- `rpi_ws281x` needs root (or `gpio` group) and PWM access.
- Scan band for this project is **380.5–383.0 MHz** (project.md), not the wider emergency
  bands BluPi defaults to.
- The Airspy variant (`N0edL/blupi-airspy`) is **not** for the Pi and not for RTL-SDR — only
  relevant if the dongle is ever swapped for an Airspy Mini.
