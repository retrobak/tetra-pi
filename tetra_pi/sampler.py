import random
import subprocess
import time
from typing import List

from tetra_pi.calibration import NoiseFloor, normalize
from tetra_pi.config import Config
from tetra_pi.parser import peak, scan_from_lines
from tetra_pi.state import RSSIState


class ScanReader:
    def __init__(self, freq_start, freq_end):
        self.freq_start = freq_start
        self.freq_end = freq_end
        self._buf: List[str] = []

    def feed(self, line: str) -> List:
        s = line.rstrip("\n").rstrip("\r")
        if s.strip() == "" or s.strip().startswith("#"):
            if self._buf:
                scan = scan_from_lines(self._buf, self.freq_start, self.freq_end)
                self._buf = []
                return scan
            return []
        self._buf.append(s)
        return []

    def flush(self) -> List:
        if self._buf:
            scan = scan_from_lines(self._buf, self.freq_start, self.freq_end)
            self._buf = []
            return scan
        return []


class Sampler:
    def __init__(self, config: Config, state: RSSIState):
        self.config = config
        self.state = state
        self.noise_floor = NoiseFloor(config.noise_floor_window, config.noise_floor_percentile)
        self.reader = ScanReader(config.freq_start_hz, config.freq_end_hz)

    def build_command(self) -> List[str]:
        cfg = self.config
        return [
            cfg.rtl_power_fftw_bin,
            "-f", f"{cfg.freq_start_hz}:{cfg.freq_end_hz}",
            "-r", str(int(cfg.sample_rate_hz)),
            "-b", str(cfg.bins),
            "-t", str(cfg.integration_s),
            "-p", str(cfg.ppm),
            "-g", str(cfg.gain_tenths_db),
            "-c", "-q",
        ]

    def _on_scan(self, scan):
        if not scan:
            return
        pwr, freq = peak(scan)
        if pwr is None:
            return
        floor = self.noise_floor.update(pwr)
        if floor is None:
            floor = pwr
        level = max(0.0, pwr - floor)
        norm = normalize(level, self.config.expected_dynamic_range_db)
        self.state.update(pwr, floor, level, norm, freq)

    def run(self):
        if self.config.demo:
            self._run_demo()
        else:
            self._run_subprocess()

    def _run_subprocess(self):
        cmd = self.build_command()
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, bufsize=1)
        try:
            for line in proc.stdout:
                scan = self.reader.feed(line)
                if scan:
                    self._on_scan(scan)
        finally:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except Exception:
                proc.kill()

    def _run_demo(self):
        while True:
            for line in self._demo_scan():
                scan = self.reader.feed(line)
                if scan:
                    self._on_scan(scan)
            time.sleep(0.2)

    def _demo_scan(self):
        n = 200
        base = -75.0 + random.uniform(-2, 2)
        spike = random.random() < 0.3
        spike_db = base + random.uniform(10, 28) if spike else base
        spike_at = random.randint(0, n - 1)
        yield "# Acquisition start: demo"
        yield "# frequency [Hz] power spectral density [dB/Hz]"
        for i in range(n):
            freq = self.config.freq_start_hz + (i / (n - 1)) * (self.config.freq_end_hz - self.config.freq_start_hz)
            pwr = base + random.uniform(-1.5, 1.5)
            if i == spike_at:
                pwr = spike_db
            yield f"{freq:.6e} {pwr:.4f}"
        yield ""
