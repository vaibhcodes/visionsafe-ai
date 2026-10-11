"""VisionSafe AI's intentionally small, test-data-backed API vertical slice."""
import logging
import math
from datetime import UTC, datetime, timedelta
from uuid import uuid4

from fastapi import BackgroundTasks, FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.ml.congestion import estimate_congestion
from backend.routing.scoring import RouteScoreInput, score_route
from backend.schemas.telemetry import (
    ApiEnvelope, ApiError, DataProvenance, ForecastPoint, ForecastResponse,
    LiveObservationMetrics, LiveTrafficObservation, Location, RouteCandidate,
    RouteRecommendation, RouteRecommendationRequest, SourceType,
    VideoAnalysisJob, VideoAnalysisRequest,
)

logger = logging.getLogger("visionsafe.api")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")

app = FastAPI(title="VisionSafe AI API", description="Test-data-backed traffic API vertical slice", version="1.0.0-draft", docs_url="/docs")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:3000"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

JOBS: dict[str, VideoAnalysisJob] = {}
OBSERVATIONS: dict[str, LiveTrafficObservation] = {}
TEST_CORRIDOR = "synthetic-test-corridor-1"


def now() -> datetime:
    return datetime.now(UTC)


def envelope(data: object, code: int = 200) -> JSONResponse:
    return JSONResponse(status_code=code, content=ApiEnvelope(success=True, data=data, timestamp=now()).model_dump(mode="json"))


