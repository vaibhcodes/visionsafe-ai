# Storage Architecture & Budget Plan: VisionSafe AI

## 1. Physical Drive Verification

A physical and logical inspection of attached storage devices was conducted on 2026-10-09:

| Drive Letter | Volume Label | Bus / Hardware Type | Total Size | Free Space | Used Space | Notes |
|---|---|---|---|---|---|---|
| **C:** | OS | NVMe INTEL SSDPEKNU512GZ | 252.87 GB | 35.74 GB | 217.13 GB | Internal OS SSD (Low free headroom) |
| **D:** | New Volume | Internal Partition | 200.00 GB | 42.89 GB | 157.11 GB | Secondary internal storage |
| **E:** | New Volume | **USB 3.0 External SSD** | **238.47 GB** | **156.23 GB** | 82.24 GB | **Active External SSD Workspace** |

### Key Findings
1. The **external SSD is currently mounted at `E:\`** (detected via `BusType: USB`, FriendlyName `USB 3.0`).
2. Current repository location: `E:\VisionSafe AI`.
3. Total capacity of drive `E:` is **238.47 GB** (approx. 240 GB class SSD), with **156.23 GB free space remaining**.
4. User requirement specifies preserving at least **25 GB free headroom** at all times and initially limiting new raw dataset downloads to **15 GB total** pending explicit user sign-off.

---

## 2. Storage Allocation Budget (Drive E:)

| Category | Initial Budget Cap | Future Scaled Cap | Description / Contents |
|---|---|---|---|
| **Safety Reserve Buffer** | **25.00 GB** | 25.00 GB | Fixed emergency reserve; prevents drive exhaustion, NTFS thrashing, and OS write failures. |
| **Raw Datasets (`data/raw/`)** | **15.00 GB (Strict Cap)** | 35.00 GB | Selected subsets of BMD-45, UVH-26, ITD, plus sample benchmark videos. |
| **Processed / Extracted (`data/processed/`)**| 10.00 GB | 20.00 GB | YOLO-formatted frames, standardized annotations, feature vectors, pre-aggregated tables. |
| **Model Weights & Checkpoints (`models/`)** | 8.00 GB | 15.00 GB | Base YOLO weights (nano/small), ByteTrack trackers, fine-tuned checkpoints, ONNX exports. |
| **Training Runs & Artifacts (`runs/`)** | 6.00 GB | 12.00 GB | MLflow / TensorBoard metrics, evaluation confusion matrices, prediction validation clips. |
| **Database & Caches (`data/db/` & `.cache/`)** | 6.00 GB | 12.00 GB | SQLite/DuckDB/local Postgres data files, huggingface cache, OSM extract graph cache. |
| **Source Code & Virtualenvs** | 5.00 GB | 8.00 GB | Git workspace, frontend `node_modules`, backend `.venv`. |
| **Remaining Free Buffer** | **81.23 GB** | 29.23 GB | Unallocated available drive buffer. |
| **Total Available on E:** | **156.23 GB** | 156.23 GB | |

---

## 3. Directory Structure on External SSD

All high-volume assets reside strictly under `E:\VisionSafe AI\`:

```
E:\VisionSafe AI\
├── .cache/                     # HuggingFace & Torch model download cache (ignored in git)
├── data/
│   ├── raw/                    # Read-only source datasets (capped <= 15 GB initially)
│   │   ├── BMD-45/             # Bounded subset only (validation/sample splits)
│   │   ├── uvh-26/             # Sample traffic clips & STAPLE subset
│   │   ├── itd/                # Sample Indian Highway Capacity Manual annotated samples
│   │   ├── sample_videos/      # Real-world Indian traffic video clips (1080p/720p mp4)
│   │   └── osm/                # OpenStreetMap road network extracts (.pbf / .graphml)
│   ├── processed/              # Normalized format (YOLO labels, unified classes)
│   ├── ground_truth/           # Benchmark labels for tracking & congestion validation
│   └── db/                     # PostGIS / SQLite persistent store files
├── models/
│   ├── pretrained/             # Official weights (yolo11n.pt, etc.)
│   ├── finetuned/              # Domain-adapted Indian traffic checkpoints
│   └── exported/               # TensorRT / ONNX optimized models
├── runs/                       # Training logs, validation inferences, run metrics
└── docs/                       # Architectural and technical documentation
```

---

## 4. Environment and Path Configuration

To prevent any library (e.g. Hugging Face, PyTorch, Ultralytics) from polluting the primary drive `C:\Users\antar\AppData` or `C:\Users\antar\.cache`, the following environment variables must be exported in backend configuration and scripts:

```env
# Storage paths on Drive E:
DATA_DIR=E:/VisionSafe AI/data
MODELS_DIR=E:/VisionSafe AI/models
RUNS_DIR=E:/VisionSafe AI/runs

# Redirect HuggingFace and PyTorch caches away from Drive C:
HF_HOME=E:/VisionSafe AI/.cache/huggingface
TORCH_HOME=E:/VisionSafe AI/.cache/torch
ULTRALYTICS_CONFIG_DIR=E:/VisionSafe AI/.cache/ultralytics
```

---

## 5. Enforcement Protocols

1. **Pre-Download Size Verification**: Every download script or data pipeline must query remote headers (`Content-Length` or API file metadata) before downloading.
2. **Quota Checks**: An automated guardrail utility `scripts/check_storage.py` must run prior to any download or training stage. If free space on drive `E:` falls below 25 GB, the process aborts immediately.
3. **No Redundant Extraction**: Raw `.tar` or `.zip` archives must either be streamed and parsed on-the-fly or deleted immediately after verified decompression.
4. **Git LFS Avoidance**: Raw video and weight binaries must be tracked in `.gitignore` and managed via manifest hashes rather than checked into git.
