import math
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tetra_pi import calibration, config, leds, parser, state
from tetra_pi.sampler import Sampler


class TestParser(unittest.TestCase):
    def test_skip_comments_and_blanks(self):
        self.assertIsNone(parser.parse_line("# header"))
        self.assertIsNone(parser.parse_line("   "))
        self.assertIsNone(parser.parse_line(""))

    def test_parse_point(self):
        self.assertEqual(parser.parse_line("1.41940575e+09 -68.7714"), (1.41940575e9, -68.7714))

    def test_freq_filter(self):
        self.assertIsNone(parser.parse_line("1.0e9 -50", freq_start=1.4e9, freq_end=1.5e9))
        self.assertIsNotNone(parser.parse_line("1.42e9 -50", freq_start=1.4e9, freq_end=1.5e9))

    def test_scan_from_lines(self):
        lines = ["# hdr", "1.0e9 -60", "1.1e9 -55", "", "garbage"]
        self.assertEqual(len(parser.scan_from_lines(lines)), 2)

    def test_peak(self):
        pts = [(1.0e9, -60), (1.1e9, -40), (1.2e9, -55)]
        pwr, freq = parser.peak(pts)
        self.assertEqual(pwr, -40)
        self.assertEqual(freq, 1.1e9)


class TestCalibration(unittest.TestCase):
    def test_percentile(self):
        vals = [10, 20, 30, 40, 50]
        self.assertAlmostEqual(calibration.percentile(vals, 25), 20.0)
        self.assertAlmostEqual(calibration.percentile(vals, 50), 30.0)

    def test_noise_floor(self):
        nf = calibration.NoiseFloor(window=10, pct=25.0)
        for v in [-70, -71, -69, -70, -72, -68, -71, -70, -69, -70]:
            floor = nf.update(v)
        self.assertLess(floor, -60)

    def test_normalize(self):
        self.assertEqual(calibration.normalize(0, 30), 0.0)
        self.assertEqual(calibration.normalize(30, 30), 1.0)
        self.assertEqual(calibration.normalize(60, 30), 1.0)
        self.assertEqual(calibration.normalize(-5, 30), 0.0)


class TestConfig(unittest.TestCase):
    def test_defaults(self):
        c = config.Config()
        self.assertEqual(c.freq_start_hz, 380.5e6)
        self.assertEqual(c.freq_end_hz, 383.0e6)

    def test_from_env(self):
        os.environ["TETRA_PPM"] = "40"
        os.environ["TETRA_INTEGRATION_S"] = "4"
        c = config.Config.from_env()
        self.assertEqual(c.ppm, 40)
        self.assertEqual(c.integration_s, 4.0)
        del os.environ["TETRA_PPM"]
        del os.environ["TETRA_INTEGRATION_S"]

    def test_build_command(self):
        c = config.Config(ppm=40, gain_tenths_db=350)
        cmd = Sampler(c, state.RSSIState()).build_command()
        self.assertIn("-p", cmd)
        self.assertIn("40", cmd)
        self.assertIn("-g", cmd)
        self.assertIn("350", cmd)
        self.assertTrue(any("380.5" in x or "383" in x for x in cmd))
        self.assertIn("-c", cmd)


class TestLeds(unittest.TestCase):
    def test_color_for(self):
        r, g, b = leds.WS2812B._color_for(0, 8)
        self.assertEqual(g, 255)
        r2, g2, b2 = leds.WS2812B._color_for(7, 8)
        self.assertEqual(r2, 255)

    def test_null_led_is_safe(self):
        led = leds.NullLED()
        led.boot_sequence()
        led.render(0.9)
        led.close()


if __name__ == "__main__":
    unittest.main()
