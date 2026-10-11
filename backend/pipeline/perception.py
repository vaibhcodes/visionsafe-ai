"""Ultralytics YOLO11 inference and ByteTrack tracking module."""
import os
from pathlib import Path
from typing import Any

from backend.pipeline.types import Detection, Track

class UltralyticsByteTrackPipeline:
    def __init__(self, checkpoint_path: str | Path, tracker_config: str = "bytetrack.yaml", device: str | None = None) -> None:
        self.checkpoint_path = Path(checkpoint_path)
        if not self.checkpoint_path.is_file():
            raise FileNotFoundError(f"Configured YOLO checkpoint does not exist: {self.checkpoint_path}")
        
        # Load once
        from ultralytics import YOLO
        self.model = YOLO(str(self.checkpoint_path))
        self.tracker_config = tracker_config
        self.device = device

        # Introspect model classes to map them correctly, abandoning old hardcoded 7 classes
        self.names = self.model.names

    def detect_frame(self, frame: Any, conf: float = 0.25, iou: float = 0.45) -> list[Detection]:
        """Runs stateless detection on a single frame."""
        results = self.model(frame, conf=conf, iou=iou, device=self.device, verbose=False)
        result = results[0]
        
        detections = []
        if result.boxes is not None:
            for box in result.boxes:
                cls_id = int(box.cls.item())
                class_name = self.names[cls_id]
                detections.append(Detection(
                    class_name=class_name,
                    confidence=float(box.conf.item()),
                    bbox=tuple(float(v) for v in box.xyxy[0].tolist())
                ))
        return detections

    def track_frame(self, frame: Any, conf: float = 0.25, iou: float = 0.45) -> list[Track]:
        """Runs stateful tracking across frames."""
        results = self.model.track(frame, persist=True, tracker=self.tracker_config, conf=conf, iou=iou, device=self.device, verbose=False)
        result = results[0]
        
        tracks = []
        if result.boxes is not None and result.boxes.id is not None:
            for box, track_id in zip(result.boxes, result.boxes.id.tolist()):
                cls_id = int(box.cls.item())
                class_name = self.names[cls_id]
                tracks.append(Track(
                    track_id=int(track_id),
                    class_name=class_name,
                    confidence=float(box.conf.item()),
                    bbox=tuple(float(v) for v in box.xyxy[0].tolist())
                ))
        return tracks
