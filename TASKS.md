# Task Board & Implementation Plan: VisionSafe AI

## Module Ownership & Boundary Rules

To avoid merge collisions and conflicting changes:
- **Gemini**: Owns Frontend (`frontend/`), UI components, client API integration, interactive MapLibre/Deck.gl maps, video telemetry visualizer, and architectural documentation (`docs/`).
- **Codex**: Owns Backend (`backend/`), data pipelines (`data/`), model inference & training (`models/`, `backend/ml/`), CV pipelines (`backend/pipeline/`), routing engine (`backend/routing/`), storage guard scripts, and automated unit/integration tests (`backend/tests/`).
- **Forbidden**: Simultaneous edits to the same files. Gemini and Codex must never write to each other's primary directories.

---

## Phase 0: Foundations, Storage Guardrails & Contracts (COMPLETED)

- [x] **PLAN-01 (Gemini)**: Inspect hardware, storage devices, and identify external SSD (`E:\`, 156.23 GB free).
- [x] **PLAN-02 (Gemini)**: Define storage plan with 25 GB reserve buffer and 15 GB initial raw dataset cap in [STORAGE_PLAN.md](file:///e:/VisionSafe%20AI/docs/STORAGE_PLAN.md).
- [x] **PLAN-03 (Gemini)**: Investigate BMD-45, UVH-26, ITD, and establish bounded dataset acquisition plan in [DATASET_ACQUISITION_PLAN.md](file:///e:/VisionSafe%20AI/docs/DATASET_ACQUISITION_PLAN.md).
- [x] **PLAN-04 (Gemini)**: Define system architecture, 7-class Indo-HCM mapping, and vertical slice flow in [SYSTEM_ARCHITECTURE.md](file:///e:/VisionSafe%20AI/docs/SYSTEM_ARCHITECTURE.md).
- [x] **PLAN-05 (Gemini)**: Specify API schema contracts, data state tags (`live_observation`, `historical`, `forecast`), and endpoints in [API_CONTRACT.md](file:///e:/VisionSafe%20AI/docs/API_CONTRACT.md).

---

## Phase 1: Core Skeletons & Storage Enforcers (IN PROGRESS)

### Codex Tasks (Backend, Data & Testing)
- [ ] **B-01: Storage Guard Utility & Environment Bootstrap**
  - **Owner**: Codex
  - **Scope**: Create `scripts/check_storage.py` that verifies drive `E:` free space >= 25 GB before any task. Bootstrap Python virtual environment `.venv` on `E:\VisionSafe AI\.venv` with environment overrides pointing `HF_HOME`, `TORCH_HOME`, and `ULTRALYTICS_CONFIG_DIR` to `E:\VisionSafe AI\.cache`.
  - **Acceptance Criteria**: Running `python scripts/check_storage.py` succeeds if free space >= 25 GB and exits with non-zero code if below 25 GB.
- [ ] **B-02: FastAPI Application Skeleton & Pydantic Contracts** *(implementation complete; test execution is blocked until a Python interpreter is available in the current shell)*
  - **Owner**: Codex
  - **Scope**: Initialize `backend/` with FastAPI, Pydantic models matching [API_CONTRACT.md](file:///e:/VisionSafe%20AI/docs/API_CONTRACT.md), CORS middleware for Next.js, and health check endpoint `GET /api/v1/health`.
  - **Acceptance Criteria**: FastAPI server starts on port 8000; OpenAPI Swagger docs display all defined schemas; unit tests in `backend/tests/test_health.py` pass.

- [ ] **B-02a: Test-data Backend Vertical Slice** *(implementation complete; verification blocked as above)*
  - **Owner**: Codex
  - **Scope**: Health envelope, in-memory asynchronous video-job interface, explicit synthetic traffic observation fixture, PCU/capacity congestion baseline, persistence forecast fixture, and deterministic geometric route scoring.
  - **Guardrails**: No video/dataset download, no model inference, no physical speed without calibration, no live-traffic or live travel-time claim.
  - **Acceptance Criteria**: `backend/tests/` verifies health, observation provenance, video-job lifecycle, PCU baseline, and route score/recommendation after a supported Python runtime is installed.

- [x] **B-02b: Kaggle-First Training Interface**
  - **Owner**: Codex
  - **Scope**: Add environment-driven training paths, pinned Kaggle dependencies, YOLO configuration, input validation, smoke/train/evaluate/export commands, manifests, and checkpoint recovery handoff.
  - **Acceptance Criteria**: `backend/ml/README.md` documents Kaggle inputs/outputs/commands and the existing notebook can invoke the central CLI without local training or dataset download.

### Gemini Tasks (Frontend & Design System)
- [x] **F-01: Next.js 14 Web Application Skeleton**
  - **Owner**: Gemini
  - **Scope**: Initialize Next.js 14 App Router project in `frontend/` with TypeScript and Tailwind CSS. Setup design tokens (dark mode theme, traffic state color tokens: emerald for free flow, amber for moderate, rose for severe).
  - **Acceptance Criteria**: `npm run dev` builds and renders landing dashboard with no TypeScript or lint warnings.
  - **Verification**: `cmd /c npm run lint` and `cmd /c npm run build` pass on 2026-10-09.
- [ ] **F-02: Typed API Client & Mock State Provider**
  - **Owner**: Gemini
  - **Scope**: Create `frontend/src/services/api/` consuming contracts from [API_CONTRACT.md](file:///e:/VisionSafe%20AI/docs/API_CONTRACT.md). Include mock fallback mode so UI can be fully previewed and tested before backend services boot.
  - **Acceptance Criteria**: Client supports switching between live FastAPI endpoints and typed offline fixtures.
  - **Progress**: Typed client now covers health, observation, forecast, route recommendation, and video-job contracts. It intentionally displays unavailable-data states instead of fabricating traffic; no owner-approved offline fixture source exists.

---

## Phase 2: Vertical Slice Computer Vision & Analytics Pipeline

### Codex Tasks
- [ ] **B-03: Sample Video Ingestion & Bounded Dataset Slice**
  - **Owner**: Codex
  - **Scope**: Download bounded test video clips (<= 500 MB) of Indian traffic corridors into `data/raw/sample_videos/`. Fetch 100 validation frames and annotation sample from BMD-45 / UVH-26 strictly under the 15 GB cap.
  - **Acceptance Criteria**: Total downloads do not exceed 3 GB. Manifest file `data/raw/manifest.json` tracks file sizes and checksums.
- [ ] **B-04: YOLOv8/11 + ByteTrack Inference Pipeline**
  - **Owner**: Codex
  - **Scope**: Implement `backend/pipeline/perception.py` wrapping YOLO and ByteTrack. Detect 7 standardized classes, maintain vehicle IDs across frames, and output bounding boxes + track trajectories.
  - **Acceptance Criteria**: Processes sample video at >= 15 FPS; accurately assigns IDs to vehicles; unit tests verify tracker stability across 100 frames.
  - **Progress**: Lazy Ultralytics ByteTrack adapter and testable tracking/counting interfaces are implemented. Performance/ID-stability verification awaits a validated sample video and checkpoint.
- [ ] **B-05: Counting Tripwires, PCU Calculation & Congestion Estimator**
  - **Owner**: Codex
  - **Scope**: Implement `backend/pipeline/analytics.py` for virtual tripwire counting, Indo-HCM PCU computation, occupancy ratio, and Level of Service (LOS A-F) classification.
  - **Acceptance Criteria**: Emits `LiveTrafficObservation` JSON payload matching [API_CONTRACT.md](file:///e:/VisionSafe%20AI/docs/API_CONTRACT.md).
  - **Progress**: PCU/capacity baseline, LOS mapping, configurable counting line, and occupancy calculation are implemented. Pipeline-to-API emission awaits real video inference.
  - **Audit repair**: Counting is idempotent per track ID for a configured line; regression coverage prevents oscillation-driven duplicate counts.

### Gemini Tasks
- [ ] **F-03: Real-Time Traffic Telemetry Dashboard**
  - **Owner**: Gemini
  - **Scope**: Build interactive dashboard in `frontend/src/components/telemetry/` showing vehicle counts by mode (2W, 3W, car, bus, truck), PCU flow rate gauge, LOS status indicator, and temporal state badge (`LIVE OBSERVATION` vs `HISTORICAL`).
  - **Acceptance Criteria**: Visually responsive, high-aesthetic dark theme with animated PCU gauges.
  - **Progress**: Responsive congestion, PCU, LOS, vehicle-count, forecast, provenance, loading, and unavailable-data panels are implemented against REST data. Live WebSocket telemetry and animation remain unavailable until INT-01 backend support exists.
- [ ] **F-04: Video Inference Overlay Player**
  - **Owner**: Gemini
  - **Scope**: Build canvas/video component rendering live or sample video with synchronized vehicle bounding boxes, class labels, and virtual counting tripwire overlay.
  - **Acceptance Criteria**: Smooth frame rendering synchronized with incoming telemetry timestamps.
  - **Progress**: Video-analysis job control and explicit byte-upload/telemetry-unavailable state are implemented. An overlay player cannot be completed until the backend accepts uploads and exposes frame telemetry.

---

## Phase 3: Route Recommendation Engine & Map Integration

### Codex Tasks
- [ ] **B-06: OSM Road Graph Ingestion & Congestion-Aware Router**
  - **Owner**: Codex
  - **Scope**: Ingest bounded Bengaluru road network extract into NetworkX / pgRouting graph. Implement route costing penalty function integrating real-time CV observations and historical link speeds.
  - **Acceptance Criteria**: `POST /routes/recommend` returns 2-3 candidate routes with duration, distance, bottleneck warnings, and GeoJSON polylines.

### Gemini Tasks
- [ ] **F-05: Interactive Map & Candidate Route Comparison UI**
  - **Owner**: Gemini
  - **Scope**: Implement MapLibre GL map view rendering corridor CCTV markers, route candidate polylines color-coded by congestion level (green/amber/red), and route comparison card (ETA, distance, savings).
  - **Acceptance Criteria**: Clicking candidate routes highlights the path and updates the bottleneck breakdown.
  - **Progress**: Interactive returned-GeoJSON route visualization, candidate selection, and actual route comparison are implemented. It uses no external basemap or fabricated traffic; OSM/map tiles await B-06/provider configuration.

---

## Phase 4: Model Fine-Tuning & Evaluation on Indian Datasets

### Codex Tasks
- [ ] **B-07: Domain Adaptation Training on Indian Traffic Benchmark**
  - **Owner**: Codex
  - **Scope**: Prepare YOLO training dataset using bounded BMD-45 and UVH-26 subsets. Fine-tune on Kaggle; log mAP@50 and mAP@50:95 across the 7 classes. Local development is validation/inference-only.
  - **Acceptance Criteria**: Actual training logs produced in `runs/detect/`; no fabricated metrics; evaluation confusion matrix generated.
- [ ] **B-08: Congestion Prediction Baseline (XGBoost / Random Forest)**
  - **Owner**: Codex
  - **Scope**: Train tabular model predicting corridor PCU and speed 15, 30, and 60 minutes ahead using historical patterns and current CV observations.
  - **Acceptance Criteria**: Evaluate with MAE and RMSE against held-out temporal validation set. Produce model card and metrics report.

---

## Phase 5: End-to-End Integration & System Hardening

- [ ] **INT-01 (Gemini & Codex)**: Connect frontend WebSocket client to backend telemetry stream for real-time video inference playback.
- [ ] **INT-02 (Codex)**: Comprehensive test suite (unit tests, API contract integration tests, pipeline latency benchmarks).
  - **Audit status**: Frontend lint/build pass. Backend suite, API integration, and pipeline benchmark remain blocked by the missing Python runtime, running backend service, checkpoint, and validated sample video; see `docs/FINAL_VERIFICATION_REPORT.md`.
- [ ] **INT-03 (Gemini)**: Polishing UI micro-animations, loading states, error boundaries, and responsive layout.
