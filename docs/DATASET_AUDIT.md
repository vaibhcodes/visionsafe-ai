# Dataset Audit & Inventory: VisionSafe AI

**Audit Date:** 2026-10-10
**Status:** Audit complete. No datasets have been downloaded, processed, or trained on yet.

## Dataset Inventory

| Dataset | Source | Purpose | Status | Local Files | Kaggle Attached | Trained On |
|---|---|---|---|---|---|---|
| **BMD-45** | [IISc-AIM (HuggingFace)](https://huggingface.co/datasets/iisc-aim/BMD-45) | Vehicle detection (7-class) | A. Identified | None (empty cache dir) | No | No |
| **UVH-26** | [IISc-AIM (HuggingFace)](https://huggingface.co/datasets/iisc-aim/UVH-26) | Tracking & counting video sequences | A. Identified | None | No | No |
| **Indian Traffic Dataset (ITD)** | [TEG-IITR (GitHub)](https://github.com/teg-iitr/ITD-Indian-traffic-dataset) | Detection & PCU analysis | A. Identified | None | No | No |
| **Indian Road Dataset** | [ThirdEyeLabs (HuggingFace)](https://huggingface.co/datasets/thirdeyelabs/indian-road-dataset) | Diverse urban detection | A. Identified | None | No | No |
| **OpenStreetMap** | [OSM Export](https://www.openstreetmap.org/export) | Route graph | A. Identified | None | No | No |

*Note on Statuses:*
A = Identified, B = Downloaded, C = Processed, D = Kaggle Attached, E = Trained.

## Missing Data & Unsuitable Combinations
- **Vehicle Detection**: BMD-45 is massive (~150GB). We must only use the validation slice (`BMD-45-Val`) to fit Kaggle disk limits.
- **Congestion Classification**: No robust, labeled congestion dataset (e.g., ground-truth LOS ratings mapped to visual feeds) exists in the current inventory.
- **Traffic Forecasting**: We lack genuine timestamped, chronological historical traffic flow logs. We cannot train a forecasting model without time-series data.
- **Route Recommendation**: OSM provides the static network, but we lack live/historical travel times. Routing will rely on synthetic/fallback free-flow approximations until telemetry is gathered.

## Recommended Dataset Strategy
1. **Download Bounded Subset Natively in Kaggle**: The full dataset is ~153 GB. The updated `train_vision_model.ipynb` notebook uses `huggingface_hub` to download *only* the `_annotations.coco.json` metadata for both Train and Val splits. It parses the metadata and sequentially fetches a strict, user-defined maximum number of images (e.g., 100 train, 20 val) directly from the HuggingFace paths, ensuring storage limits are inherently respected before downloading actual pixels.
2. **Download UVH-26 Sample Videos Locally**: Download a small subset (<= 5 GB) of UVH-26 strictly for local tracking/analytics pipeline validation.
3. **Defer Forecasting & Congestion ML**: Wait until the CV pipeline can generate synthetic time-series data from UVH-26 videos, or source a dedicated traffic flow dataset.
