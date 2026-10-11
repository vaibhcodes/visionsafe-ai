"""Counting and occupancy calculations independent of detector implementation."""
from dataclasses import dataclass, field

from backend.pipeline.types import Track


@dataclass(frozen=True)
class CountingLine:
    start: tuple[float, float]
    end: tuple[float, float]


def _side(point: tuple[float, float], line: CountingLine) -> float:
    (x1, y1), (x2, y2) = line.start, line.end
    x, y = point
    return (x2 - x1) * (y - y1) - (y2 - y1) * (x - x1)


@dataclass
class LineCounter:
    line: CountingLine
    counts: dict[str, int] = field(default_factory=dict)
    _previous_sides: dict[int, float] = field(default_factory=dict)
    _counted_track_ids: set[int] = field(default_factory=set)

    def update(self, tracks: list[Track]) -> dict[str, int]:
        """Count a track once when its centroid crosses the configured line."""
        for track in tracks:
            current = _side(track.centroid, self.line)
            previous = self._previous_sides.get(track.track_id)
            if previous is not None and previous * current < 0 and track.track_id not in self._counted_track_ids:
                self.counts[track.class_name] = self.counts.get(track.class_name, 0) + 1
                self._counted_track_ids.add(track.track_id)
            self._previous_sides[track.track_id] = current
        return dict(self.counts)


def occupancy_ratio(tracks: list[Track], roi_area_pixels: float) -> float:
    if roi_area_pixels <= 0:
        raise ValueError("roi_area_pixels must be positive")
    occupied = sum(max(0, x2 - x1) * max(0, y2 - y1) for x1, y1, x2, y2 in (track.bbox for track in tracks))
    return min(occupied / roi_area_pixels, 1.0)
