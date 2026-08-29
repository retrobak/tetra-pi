import math
from collections import deque
from typing import List, Optional

try:
    import numpy as np
    _HAVE_NUMPY = True
except Exception:
    _HAVE_NUMPY = False


def percentile(sorted_values: List[float], pct: float) -> Optional[float]:
    n = len(sorted_values)
    if n == 0:
        return None
    if n == 1:
        return sorted_values[0]
    k = (n - 1) * (pct / 100.0)
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return sorted_values[int(k)]
    return sorted_values[f] * (c - k) + sorted_values[c] * (k - f)


class NoiseFloor:
    def __init__(self, window: int = 60, pct: float = 25.0):
        self.window = window
        self.pct = pct
        self.samples = deque(maxlen=window)

    def update(self, value: float) -> Optional[float]:
        self.samples.append(value)
        return self.floor()

    def floor(self) -> Optional[float]:
        if not self.samples:
            return None
        ordered = sorted(self.samples)
        if _HAVE_NUMPY:
            return float(np.percentile(ordered, self.pct))
        return percentile(ordered, self.pct)


def normalize(level_db: float, expected_range_db: float) -> float:
    if expected_range_db <= 0:
        return 0.0
    return max(0.0, min(1.0, level_db / expected_range_db))
