"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";
import { fetchForecast, fetchHealth, fetchObservation, fetchRouteRecommendation, RouteCandidate, RouteRecommendation, submitVideoJob, TrafficObservation, VideoAnalysisJob } from "../services/apiClient";

const CORRIDOR = "synthetic-test-corridor-1";
const defaultOrigin = { latitude: 12.9279, longitude: 77.6271, name: "Origin" };
const defaultDestination = { latitude: 12.9698, longitude: 77.75, name: "Destination" };
const journeyFields: [string, number][] = [["originLat", defaultOrigin.latitude], ["originLng", defaultOrigin.longitude], ["destinationLat", defaultDestination.latitude], ["destinationLng", defaultDestination.longitude]];

function Panel({ title, children }: { title: string; children: React.ReactNode }) { return <section className="rounded-xl border border-slate-800 bg-slate-900/70 p-5 shadow-sm"><h2 className="text-base font-semibold text-slate-100">{title}</h2>{children}</section>; }
function Metric({ label, value }: { label: string; value: string }) { return <div className="rounded-lg bg-slate-800 p-3"><dt className="text-xs uppercase tracking-wide text-slate-400">{label}</dt><dd className="mt-1 text-lg font-semibold">{value}</dd></div>; }

function RouteMap({ routes, selected, onSelect }: { routes: RouteCandidate[]; selected?: string; onSelect: (id: string) => void }) {
  const points = routes.flatMap((route) => route.polyline_geojson.coordinates);
  if (!points.length) return <p className="mt-3 rounded bg-slate-800 p-4 text-sm text-slate-400">No route geometry is available from the routing API.</p>;
  const xs = points.map(([x]) => x), ys = points.map(([, y]) => y);
  const toPoint = ([x, y]: [number, number]) => `${20 + ((x - Math.min(...xs)) / (Math.max(...xs) - Math.min(...xs) || 1)) * 260},${180 - ((y - Math.min(...ys)) / (Math.max(...ys) - Math.min(...ys) || 1)) * 140}`;
  return <svg viewBox="0 0 300 200" className="mt-3 w-full rounded-lg bg-slate-950" role="img" aria-label="Route geometry from the routing API">{routes.map((route, index) => <polyline key={route.route_id} points={route.polyline_geojson.coordinates.map(toPoint).join(" ")} onClick={() => onSelect(route.route_id)} className="cursor-pointer" fill="none" stroke={route.route_id === selected ? "#22d3ee" : index ? "#fbbf24" : "#f87171"} strokeWidth={route.route_id === selected ? 6 : 4} />)}</svg>;
}

