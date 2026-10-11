# Training Status: VisionSafe AI

This document tracks the execution status of all model training runs performed on Kaggle.

| Task | Target Model | Dataset | Status | Last Updated | Notes |
|---|---|---|---|---|---|
| **A. Vehicle Detection (V1 Baseline)** | YOLO11n (`yolo11n.pt`) | BMD-45 (Subset: 100 Train / 20 Val) | 🟢 COMPLETED | 2026-10-10 | Run complete (50 Epochs). mAP@50: 0.3396, mAP@50-95: 0.2540. |
| **B. Tracking & Counting** | ByteTrack | N/A (Algorithmic) | ⚪ NOT STARTED | 2026-10-09 | Integration testing required after Detection is complete. |
| **C. Congestion Classification** | Random Forest / XGBoost | Aggregated telemetry | ⚪ NOT STARTED | 2026-10-09 | Awaiting historical telemetry dataset generation. |
| **D. Traffic Forecasting** | Time-Series Baseline | Chronological link data | ⚪ NOT STARTED | 2026-10-09 | Requires actual timestamped observation dataset. |
| **E. Route Recommendation** | Cost-weighted Graph Search | OSM + Telemetry | ⚪ NOT STARTED | 2026-10-09 | Purely algorithmic; no ML training planned currently. |

## Current Execution Blockers
- **Vehicle Detection**: Initial 100-image baseline training is complete. The project is awaiting the download of the `best.pt` Kaggle artifact to `E:\VisionSafe AI\models\` for local inference testing. **Full-Dataset Blocker**: Training on the entire 153 GB BMD-45 dataset is physically impossible in a standard Kaggle Notebook because `/kaggle/working` is capped at ~73 GB. The notebook has been updated with a strict storage gate. To train on the full 153 GB, the dataset must be uploaded as a mounted Kaggle Dataset or training must be moved to an AWS/RunPod instance with >200 GB storage.
- **Congestion & Forecasting**: Blocked pending generation of labeled time-series telemetry data.
