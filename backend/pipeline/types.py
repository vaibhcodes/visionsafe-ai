from dataclasses import dataclass


@dataclass(frozen=True)
class Detection:
    class_name: str
    confidence: float
    bbox: tuple[float, float, float, float]


@dataclass(frozen=True)
class Track:
    track_id: int
    class_name: str
    confidence: float
    bbox: tuple[float, float, float, float]

    @property
    def centroid(self) -> tuple[float, float]:
        x1, y1, x2, y2 = self.bbox
        return ((x1 + x2) / 2, (y1 + y2) / 2)
