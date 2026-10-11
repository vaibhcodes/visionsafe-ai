# Kaggle Training Guide: VisionSafe AI

## Overview
This guide defines the standardized procedure for training and fine-tuning VisionSafe AI models using Kaggle's cloud GPUs. It ensures reproducibilty, prevents local storage exhaustion, and strictly controls dataset acquisition.

## Prerequisites
1. **Kaggle Account**: Must be active and authenticated.
2. **Kaggle API Credentials**: Ensure your `kaggle.json` is configured locally or the `KAGGLE_USERNAME` and `KAGGLE_KEY` environment variables are set.
3. **Push Script**: Use `scripts/push_to_kaggle.py` to deploy training notebooks directly from this repository to Kaggle.

## Training Workflow
1. **Notebook Preparation**: Training logic is defined in standalone Jupyter notebooks in `backend/ml/`.
   - E.g., `train_vision_model.ipynb` for YOLOv8 object detection.
2. **Push to Kaggle**: Execute the push script to initiate a Kaggle Kernel session.
   Use the central CLI/configuration contract in `backend/ml/README.md` from the
   existing notebook so notebook and backend runs share paths, checkpoints, and
   evaluation commands.
3. **Cloud Execution**:
   - Attach a verified, prepared bounded dataset as a Kaggle input. Inputs are
     read-only under `/kaggle/input/`; do not rely on notebook-time downloads.
   - A smoke test is performed prior to full epoch training.
   - Validation metrics (mAP@50, precision, recall) are logged.
4. **Artifact Retrieval & Persistence**: Once the Kaggle session completes or is interrupted, the output weights (`best.pt`, `last.pt`) and config are bundled in the Kernel's output tab. See `docs/CHECKPOINT_RECOVERY.md` for instructions on how to use `last.pt` to resume training across sessions.
5. **Integration**: Place the retrieved `best.pt` artifact into `models/finetuned/` and update `docs/MODEL_REGISTRY.md`.

## Strict Guardrails
- **No Full Downloads**: Never download the entire ~150GB BMD-45 dataset. Only use targeted validation slices.
- **Leakage Prevention**: Ensure time-series data (for congestion forecasting) is split chronologically, not randomly.
- **Verified Metrics Only**: Do not fabricate evaluation results. All reported metrics must be derived from actual Kaggle output logs.
- **Resumability & Batch Optimization**: The training notebooks implement AutoBatch (`batch=-1`) to prevent Out Of Memory (OOM) errors and require explicit checkpointing (`save_period=5`) to allow seamless resumption. Never train from epoch zero if a valid `last.pt` checkpoint exists.
- **No Local Training**: Laptop development is limited to validation, API
  integration, tests, and small smoke fixtures. Substantial model training is
  executed only on Kaggle.
