# Setup: flashing, read-only root, and auto-start

Goal: a Pi 2B that boots straight into the TETRA RSSI app, with a **read-only root
filesystem** so a reboot/reflash is the normal "reset". Do every build step **before**
enabling read-only, because after that point all writes to `/` are discarded on reboot.

## 1. Flash Raspberry Pi OS Lite (32-bit)

- Use **Raspberry Pi OS Lite (32-bit)** — works on all Pi 2B revisions (the original Pi 2 is
  ARMv7; the 32-bit Lite image is the safe choice). Get it via **Raspberry Pi Imager**.
- In Imager, pick the Lite image, then open **Settings** (gear) and pre-configure:
  - hostname (e.g. `tetra-pi`)
  - user + password (or SSH key)
  - **enable SSH**
  - **configure Wi-Fi (SSID/PSK)** — do this now; it lands on the writable `/boot` partition,
    which stays writable after read-only is enabled. Runtime Wi-Fi changes are lost otherwise.
  - locale / timezone
- Write the SD card.

## 2. First boot — build-time setup (fs still writable)

SSH in (`ssh <user>@tetra-pi.local`). Run as root (`sudo -i`).

### System packages + free the dongle
```
apt-get update
apt-get install -y rtl-sdr libfftw3-dev libtclap-dev librtlsdr-dev libusb-1.0-0-dev cmake python3 python3-pip
echo 'blacklist dvb_usb_rtl28xxu' > /etc/modprobe.d/rtl-sdr-blacklist.conf
```
The blacklist stops the kernel DVB-T driver from claiming the RTL2832U so `rtl-sdr`
userspace tools (and `rtl_power_fftw`) can open it.

### Build `rtl_power_fftw` (built from source — see `docs/software.md`)
```
git clone https://github.com/AD-Vega/rtl-power-fftw.git
cd rtl-power-fftw && mkdir build && cd build && cmake .. && make && make install
ldconfig
```

### Install the app
```
mkdir -p /opt/tetra-pi
cp -r tetra_pi requirements.txt deploy /opt/tetra-pi/
pip3 install -r /opt/tetra-pi/requirements.txt
cp /opt/tetra-pi/deploy/tetra-pi.service /etc/systemd/system/
cp /opt/tetra-pi/deploy/99-rtlsdr.rules /etc/udev/rules.d/   # optional, we run as root
chmod +x /opt/tetra-pi/start.sh
systemctl daemon-reload
systemctl enable tetra-pi
```
The `systemctl enable` writes its symlink into the base layer, so the service keeps
auto-starting after the root fs becomes read-only.

### Calibrate PPM
```
rtl_test -p     # run a few minutes, note the ppm correction
```
Set it persistently by editing `Environment=TETRA_PPM=...` in
`/etc/systemd/system/tetra-pi.service` (or pass `TETRA_PPM` in the environment). Other tuning
via `TETRA_*` env vars — see `README.md`.

## 3. Enable read-only root (OverlayFS)

Use raspi-config (interactive, unambiguous across versions):
```
raspi-config
```
Performance Options → **Overlay File System** → Enable → also enable the **read-only boot
option** → Reboot.

(For automation you can try `sudo raspi-config nonint do_overlayfs 0`, but verify the flag
polarity on your specific image before relying on it.)

After reboot, `/` is read-only. `/boot` stays writable, so you can re-run `raspi-config` later
to disable overlay for maintenance. The app writes nothing to disk (all state is in-memory;
any tmpfs writes are discarded on reboot) — exactly the intended reset behavior.

## 4. Verify auto-start

With the dongle + WS2812B strip connected, after reboot:
```
systemctl status tetra-pi
journalctl -u tetra-pi -f
```
Open `http://tetra-pi.local:5000/`. The LED strip should play its boot sequence, then reflect
live RSSI. The web page polls `/api/state`.

## Maintenance

- **Change config:** disable overlay via `raspi-config`, reboot, edit, re-enable overlay.
- **Logs:** journald output lands in the overlay tmpfs and is lost on reboot. For persistent
  logs, point the service at a tmpfs or external store (out of scope for MVP).
