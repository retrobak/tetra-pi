# TETRA RSSI visualizer

Portable TETRA **RSSI-only** detector/visualizer for Raspberry Pi 2B + RTL-SDR (RTL2832U)
+ WS2812B 8-LED strip. Scans 380.5–383.0 MHz via `rtl_power_fftw`, averages RSSI over the
4s handheld pulse interval, auto-calibrates the noise floor, drives the LED strip, and serves
a small Flask page for live visualization.

## Install (on the Pi, image-build time — root fs is read-only at runtime)

```
sudo apt-get install rtl-sdr libfftw3-dev libtclap-dev librtlsdr-dev libusb-1.0-0-dev cmake python3 python3-pip
pip3 install -r requirements.txt
git clone https://github.com/AD-Vega/rtl-power-fftw.git
cd rtl-power-fftw && mkdir build && cd build && cmake .. && make && sudo make install
```

- Blacklist the DVB-T module so the dongle is free: `dvb_usb_rtl28xxu`.
- Run `rtl_test -p` for a few minutes and set `TETRA_PPM` to the measured correction.

## Run

```
python3 -m tetra_pi.app                 # real SDR (needs root for dongle + LEDs)
python3 -m tetra_pi.app --demo          # simulated input, no hardware required
```

Open `http://<pi-ip>:5000/`. LEDs show live RSSI level; the web page polls `/api/state`.

## Config (environment, prefix `TETRA_`)

`TETRA_PPM`, `TETRA_GAIN_TENTHS_DB`, `TETRA_INTEGRATION_S`, `TETRA_FREQ_START_HZ`,
`TETRA_FREQ_END_HZ`, `TETRA_LED_COUNT`, `TETRA_LED_GPIO`, `TETRA_NOISE_FLOOR_WINDOW`,
`TETRA_EXPECTED_DYNAMIC_RANGE_DB`, `TETRA_HOST`, `TETRA_PORT`.
