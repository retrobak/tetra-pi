# MVP plan — TETRA RSSI visualizer

Scope guard: **RSSI detection only**. No TETRA payload decoding, no map/positioning.
Target hardware: **Raspberry Pi 2B**, **RTL2832U dongle**, **WS2812B 8-LED strip**.
Scan band: **380.5–383.0 MHz**. RSSI value = average over **4 s** (default handheld pulse interval).

Software basis: `docs/software.md`. Each phase lists concrete deliverables + a verification step.

---

## Phase 1 — Base OS on read-only filesystem
- Install **minimal Raspbian** on the Pi 2B.
- Configure the **read-only root filesystem** (overlayfs / boot-flag). All runtime writes must go to tmpfs; persistence is opt-in (reboot/reflash = normal reset).
- Enable Wi-Fi; document provisioning in `docs/` (SSID/psk via `wpa_supplicant`, headless setup).
- **Verify:** Pi boots, SSH/Wi-Fi up, root is read-only (`mount | grep ' / '` shows `ro`).

## Phase 2 — RTL-SDR hardware bring-up
- Blacklist the DVB-T kernel module: `dvb_usb_rtl28xxu` (prevents the kernel claiming the dongle).
- Add udev rule for non-root access (or plan to run SDR tooling as root).
- Install `rtl-sdr` (userspace tools + librtlsdr).
- Run `rtl_test -p` for a few minutes → record **PPM error** for the dongle; feed into scanner config.
- **Verify:** `rtl_test` opens the device with no "No supported devices" / permission error.

## Phase 3 — Build the scanning frontend
- Install build deps: `libfftw3-dev`, `libtclap-dev`, `librtlsdr-dev`, `libusb-1.0-0-dev`, `cmake`.
- Build **`rtl_power_fftw`** from source (`github.com/AD-Vega/rtl-power-fftw`) — this is what emits per-bin power/RSSI.
- Run a scan of **380.5–383.0 MHz** and confirm sensible power output.
- **Verify:** `rtl_power_fftw` produces power samples across the TETRA band; note a reference phone signal near ~900 MHz for later sanity-checking calibration.

## Phase 4 — SDR sampling process (RSSI engine)
- A long-running process that drives `rtl_power_fftw`, parses its output, and maintains:
  - **4-second rolling RSSI average** per scan.
  - **Dynamic noise-floor calibration** (track baseline, auto-adjust thresholds rather than hardcoding dBm).
- Expose the latest RSSI level to the rest of the system (local socket / file in tmpfs / shared state).
- **Verify:** with the ~900 MHz reference signal present, the averaged value rises measurably above the calibrated noise floor.

## Phase 5 — LED feedback (WS2812B)
- `pip install rpi_ws281x`; run as **root** (PWM/timing requirement).
- Implement **boot sequence** on the 8-LED strip.
- Map live RSSI level → LED pattern (e.g., number/color of lit LEDs) using the calibrated thresholds.
- **Verify:** boot animation plays; LEDs respond to a changing signal.

## Phase 6 — Flask visualization webserver
- `pip install flask numpy`.
- Single Flask app = visualization entrypoint; reads RSSI from the sampling process (Phase 4).
- Render current/averaged RSSI and noise floor. Keep it lightweight for the Pi 2B.
- **Verify:** open the web page, see live RSSI updates matching the LED behavior.

## Phase 7 — Documentation
- `docs/setup.md`: OS install, read-only fs, Wi-Fi provisioning.
- `docs/hardware.md`: RTL-SDR wiring/blacklist/udev, WS2812B wiring (GPIO, power, level shifting), PPM note.
- `docs/software.md`: already covers the package list.

## Open decisions (resolve before coding)
- How the sampling process and Flask app communicate (tmpfs file vs. local socket vs. in-process).
- Exact LED mapping (threshold buckets vs. continuous scale) once noise floor is characterized.
- Whether `rtl_power_fftw` is wrapped as a subprocess or replaced by a `pyrtlsdr`-based reader (keep `rtl_power_fftw` unless a reason emerges).
