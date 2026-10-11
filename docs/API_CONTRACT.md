# API Contract Specification: VisionSafe AI

**Version**: 1.0.0-draft  
**Base URL**: `http://localhost:8000/api/v1`  
**OpenAPI Specification**: Available automatically at `http://localhost:8000/docs`

This document defines the formal request/response contract between the **Backend (Codex)** and the **Frontend / Clients (Gemini)**.

---

## 1. General Principles & Standard Types

### 1.1 Standard Response Envelope
All non-streaming endpoints return an envelope containing metadata and timing:

```json
{
  "success": true,
  "data": { ... },
  "error": null,
  "timestamp": "2026-10-09T18:30:00.000Z"
}
```

In the event of an error:
```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "The requested camera stream does not exist.",
    "details": {}
  },
  "timestamp": "2026-10-09T18:30:00.000Z"
}
```

### 1.2 Data State Tagging
Every traffic measurement object must include a `provenance` block:
```typescript
interface DataProvenance {
  source_type: "live_observation" | "historical" | "forecast" | "third_party";
  model_version?: string;
  confidence_score?: number; // 0.0 to 1.0
  is_live: boolean;
  captured_at: string; // ISO 8601
}
```

---

## 2. Endpoints Specification

### 2.1 Video & Stream Management

#### `POST /streams/jobs`
Submit a video file or RTSP stream URI for perception processing.

**Request Payload:**
```json
{
  "stream_source": "file_upload" | "rtsp_url" | "sample_corridor_1",
  "source_path": "data/raw/sample_videos/blr_outer_ring_road_01.mp4",
  "corridor_id": "blr-orr-bellandur",
  "fps_target": 15,
  "enable_tracking": true,
  "enable_counting": true
}
```

**Response (202 Accepted):**
```json
{
  "success": true,
  "data": {
    "job_id": "job_01hxyz89abc",
    "status": "queued",
    "corridor_id": "blr-orr-bellandur",
    "created_at": "2026-10-09T18:35:00.000Z"
  },
  "error": null,
  "timestamp": "2026-10-09T18:35:00.000Z"
}
```

#### `GET /streams/jobs/{job_id}`
Query status and progress of a perception job.

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "job_id": "job_01hxyz89abc",
    "status": "processing" | "completed" | "failed",
    "progress_percent": 68.5,
    "processed_frames": 1028,
    "total_frames": 1500,
    "active_vehicle_tracks": 42
  },
  "error": null,
  "timestamp": "2026-10-09T18:35:10.000Z"
}
```

---

### 2.2 Live Traffic Telemetry & Observations

#### `GET /corridors/{corridor_id}/observation`
Retrieve the latest validated traffic observation for a specific monitored link or junction.

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "corridor_id": "blr-orr-bellandur",
    "name": "Outer Ring Road - Bellandur Junction",
    "coordinates": {
      "latitude": 12.926031,
      "longitude": 77.676246
    },
    "provenance": {
      "source_type": "live_observation",
      "model_version": "yolov11n-indotraffic-v1",
      "confidence_score": 0.94,
      "is_live": true,
      "captured_at": "2026-10-09T18:35:30.000Z"
    },
    "metrics": {
      "vehicle_counts": {
        "two_wheeler": 118,
        "auto_rickshaw": 34,
        "car": 72,
        "lcv": 8,
        "bus": 6,
        "truck": 2,
        "vru": 14
      },
      "total_vehicle_count": 254,
      "pcu_flow_rate_per_hour": 1845.0,
      "estimated_avg_speed_kmh": 14.8,
      "occupancy_ratio": 0.72,
      "level_of_service": "E",
      "congestion_index": 0.76
    }
  },
  "error": null,
  "timestamp": "2026-10-09T18:35:32.000Z"
}
```

#### `GET /corridors/{corridor_id}/forecast`
Retrieve the predicted congestion curve for the next 60 minutes in 15-minute intervals.

