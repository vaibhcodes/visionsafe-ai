export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export type DataProvenance = {
  source_type: "live_observation" | "historical" | "forecast" | "third_party";
  model_version?: string;
  confidence_score?: number;
  is_live: boolean;
  captured_at: string;
  is_test_data?: boolean;
};

export type ObservationMetrics = {
  vehicle_counts: Record<string, number>;
  total_vehicle_count: number;
  pcu_flow_rate_per_hour: number;
  estimated_avg_speed_kmh: number | null;
  relative_speed_score?: number | null;
  physical_speed_available?: boolean;
  occupancy_ratio: number;
  level_of_service: string;
  congestion_index: number;
};

export type TrafficObservation = {
  corridor_id: string;
  name: string;
  coordinates: { latitude: number; longitude: number };
  provenance: DataProvenance;
  metrics: ObservationMetrics;
};

export type ForecastPoint = {
  timestamp: string;
  predicted_pcu_flow: number;
  predicted_speed_kmh: number | null;
  congestion_index: number;
  level_of_service: string;
  confidence_interval: [number, number];
};

export type ForecastResponse = { corridor_id: string; provenance: DataProvenance; forecast_points: ForecastPoint[] };
export type Location = { latitude: number; longitude: number; name?: string };
export type RouteCandidate = {
  route_id: string; route_name: string; distance_km: number; estimated_duration_minutes: number;
  free_flow_duration_minutes: number; avg_congestion_index: number; level_of_service: string;
  bottlenecks: { segment_name: string; congestion_index: number; has_live_cv_feed: boolean }[];
  polyline_geojson: { type: "LineString"; coordinates: [number, number][] }; score: number; data_freshness: string;
};
export type RouteRecommendation = { origin: Location; destination: Location; recommended_route_id: string; recommendation_reason: string; candidates: RouteCandidate[] };
export type VideoAnalysisJob = { job_id: string; status: string; corridor_id: string; created_at: string; progress_percent: number; processed_frames: number; total_frames: number | null; active_vehicle_tracks: number; error_message: string | null };
export type ApiError = { code: string; message: string; details?: Record<string, unknown> };
export type ApiEnvelope<T> = { success: boolean; data: T | null; error: ApiError | null; timestamp: string };

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, { ...init, headers: { "Content-Type": "application/json", ...init?.headers } });
  const body = (await response.json()) as ApiEnvelope<T>;
  if (!response.ok || !body.success || body.data === null) throw new Error(body.error?.message || `API request failed (${response.status})`);
  return body.data;
}

export const fetchHealth = () => request<{ status: string; service: string; mode: string }>("/health");
export const fetchObservation = (corridorId: string) => request<TrafficObservation>(`/corridors/${encodeURIComponent(corridorId)}/observation`);
export const fetchForecast = (corridorId: string) => request<ForecastResponse>(`/corridors/${encodeURIComponent(corridorId)}/forecast`);
export const fetchRouteRecommendation = (origin: Location, destination: Location) => request<RouteRecommendation>("/routes/recommend", { method: "POST", body: JSON.stringify({ origin, destination, vehicle_type: "car", optimization_priority: "balanced" }) });
export const submitVideoJob = (corridorId: string, sourcePath?: string) => request<VideoAnalysisJob>("/streams/jobs", { method: "POST", body: JSON.stringify({ stream_source: sourcePath ? "file_upload" : "sample_corridor_1", source_path: sourcePath, corridor_id: corridorId, fps_target: 15, enable_tracking: true, enable_counting: true }) });
