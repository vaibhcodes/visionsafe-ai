"""Pydantic contracts for the public VisionSafe API.

The synthetic corridor identifiers in this module are test fixtures only.  They
exist to exercise the vertical slice and must never be presented as live data.
"""
from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class SourceType(str, Enum):
    LIVE_OBSERVATION = "live_observation"
    HISTORICAL = "historical"
    FORECAST = "forecast"
    THIRD_PARTY = "third_party"


class DataProvenance(BaseModel):
    source_type: SourceType
    model_version: str | None = None
    confidence_score: float | None = Field(default=None, ge=0.0, le=1.0)
    is_live: bool
    captured_at: datetime
    is_test_data: bool = False


class Coordinates(BaseModel):
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)


class LiveObservationMetrics(BaseModel):
    vehicle_counts: dict[str, int]
    total_vehicle_count: int = Field(ge=0)
    pcu_flow_rate_per_hour: float = Field(ge=0)
    estimated_avg_speed_kmh: float | None = Field(default=None, ge=0)
    relative_speed_score: float | None = Field(default=None, ge=0, le=1)
    physical_speed_available: bool = False
    occupancy_ratio: float = Field(ge=0.0, le=1.0)
    level_of_service: str = Field(pattern="^[A-F]$")
    congestion_index: float = Field(ge=0.0, le=1.0)

    @field_validator("vehicle_counts")
    @classmethod
    def counts_must_be_non_negative(cls, value: dict[str, int]) -> dict[str, int]:
        if any(count < 0 for count in value.values()):
            raise ValueError("vehicle counts cannot be negative")
        return value


class LiveTrafficObservation(BaseModel):
    corridor_id: str = Field(min_length=1, max_length=128)
    name: str
    coordinates: Coordinates
    provenance: DataProvenance
    metrics: LiveObservationMetrics


class StreamSource(str, Enum):
    FILE_UPLOAD = "file_upload"
    RTSP_URL = "rtsp_url"
    SAMPLE_CORRIDOR_1 = "sample_corridor_1"


class VideoAnalysisRequest(BaseModel):
    stream_source: StreamSource
    source_path: str | None = None
    corridor_id: str = Field(min_length=1, max_length=128)
    fps_target: int = Field(default=15, ge=1, le=60)
    enable_tracking: bool = True
    enable_counting: bool = True

    @field_validator("source_path")
    @classmethod
    def path_is_not_blank(cls, value: str | None) -> str | None:
        return value.strip() if value and value.strip() else None


class VideoAnalysisJob(BaseModel):
    job_id: str
    status: str
    corridor_id: str
    created_at: datetime
    progress_percent: float = Field(default=0, ge=0, le=100)
    processed_frames: int = Field(default=0, ge=0)
    total_frames: int | None = Field(default=None, ge=0)
    active_vehicle_tracks: int = Field(default=0, ge=0)
    error_message: str | None = None


class ForecastPoint(BaseModel):
    timestamp: datetime
    predicted_pcu_flow: float = Field(ge=0)
    predicted_speed_kmh: float | None = Field(default=None, ge=0)
    congestion_index: float = Field(ge=0, le=1)
    level_of_service: str = Field(pattern="^[A-F]$")
    confidence_interval: tuple[float, float]


class ForecastResponse(BaseModel):
    corridor_id: str
    provenance: DataProvenance
    forecast_points: list[ForecastPoint]


class Location(BaseModel):
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    name: str | None = None


class RouteRecommendationRequest(BaseModel):
    origin: Location
    destination: Location
    vehicle_type: str = Field(default="car", min_length=1)
    optimization_priority: str = Field(default="balanced", pattern="^(fastest|balanced|lowest_congestion)$")


class Bottleneck(BaseModel):
    segment_name: str
    congestion_index: float = Field(ge=0, le=1)
    has_live_cv_feed: bool


class RouteCandidate(BaseModel):
    route_id: str
    route_name: str
    distance_km: float = Field(ge=0)
    estimated_duration_minutes: float = Field(ge=0)
    free_flow_duration_minutes: float = Field(ge=0)
    avg_congestion_index: float = Field(ge=0, le=1)
    level_of_service: str = Field(pattern="^[A-F]$")
    bottlenecks: list[Bottleneck]
    polyline_geojson: dict[str, Any]
    score: float = Field(ge=0)
    data_freshness: str


class RouteRecommendation(BaseModel):
    origin: Location
    destination: Location
    recommended_route_id: str
    recommendation_reason: str
    candidates: list[RouteCandidate]


class ApiError(BaseModel):
    code: str
    message: str
    details: dict[str, Any] = Field(default_factory=dict)


class ApiEnvelope(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    success: bool
    data: Any | None = None
    error: ApiError | None = None
    timestamp: datetime
