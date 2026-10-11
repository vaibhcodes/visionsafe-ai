from fastapi.testclient import TestClient

from backend.main import TEST_CORRIDOR, app
from backend.ml.congestion import estimate_congestion
from backend.routing.scoring import RouteScoreInput, score_route

client = TestClient(app)


def test_congestion_baseline_uses_pcu_weights():
    estimate = estimate_congestion({"two_wheeler": 2, "car": 1, "bus": 1}, 60, 600)
    assert estimate.pcu_total == 5.0
    assert estimate.pcu_flow_rate_per_hour == 300.0
    assert estimate.congestion_index == 0.5
    assert estimate.level_of_service == "D"


def test_route_score_penalizes_congestion_delay_and_uncertainty():
    clear = score_route(RouteScoreInput(free_flow_minutes=10, congestion_index=0.1))
    delayed = score_route(RouteScoreInput(free_flow_minutes=10, congestion_index=0.8, delay_minutes=3, uncertainty_minutes=2))
    assert delayed > clear


def test_test_fixture_observation_is_explicitly_non_live():
    response = client.get(f"/api/v1/corridors/{TEST_CORRIDOR}/observation")
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["provenance"]["is_test_data"] is True
    assert data["provenance"]["is_live"] is False
    assert data["metrics"]["physical_speed_available"] is False
    assert data["metrics"]["estimated_avg_speed_kmh"] is None


def test_video_analysis_job_interface_completes_test_fixture():
    response = client.post("/api/v1/streams/jobs", json={"stream_source": "sample_corridor_1", "corridor_id": TEST_CORRIDOR, "fps_target": 15, "enable_tracking": True, "enable_counting": True})
    assert response.status_code == 202
    job_id = response.json()["data"]["job_id"]
    status_response = client.get(f"/api/v1/streams/jobs/{job_id}")
    assert status_response.status_code == 200
    assert status_response.json()["data"]["status"] == "completed"


def test_route_recommendation_is_marked_as_synthetic():
    response = client.post("/api/v1/routes/recommend", json={"origin": {"latitude": 12.9279, "longitude": 77.6271}, "destination": {"latitude": 12.9698, "longitude": 77.75}, "vehicle_type": "car", "optimization_priority": "balanced"})
    assert response.status_code == 200
    result = response.json()["data"]
    assert len(result["candidates"]) == 2
    assert "not a live travel-time claim" in result["recommendation_reason"]
