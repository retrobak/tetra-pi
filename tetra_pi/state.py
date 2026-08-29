import threading
import time
from collections import deque
from dataclasses import dataclass, field
from typing import Deque, Optional


@dataclass
class RSSIState:
    current_db: Optional[float] = None
    noise_floor_db: Optional[float] = None
    level_db: float = 0.0
    level_normalized: float = 0.0
    peak_freq_hz: Optional[float] = None
    scan_count: int = 0
    last_scan_time: float = 0.0
    history: Deque = field(default_factory=lambda: deque(maxlen=240))
    _lock: threading.Lock = field(default_factory=threading.Lock)

    def update(self, current_db, noise_floor_db, level_db, level_normalized, peak_freq_hz):
        with self._lock:
            now = time.time()
            self.current_db = current_db
            self.noise_floor_db = noise_floor_db
            self.level_db = level_db
            self.level_normalized = level_normalized
            self.peak_freq_hz = peak_freq_hz
            self.scan_count += 1
            self.last_scan_time = now
            self.history.append((now, current_db, noise_floor_db, level_normalized))

    def snapshot(self):
        with self._lock:
            return {
                "current_db": self.current_db,
                "noise_floor_db": self.noise_floor_db,
                "level_db": self.level_db,
                "level_normalized": self.level_normalized,
                "peak_freq_hz": self.peak_freq_hz,
                "scan_count": self.scan_count,
                "last_scan_time": self.last_scan_time,
            }