export default function Home() {
  const [observation, setObservation] = useState<TrafficObservation | null>(null);
  const [forecast, setForecast] = useState<number[]>([]);
  const [service, setService] = useState("Connecting");
  const [error, setError] = useState<string | null>(null);
  const [routes, setRoutes] = useState<RouteRecommendation | null>(null);
  const [routeError, setRouteError] = useState<string | null>(null);
  const [selectedRoute, setSelectedRoute] = useState<string>();
  const [job, setJob] = useState<VideoAnalysisJob | null>(null);
  const [jobError, setJobError] = useState<string | null>(null);

  useEffect(() => { Promise.all([fetchHealth(), fetchObservation(CORRIDOR), fetchForecast(CORRIDOR)]).then(([health, value, curve]) => { setService(health.status); setObservation(value); setForecast(curve.forecast_points.map((point) => point.congestion_index)); }).catch((reason: unknown) => { setService("unavailable"); setError(reason instanceof Error ? reason.message : "Backend unavailable"); }); }, []);
  const selected = useMemo(() => routes?.candidates.find((candidate) => candidate.route_id === selectedRoute) || routes?.candidates.find((candidate) => candidate.route_id === routes.recommended_route_id), [routes, selectedRoute]);

  async function searchJourney(event: FormEvent<HTMLFormElement>) { event.preventDefault(); setRouteError(null); const form = new FormData(event.currentTarget); const origin = { latitude: Number(form.get("originLat")), longitude: Number(form.get("originLng")), name: "Origin" }; const destination = { latitude: Number(form.get("destinationLat")), longitude: Number(form.get("destinationLng")), name: "Destination" }; try { const response = await fetchRouteRecommendation(origin, destination); setRoutes(response); setSelectedRoute(response.recommended_route_id); } catch (reason) { setRouteError(reason instanceof Error ? reason.message : "Route search unavailable"); } }
  async function startAnalysis(event: FormEvent<HTMLFormElement>) { event.preventDefault(); setJobError(null); const file = new FormData(event.currentTarget).get("video") as File | null; if (file?.name) { setJobError("The current API contract accepts a server-side source_path, not video bytes. Local file upload is unavailable until the backend upload endpoint exists."); return; } try { setJob(await submitVideoJob(CORRIDOR)); } catch (reason) { setJobError(reason instanceof Error ? reason.message : "Video analysis unavailable"); } }

  return <main className="min-h-screen bg-slate-950 p-4 text-slate-100 md:p-8"><div className="mx-auto max-w-7xl">
    <header className="mb-6 flex flex-wrap items-center justify-between gap-3"><div><p className="text-xs font-semibold tracking-[0.2em] text-cyan-400">VISIONSAFE AI</p><h1 className="text-3xl font-bold">Traffic intelligence</h1></div><span className={`rounded-full px-3 py-1 text-sm ${service === "healthy" ? "bg-emerald-950 text-emerald-300" : "bg-amber-950 text-amber-300"}`}>API: {service}</span></header>
    {error && <div role="alert" className="mb-6 rounded-lg border border-amber-800 bg-amber-950/40 p-4 text-amber-200"><strong>Data unavailable.</strong> {error}. Configure `NEXT_PUBLIC_API_URL` and start FastAPI; no traffic fallback is displayed.</div>}
    {!error && !observation && <p className="mb-6 animate-pulse text-slate-400">Loading validated observation...</p>}
    <div className="grid gap-5 lg:grid-cols-3">
      <div className="space-y-5 lg:col-span-2">
        <Panel title="Congestion and vehicle statistics">{observation ? <><p className="mt-1 text-sm text-slate-400">{observation.provenance.is_test_data ? "TEST DATA - not live traffic" : observation.provenance.is_live ? "Live observation" : "Historical observation"} · {observation.name}</p><dl className="mt-4 grid gap-3 sm:grid-cols-2 xl:grid-cols-4"><Metric label="LOS" value={observation.metrics.level_of_service} /><Metric label="Congestion" value={`${Math.round(observation.metrics.congestion_index * 100)}%`} /><Metric label="PCU flow/hour" value={observation.metrics.pcu_flow_rate_per_hour.toFixed(0)} /><Metric label="Speed" value={observation.metrics.physical_speed_available && observation.metrics.estimated_avg_speed_kmh !== null ? `${observation.metrics.estimated_avg_speed_kmh.toFixed(1)} km/h` : "Unavailable"} /></dl><div className="mt-4 grid grid-cols-2 gap-2 sm:grid-cols-4">{Object.entries(observation.metrics.vehicle_counts).map(([name, count]) => <div key={name} className="rounded bg-slate-800 p-2 text-sm"><span className="block text-slate-400">{name.replaceAll("_", " ")}</span>{count}</div>)}</div><p className="mt-3 text-xs text-slate-500">Physical speed is unavailable without camera calibration.</p></> : <p className="mt-3 text-sm text-slate-400">No observation available.</p>}</Panel>
        <Panel title="Congestion forecast"><p className="mt-2 text-sm text-slate-400">Persistence baseline only; not a trained forecast.</p>{forecast.length ? <div className="mt-3 flex h-20 items-end gap-2">{forecast.map((value, index) => <div key={index} className="flex-1 rounded-t bg-cyan-500" style={{ height: `${Math.max(8, value * 100)}%` }} title={`${Math.round(value * 100)}%`} />)}</div> : <p className="mt-3 text-sm text-slate-500">Forecast unavailable.</p>}</Panel>
        <Panel title="Journey search"><form onSubmit={searchJourney} className="mt-3 grid gap-3 sm:grid-cols-2">{journeyFields.map(([name, value]) => <label key={name} className="text-xs text-slate-400">{name}<input required name={name} type="number" step="any" defaultValue={value} className="mt-1 w-full rounded border border-slate-700 bg-slate-950 p-2 text-slate-100" /></label>)}<button className="rounded bg-cyan-600 px-4 py-2 font-medium text-white hover:bg-cyan-500 sm:col-span-2">Compare routes</button></form>{routeError && <p role="alert" className="mt-3 text-sm text-amber-300">Route unavailable: {routeError}</p>}</Panel>
        <Panel title="Route comparison">{routes ? <><RouteMap routes={routes.candidates} selected={selected?.route_id} onSelect={setSelectedRoute} /><p className="mt-3 text-sm text-slate-400">{routes.recommendation_reason}</p><div className="mt-3 grid gap-2">{routes.candidates.map((route) => <button key={route.route_id} onClick={() => setSelectedRoute(route.route_id)} className={`rounded border p-3 text-left ${route.route_id === selected?.route_id ? "border-cyan-400 bg-cyan-950/40" : "border-slate-700"}`}><strong>{route.route_name}</strong><span className="ml-2 text-sm text-slate-400">{route.estimated_duration_minutes} min · {route.distance_km} km · LOS {route.level_of_service}</span><p className="mt-1 text-xs text-slate-500">{route.data_freshness}</p></button>)}</div></> : <p className="mt-3 text-sm text-slate-400">Search a journey to request candidate routes from the API.</p>}</Panel>
      </div>
      <aside className="space-y-5"><Panel title="Traffic video analysis"><form onSubmit={startAnalysis} className="mt-3 space-y-3"><label className="block text-sm text-slate-400">Select video<input name="video" type="file" accept="video/*" className="mt-1 block w-full text-xs" /></label><button className="w-full rounded border border-cyan-500 px-3 py-2 text-sm text-cyan-300">Start analysis</button></form>{job && <p className="mt-3 text-sm text-slate-300">Job {job.job_id}: {job.status} ({job.progress_percent}%)</p>}{jobError && <p role="alert" className="mt-3 text-sm text-amber-300">{jobError}</p>}<p className="mt-3 text-xs text-slate-500">Byte upload is not exposed by the current API; this control remains unavailable for local files.</p></Panel>
        <Panel title="Model metrics"><p className="mt-3 text-sm text-slate-400">No evaluated model artifact or metrics endpoint is available. Kaggle training results must be retrieved and verified before model metrics can be shown.</p></Panel>
        <Panel title="Live telemetry"><p className="mt-3 text-sm text-slate-400">WebSocket telemetry is unavailable because the backend endpoint is not implemented. This dashboard does not simulate tracks.</p></Panel>
      </aside>
    </div>
  </div></main>;
}
