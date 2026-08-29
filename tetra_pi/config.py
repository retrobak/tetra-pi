from dataclasses import dataclass
from typing import Optional


@dataclass
class Config:
    freq_start_hz: float = 380.5e6
    freq_end_hz: float = 383.0e6
    sample_rate_hz: float = 2_400_000.0
    bins: int = 512
    integration_s: float = 4.0
    ppm: int = 0
    gain_tenths_db: int = 0
    rtl_power_fftw_bin: str = "rtl_power_fftw"

    led_count: int = 8
    led_gpio: int = 18
    led_brightness: int = 255
    led_dma: int = 10
    led_channel: int = 0
    led_invert: bool = False

    noise_floor_window: int = 60
    noise_floor_percentile: float = 25.0
    expected_dynamic_range_db: float = 30.0

    host: str = "0.0.0.0"
    port: int = 5000
    demo: bool = False

    @classmethod
    def from_env(cls, prefix: str = "TETRA_") -> "Config":
        import os
        mapping = {
            "FREQ_START_HZ": ("freq_start_hz", float),
            "FREQ_END_HZ": ("freq_end_hz", float),
            "SAMPLE_RATE_HZ": ("sample_rate_hz", float),
            "BINS": ("bins", int),
            "INTEGRATION_S": ("integration_s", float),
            "PPM": ("ppm", int),
            "GAIN_TENTHS_DB": ("gain_tenths_db", int),
            "RTL_POWER_FFTW_BIN": ("rtl_power_fftw_bin", str),
            "LED_COUNT": ("led_count", int),
            "LED_GPIO": ("led_gpio", int),
            "LED_BRIGHTNESS": ("led_brightness", int),
            "LED_DMA": ("led_dma", int),
            "LED_CHANNEL": ("led_channel", int),
            "NOISE_FLOOR_WINDOW": ("noise_floor_window", int),
            "NOISE_FLOOR_PERCENTILE": ("noise_floor_percentile", float),
            "EXPECTED_DYNAMIC_RANGE_DB": ("expected_dynamic_range_db", float),
            "HOST": ("host", str),
            "PORT": ("port", int),
            "DEMO": ("demo", lambda v: v.lower() in ("1", "true", "yes")),
        }
        kwargs = {}
        for env_key, (attr, cast) in mapping.items():
            val = os.environ.get(prefix + env_key)
            if val is not None:
                kwargs[attr] = cast(val)
        return cls(**kwargs)
