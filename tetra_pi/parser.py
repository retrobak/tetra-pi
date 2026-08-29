from typing import Iterable, List, Optional, Tuple


def parse_line(line: str, freq_start: Optional[float] = None, freq_end: Optional[float] = None) -> Optional[Tuple[float, float]]:
    s = line.strip()
    if not s or s.startswith("#"):
        return None
    parts = s.split()
    if len(parts) < 2:
        return None
    try:
        freq = float(parts[0])
        power = float(parts[1])
    except ValueError:
        return None
    if freq_start is not None and freq < freq_start:
        return None
    if freq_end is not None and freq > freq_end:
        return None
    return (freq, power)


def scan_from_lines(lines: Iterable[str], freq_start: Optional[float] = None, freq_end: Optional[float] = None) -> List[Tuple[float, float]]:
    points = []
    for line in lines:
        p = parse_line(line, freq_start, freq_end)
        if p:
            points.append(p)
    return points


def peak(points: List[Tuple[float, float]]) -> Tuple[Optional[float], Optional[float]]:
    if not points:
        return None, None
    best = max(points, key=lambda pt: pt[1])
    return best[1], best[0]
