# Model Registry: VisionSafe AI

This registry tracks the approved and integrated machine learning models available for use within the VisionSafe AI backend pipeline.

## 1. Vehicle Detection Models

### `yolo11n-indotraffic-v1`
- **Status**: 🟡 Pending Training
- **Base Model**: Ultralytics YOLO11 Nano (`yolo11n.pt`)
- **Training Data**: BMD-45 (Val Subset, ~3000 images) + UVH-26 (STAPLE Val Subset)
- **Class Mapping (13 Classes)**:
  1. `Hatchback`
  2. `Sedan`
  3. `SUV`
  4. `MUV`
  5. `Bus`
  6. `Truck`
  7. `Three-wheeler`
  8. `Two-wheeler`
  9. `LCV`
  10. `Mini-bus`
  11. `Tempo-traveller`
  12. `Bicycle`
  13. `Van`
- **Metrics (Held-out Test Set)**:
  - **mAP@50**: *Pending*
  - **mAP@50-95**: *Pending*
  - **Precision**: *Pending*
  - **Recall**: *Pending*
- **Artifacts**: Expected at `models/finetuned/yolo11n-indotraffic-v1/best.pt`

## 2. Congestion Classification Models

*(No models trained yet. Awaiting historical feature dataset.)*

## 3. Traffic Forecasting Models

*(No models trained yet. Awaiting sequential time-series traffic logs.)*

---

### How to Import an Artifact
Once a Kaggle training run finishes:
1. Download the output archive `visionsafe_weights.zip` from the Kaggle kernel.
2. Extract the `best.pt` file into `E:\VisionSafe AI\models\finetuned\<model_name>\`.
3. Update this registry with the recorded validation metrics from the Kaggle log.
