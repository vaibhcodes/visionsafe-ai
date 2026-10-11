# VisionSafe AI frontend

The dashboard consumes the FastAPI API; it deliberately does not render mock
traffic as live data. It exposes loading, backend-unavailable, test-data, and
uncalibrated-speed states.

```powershell
cd frontend
npm ci
$env:NEXT_PUBLIC_API_URL = "http://localhost:8000/api/v1" # optional default
npm run dev
npm run build
```

For the included synthetic API fixture, start the backend first and open
`http://localhost:3000`. The resulting dashboard will visibly label the data as
test data, not a live observation.
