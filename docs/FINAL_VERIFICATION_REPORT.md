# Final Verification Report: VisionSafe AI

**Audit date:** 2026-10-09  
**Scope:** Integrated repository audit; no dataset download or model training was started.

## Commands actually run

```powershell
cmd /c "npm run lint && npm run build"        # frontend/
Invoke-WebRequest http://localhost:8000/api/v1/health -TimeoutSec 5
Get-Command python,py
fsutil volume diskfree E:
git check-ignore -v .venv data/raw/BMD-45/.cache/huggingface/CACHEDIR.TAG .env
git diff --check
```

## Test and command results

| Check | Result | Evidence |
| --- | --- | --- |
| Frontend lint | Passed | `next lint`: no warnings or errors |
| Frontend production build | Passed | Next.js compiled, type-checked, and generated static pages |
| Backend health | Blocked | `localhost:8000` was not listening |
| Backend unit/API/pipeline tests | Blocked | Neither `python` nor `py` is available in the active shell |
| Video upload/analysis | Blocked | No byte-upload endpoint, source video, checkpoint, or running backend |
| Model-training smoke test | Not run | No Python runtime or verified training dataset; Kaggle is the designated training environment |
| Storage inspection | Passed | `E:` has 155.8 GB free of 238.5 GB |
| Ignore rules | Passed for checked paths | Hugging Face cache and `.env` are ignored; binary-data/checkpoint patterns are present in `.gitignore` |

## Features verified by inspection and executable checks

- The frontend calls `/health`, `/corridors/{id}/observation`,
  `/corridors/{id}/forecast`, `/routes/recommend`, and `/streams/jobs` through
  its typed API client. Its route locations use `latitude`/`longitude`, now
  matching the corrected API document and backend model.
- The frontend has verified loading, error, unavailable-service, test-data,
  unavailable-physical-speed, unavailable-model-metrics, unavailable-upload,
  and unavailable-telemetry states. It does not display mock data as live.
- The FastAPI synthetic fixture identifies itself as historical test data and
  does not report physical speed. Its forecast is labelled a persistence test
  baseline rather than a trained model.
- Route scoring is deterministic and has existing unit coverage for congestion,
  delay, and uncertainty penalties.
- `LineCounter` was repaired during this audit: a track ID is now counted only
  once after a valid crossing. A regression test covers an oscillating track.
- Dataset/model training configuration declares distinct train/validation/test
  directories and validates class order. It cannot by itself prove temporal
  separation; the upstream dataset manifest must establish that property.

## Model and evaluation evidence

No trained checkpoint, evaluation report, confusion matrix, held-out metric,
or training log exists in the repository. `MODEL_REGISTRY.md` marks all model
metrics as pending. Therefore:

- **Genuinely trained checkpoints:** none.
- **Held-out metrics actually measured:** none.
- **Model results shown in the UI:** none; the UI explicitly states that model
  metrics are unavailable.

## Unresolved defects and limitations

1. The local Python runtime is unavailable, preventing backend startup, pytest,
   OpenAPI verification, video processing, and API end-to-end testing.
2. `POST /streams/jobs` is an in-memory synthetic-job interface, not a byte
   video-upload endpoint; no annotated video or real inference is verified.
3. PostgreSQL/PostGIS, migrations, persistence, OSM/provider routing,
   WebSocket telemetry, calibrated speed, and real model integration are not
   implemented/verified.
4. No local sample video or verified dataset is present. Full BMD-45 was not
   downloaded and must not be downloaded.
5. The repository has no Git commits; all project files are currently untracked.

## Exact launch commands

After installing/exposing a supported Python interpreter and creating an
environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r backend\requirements.txt
python -m pytest backend\tests -q
python -m uvicorn backend.main:app --reload --port 8000
```

In another terminal:

```powershell
cd frontend
cmd /c npm ci
$env:NEXT_PUBLIC_API_URL = "http://localhost:8000/api/v1"
cmd /c npm run dev
```

Open `http://localhost:3000` and `http://localhost:8000/docs`. Do not use the
synthetic test fixture as evidence of live traffic, tracking accuracy, or model
performance.