@app.exception_handler(RequestValidationError)
async def validation_error(_: Request, exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(status_code=422, content=ApiEnvelope(success=False, error=ApiError(code="VALIDATION_ERROR", message="Request validation failed", details={"errors": exc.errors()}), timestamp=now()).model_dump(mode="json"))


@app.exception_handler(KeyError)
async def not_found(_: Request, exc: KeyError) -> JSONResponse:
    return JSONResponse(status_code=404, content=ApiEnvelope(success=False, error=ApiError(code="RESOURCE_NOT_FOUND", message=str(exc)), timestamp=now()).model_dump(mode="json"))


@app.exception_handler(ValueError)
async def invalid_value(_: Request, exc: ValueError) -> JSONResponse:
    return JSONResponse(status_code=400, content=ApiEnvelope(success=False, error=ApiError(code="INVALID_REQUEST", message=str(exc)), timestamp=now()).model_dump(mode="json"))


def synthetic_observation(corridor_id: str) -> LiveTrafficObservation:
    """Generate deterministic counts solely for automated/API fixture use."""
    counts = {"two_wheeler": 12, "auto_rickshaw": 3, "car": 8, "lcv": 1, "bus": 1, "truck": 0, "vru": 2}
    estimate = estimate_congestion(counts, window_seconds=60, capacity_pcu_per_hour=1800)
    return LiveTrafficObservation(
        corridor_id=corridor_id, name="Synthetic corridor [TEST DATA]",
        coordinates={"latitude": 12.926031, "longitude": 77.676246},
        provenance=DataProvenance(source_type=SourceType.HISTORICAL, model_version="pcu-baseline-test-fixture-v1", confidence_score=None, is_live=False, is_test_data=True, captured_at=now()),
        metrics=LiveObservationMetrics(vehicle_counts=counts, total_vehicle_count=sum(counts.values()), pcu_flow_rate_per_hour=estimate.pcu_flow_rate_per_hour, estimated_avg_speed_kmh=None, relative_speed_score=0.55, physical_speed_available=False, occupancy_ratio=0.31, level_of_service=estimate.level_of_service, congestion_index=estimate.congestion_index),
    )


def complete_fixture_job(job_id: str) -> None:
    job = JOBS[job_id]
    JOBS[job_id] = job.model_copy(update={"status": "completed", "progress_percent": 100, "processed_frames": 60, "total_frames": 60, "active_vehicle_tracks": 0})
    OBSERVATIONS[job.corridor_id] = synthetic_observation(job.corridor_id)
    logger.info("Completed synthetic test-fixture video job %s", job_id)


@app.get("/api/v1/health", response_model=ApiEnvelope)
def health_check() -> JSONResponse:
    return envelope({"status": "healthy", "service": "VisionSafe AI API", "mode": "development-test-fixture"})


@app.post("/api/v1/streams/jobs", status_code=status.HTTP_202_ACCEPTED, response_model=ApiEnvelope)
def submit_video_analysis(request: VideoAnalysisRequest, background_tasks: BackgroundTasks) -> JSONResponse:
    job_id = f"job_{uuid4().hex}"
    job = VideoAnalysisJob(job_id=job_id, status="queued", corridor_id=request.corridor_id, created_at=now())
    JOBS[job_id] = job
    # This slice intentionally never opens a path/RTSP stream or invokes a model.
    # Only the named test fixture is synthesized asynchronously.
    background_tasks.add_task(complete_fixture_job, job_id)
    logger.info("Queued video analysis job %s for %s", job_id, request.corridor_id)
    return envelope(job, code=status.HTTP_202_ACCEPTED)


@app.get("/api/v1/streams/jobs/{job_id}", response_model=ApiEnvelope)
def get_video_analysis_job(job_id: str) -> JSONResponse:
    if job_id not in JOBS:
        raise KeyError(f"Video analysis job '{job_id}' was not found")
    return envelope(JOBS[job_id])


@app.get("/api/v1/corridors/{corridor_id}/observation", response_model=ApiEnvelope)
def get_observation(corridor_id: str) -> JSONResponse:
    observation = OBSERVATIONS.get(corridor_id)
    if observation is None and corridor_id == TEST_CORRIDOR:
        observation = synthetic_observation(corridor_id)
    if observation is None:
        raise KeyError(f"Observation for corridor '{corridor_id}' was not found")
    return envelope(observation)


@app.get("/api/v1/corridors/{corridor_id}/forecast", response_model=ApiEnvelope)
def get_forecast(corridor_id: str, horizon_minutes: int = 60) -> JSONResponse:
    if not 1 <= horizon_minutes <= 120:
        raise ValueError("horizon_minutes must be between 1 and 120")
    observation = OBSERVATIONS.get(corridor_id) or (synthetic_observation(corridor_id) if corridor_id == TEST_CORRIDOR else None)
    if observation is None:
        raise KeyError(f"Observation for corridor '{corridor_id}' was not found")
    points = []
    for minutes in range(15, horizon_minutes + 1, 15):
        points.append(ForecastPoint(timestamp=now() + timedelta(minutes=minutes), predicted_pcu_flow=observation.metrics.pcu_flow_rate_per_hour, predicted_speed_kmh=None, congestion_index=observation.metrics.congestion_index, level_of_service=observation.metrics.level_of_service, confidence_interval=(max(0, observation.metrics.congestion_index - 0.15), min(1, observation.metrics.congestion_index + 0.15))))
    return envelope(ForecastResponse(corridor_id=corridor_id, provenance=DataProvenance(source_type=SourceType.FORECAST, model_version="persistence-baseline-test-fixture-v1", is_live=False, is_test_data=True, captured_at=now()), forecast_points=points))


def haversine_km(a: Location, b: Location) -> float:
    radius_km = 6371.0088
    d_lat, d_lon = math.radians(b.latitude - a.latitude), math.radians(b.longitude - a.longitude)
    lat1, lat2 = math.radians(a.latitude), math.radians(b.latitude)
    h = math.sin(d_lat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(d_lon / 2) ** 2
    return 2 * radius_km * math.asin(math.sqrt(h))


@app.post("/api/v1/routes/recommend", response_model=ApiEnvelope)
def recommend_route(request: RouteRecommendationRequest) -> JSONResponse:
    """Score geometric candidates; a routing provider is deliberately not implied."""
    direct_km = max(haversine_km(request.origin, request.destination), 0.01)
    variants = [("route_geometric_direct", "Geometric direct baseline [TEST DATA]", 1.0, 0.55), ("route_geometric_lower_congestion", "Geometric lower-congestion baseline [TEST DATA]", 1.12, 0.25)]
    candidates = []
    for route_id, name, distance_factor, congestion in variants:
        distance = direct_km * distance_factor
        free_flow = distance / 35 * 60
        delay = free_flow * congestion * 0.35
        uncertainty = free_flow * 0.2
        candidates.append(RouteCandidate(route_id=route_id, route_name=name, distance_km=round(distance, 3), estimated_duration_minutes=round(free_flow + delay, 2), free_flow_duration_minutes=round(free_flow, 2), avg_congestion_index=congestion, level_of_service=estimate_congestion({"car": int(congestion * 100)}, 60, 1800).level_of_service, bottlenecks=[], polyline_geojson={"type": "LineString", "coordinates": [[request.origin.longitude, request.origin.latitude], [request.destination.longitude, request.destination.latitude]]}, score=score_route(RouteScoreInput(free_flow, congestion, delay, uncertainty)), data_freshness="synthetic test fixture; no routing provider or live traffic feed configured"))
    selected = min(candidates, key=lambda item: item.score)
    result = RouteRecommendation(origin=request.origin, destination=request.destination, recommended_route_id=selected.route_id, recommendation_reason="Selected by deterministic free-flow, congestion, delay, and uncertainty scoring using synthetic test data. This is not a live travel-time claim.", candidates=candidates)
    return envelope(result)
