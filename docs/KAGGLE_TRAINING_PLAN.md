# Kaggle Training Plan: VisionSafe AI

## Phase 1: YOLOv8 Vehicle Detection (Prioritized)

We prioritize a working YOLO detector because downstream tasks (tracking, counting, congestion) depend on valid bounding boxes.

- **Dataset Input**: Explicit bounding of max 100 train / 20 val images via `_annotations.coco.json` metadata inspection using HuggingFace Hub directly within the notebook.
- **Notebook**: `backend/ml/train_vision_model.ipynb`
- **Initial Checkpoint**: `yolo11n.pt`
- **Batch-Size Strategy**: AutoBatch (`batch=-1`) to prevent Kaggle GPU OOM.
- **Checkpoint Recovery**: `save_period=5`. Checks for `/kaggle/input/visionsafe-yolo-training/last.pt` to resume interrupted sessions using `resume=True`.
- **Metrics**: mAP@50, mAP@50-95, Precision, Recall on a held-out split.
- **Output**: `visionsafe_artifacts.zip` containing `best.pt`.
- **Manual Actions Required**: 
  1. Login to Kaggle and click **Create > New Notebook**.
  2. Click **File > Import Notebook** and select `backend/ml/train_vision_model.ipynb`.
  3. Under the **Session Options** panel, ensure **Internet is turned ON**.
  4. Ensure the Accelerator is set to **GPU T4x2** or **P100**.
  5. Click **Run All**. 
  6. The notebook will automatically download the metadata, pull exactly 100 train / 20 val images, convert annotations to YOLO, and run a 1-epoch Smoke Test. 
  7. **Full Training is explicitly opt-in.** To start full training, change `RUN_FULL_TRAINING = True` in the final cell (Stage H) and re-run that cell. If Kaggle times out, attach the output to a new notebook and repeat.

## Phase 2: ByteTrack & Counting Validation
*Not a training phase.*
- **Action**: Run `backend/pipeline/perception.py` locally on small UVH-26 sample videos using the Kaggle-trained YOLO weights to validate tracking accuracy.

## Phase 3: Congestion & Forecasting Models (Deferred)
- **Status**: Blocked.
- **Reason**: We currently lack labeled congestion data and chronological time-series traffic flow data.
- **Action Plan**: Once Phase 2 is complete, we will use the CV pipeline to generate synthetic time-series telemetry from video feeds, which will then serve as the training dataset for the XGBoost congestion/forecasting models.
