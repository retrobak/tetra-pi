## Project goals
The goal of this project is to create a low-cost, portable system for receiving and visualizing TETRA signals using a Raspberry Pi and an RTL-SDR dongle. We only do RSSI detection, no decoding of the actual TETRA signals or map/port information.

The detection value should be calculated based on the RSSI levels received from the RTL-SDR dongle for a average of 4 seconds. That is the default pulse interval from the handheld devices.

## Basic software setup
- The Raspbian OS should be minimal and on a read-only filesystem
- Required software packages: rtl-sdr, python3, flask
- Python packages: numpy, rpi_ws281x
- Showing a boot sequence on the LED strip
- Visualizing RSSI levels on the LED strip

## Hardware
- Raspberry Pi 2B
- Cheap RTL-SDR USB dongle (e.g., RTL2832U)
- WS2812B 8-LED strip

## MVP
- Raspberry Pi 2B with Raspbian OS installed
- Cheap RTL-SDR USB dongle (e.g., RTL2832U)
- WS2812B 8-LED strip indicating RSSI levels
- Small webserver for visualizing RSSI levels
- Calibrate the noise floor dynamically
- For reference signal tune to a phone signal (like 900Mhz)
- Ensure the RTL-SDR dongle is properly configured and detected by the system
- Write documentation about how to setup, connect the Led strip, and wifi information
- Scan between 380.5 MHz and 383.0 MHz

## Future improvements
- Support for more advanced TETRA signal analysis
- Improved web interface for visualization
- Allow to configure RSSI thresholds through the web interface
- Create a sound alert on the webserver