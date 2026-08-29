import argparse
import threading

from tetra_pi.config import Config
from tetra_pi.leds import create_led, led_loop
from tetra_pi.sampler import Sampler
from tetra_pi.state import RSSIState
from tetra_pi.web import create_app


def main():
    parser = argparse.ArgumentParser(description="TETRA RSSI visualizer")
    parser.add_argument("--demo", action="store_true", help="simulate SDR input without hardware")
    parser.add_argument("--host", default=None)
    parser.add_argument("--port", type=int, default=None)
    args = parser.parse_args()

    config = Config.from_env()
    if args.demo:
        config.demo = True
    if args.host:
        config.host = args.host
    if args.port:
        config.port = args.port

    state = RSSIState()
    sampler = Sampler(config, state)
    led = create_led(config)
    led.boot_sequence()

    threading.Thread(target=sampler.run, daemon=True).start()
    threading.Thread(target=led_loop, args=(led, state), daemon=True).start()

    app = create_app(state, config)
    app.run(host=config.host, port=config.port, threaded=True)


if __name__ == "__main__":
    main()
