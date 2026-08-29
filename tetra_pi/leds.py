import time
from typing import Optional

from tetra_pi.config import Config
from tetra_pi.state import RSSIState


class NullLED:
    def begin(self):
        pass

    def boot_sequence(self):
        pass

    def render(self, level_normalized: float):
        pass

    def close(self):
        pass


class WS2812B:
    def __init__(self, config: Config):
        from rpi_ws281x import PixelStrip, Color
        self._Color = Color
        self.strip = PixelStrip(
            config.led_count,
            config.led_gpio,
            freq_hz=800000,
            dma=config.led_dma,
            invert=config.led_invert,
            brightness=config.led_brightness,
            channel=config.led_channel,
        )
        self.count = config.led_count
        self.strip.begin()

    def boot_sequence(self):
        for i in range(self.count):
            self.strip.setPixelColor(i, self._Color(0, 0, 255))
            self.strip.show()
            time.sleep(0.08)
        for i in range(self.count):
            self.strip.setPixelColor(i, self._Color(0, 0, 0))
        self.strip.show()

    def render(self, level_normalized: float):
        lit = int(round(level_normalized * self.count))
        for i in range(self.count):
            if i < lit:
                r, g, b = self._color_for(i, self.count)
                self.strip.setPixelColor(i, self._Color(r, g, b))
            else:
                self.strip.setPixelColor(i, self._Color(0, 0, 0))
        self.strip.show()

    @staticmethod
    def _color_for(index: int, count: int):
        frac = index / max(1, count - 1)
        if frac < 0.5:
            g = 255
            r = int(255 * (frac / 0.5))
        else:
            r = 255
            g = int(255 * (1 - (frac - 0.5) / 0.5))
        return r, g, 0

    def close(self):
        for i in range(self.count):
            self.strip.setPixelColor(i, self._Color(0, 0, 0))
        self.strip.show()


def create_led(config: Config):
    try:
        return WS2812B(config)
    except Exception:
        return NullLED()


def led_loop(led, state: RSSIState, interval: float = 0.2):
    while True:
        snap = state.snapshot()
        led.render(snap["level_normalized"])
        time.sleep(interval)