**Query Parameters:**
- `horizon_minutes`: integer (default: 60, max: 120)

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "corridor_id": "blr-orr-bellandur",
    "provenance": {
      "source_type": "forecast",
      "model_version": "xgboost-congestion-v1",
      "confidence_score": 0.88,
      "is_live": false,
      "captured_at": "2026-10-09T18:35:00.000Z"
    },
    "forecast_points": [
      {
        "timestamp": "2026-10-09T18:45:00.000Z",
        "predicted_pcu_flow": 2100.0,
        "predicted_speed_kmh": 11.2,
        "congestion_index": 0.84,
        "level_of_service": "F",
        "confidence_interval": [0.78, 0.90]
      },
      {
        "timestamp": "2026-10-09T19:00:00.000Z",
        "predicted_pcu_flow": 1950.0,
        "predicted_speed_kmh": 13.5,
        "congestion_index": 0.78,
        "level_of_service": "E",
        "confidence_interval": [0.71, 0.85]
      }
    ]
  },
  "error": null,
  "timestamp": "2026-10-09T18:35:32.000Z"
}
```

---

### 2.3 Route Comparison & Recommendation

#### `POST /routes/recommend`
Calculate and compare alternative routes between two coordinates, factoring in current vision observations and predictions.

**Request Payload:**
```json
{
  "origin": {
    "latitude": 12.9279,
    "longitude": 77.6271,
    "name": "Koramangala 5th Block"
  },
  "destination": {
    "latitude": 12.9698,
    "longitude": 77.7500,
    "name": "ITPB Whitefield"
  },
  "vehicle_type": "car",
  "optimization_priority": "balanced"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "origin": { "latitude": 12.9279, "longitude": 77.6271, "name": "Koramangala 5th Block" },
    "destination": { "latitude": 12.9698, "longitude": 77.7500, "name": "ITPB Whitefield" },
    "recommended_route_id": "route_candidate_2",
    "recommendation_reason": "Bypasses severe congestion (LOS F) on Bellandur junction via Old Airport Road, saving an estimated 16 minutes despite 1.4 km longer distance.",
    "candidates": [
      {
        "route_id": "route_candidate_1",
        "route_name": "Via Outer Ring Road (Direct)",
        "distance_km": 16.2,
        "estimated_duration_minutes": 58.0,
        "free_flow_duration_minutes": 26.0,
        "avg_congestion_index": 0.79,
        "level_of_service": "F",
        "bottlenecks": [
          {
            "segment_name": "Bellandur Junction Flyover Approach",
            "congestion_index": 0.88,
            "has_live_cv_feed": true
          }
        ],
        "polyline_geojson": {
          "type": "LineString",
          "coordinates": [[77.6271, 12.9279], [77.6762, 12.9260], [77.7500, 12.9698]]
        }
      },
      {
        "route_id": "route_candidate_2",
        "route_name": "Via HAL Old Airport Road & Varthur Main",
        "distance_km": 17.6,
        "estimated_duration_minutes": 42.0,
        "free_flow_duration_minutes": 28.0,
        "avg_congestion_index": 0.45,
        "level_of_service": "C",
        "bottlenecks": [],
        "polyline_geojson": {
          "type": "LineString",
          "coordinates": [[77.6271, 12.9279], [77.6510, 12.9580], [77.7500, 12.9698]]
        }
      }
    ]
  },
  "error": null,
  "timestamp": "2026-10-09T18:35:40.000Z"
}
```

---

### 2.4 Real-time WebSocket Protocol

#### `WS /ws/telemetry/{corridor_id}`
Connect to receive 2 Hz or 5 Hz bounding box tracks, counting pulses, and instantaneous PCU flow rate.

**Client Connection:**
`ws://localhost:8000/api/v1/ws/telemetry/blr-orr-bellandur`

**Server Message (Frame Telemetry):**
```json
{
  "type": "FRAME_TELEMETRY",
  "frame_idx": 450,
  "timestamp": "2026-10-09T18:35:41.200Z",
  "active_tracks": [
    {
      "track_id": 104,
      "class": "auto_rickshaw",
      "confidence": 0.92,
      "bbox": [320, 450, 410, 580],
      "speed_kmh": 22.4
    }
  ],
  "pcu_instantaneous_rate": 1820.0,
  "occupancy_ratio": 0.68
}
```
