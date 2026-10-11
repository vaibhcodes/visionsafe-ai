# VisionSafe AI backend: development vertical slice

This is a small FastAPI vertical slice, not a production video pipeline.  It
uses only an in-memory, clearly labelled synthetic fixture
(`synthetic-test-corridor-1`); it reads no video, downloads no dataset, runs no
YOLO model, and does not claim live traffic or physical speed.

## Setup and run

From the repository root, use a Python 3.11--3.13 environment (the project
status lists a launcher separately; availability must be verified locally):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r backend\requirements.txt
python -m uvicorn backend.main:app --reload --port 8000
```

Open `http://localhost:8000/docs`. The API base is `/api/v1`.

Run the tests:

```powershell
python -m pytest backend/tests -q
```

## What the fixture demonstrates

- `GET /api/v1/health` returns a standard success envelope.
- `POST /api/v1/streams/jobs` queues an in-memory fixture job; `GET` of its
  job resource reports status.
- `GET /api/v1/corridors/synthetic-test-corridor-1/observation` exposes a
  PCU-weighted observation with `is_test_data: true` and no physical speed.
- `GET /api/v1/corridors/{id}/forecast` uses a labelled persistence baseline.
- `POST /api/v1/routes/recommend` scores geometric, synthetic candidates only.

The congestion baseline is PCU flow divided by supplied capacity, clamped to
`[0, 1]`, with the documented LOS thresholds. Route scoring is lower-is-better:
free-flow time plus congestion, delay, and uncertainty penalties.

## Storage and database status

No data, checkpoints, database files, or routes are written by this slice.
PostgreSQL/PostGIS is not configured here. A future development fallback may
use SQLite for non-spatial metadata only; it is not a PostGIS substitute and
must not be used for spatial topology queries.
