# Checkpoint & Recovery Guide: VisionSafe AI (Kaggle)

This guide documents the procedures for persisting, retrieving, and resuming YOLO model training on Kaggle.

## 1. Automatic Checkpoint Saving
The Kaggle notebook is configured to automatically manage checkpoints:
- **`last.pt`**: Contains the most recent weights along with the optimizer and scheduler state required to resume an interrupted training session.
- **`best.pt`**: Contains the highest-performing validation weights. Kept strictly separate from the recovery state.
- **`save_period`**: The notebook explicitly saves a checkpoint every 5 epochs (`save_period=5`). 

## 2. Persistence Across Kaggle Sessions
Kaggle's `/kaggle/working` directory is completely wiped at the end of every session. To ensure checkpoints survive:
1. **Wait for Session End**: Ensure the notebook hits either its natural termination or Kaggle's 12-hour timeout. Kaggle automatically bundles the final `/kaggle/working` folder into the kernel's **Outputs**.
2. **Attach Output to Next Session**:
   - To resume, create a new version of the notebook.
   - Click "Add Data" -> "Kernel Output Files".
   - Search for your previous notebook run (e.g., `visionsafe-yolo-training`) and attach it.
   - The files will appear under `/kaggle/input/visionsafe-yolo-training/`.

## 3. Resume Procedure
The `train_vision_model.ipynb` contains an automatic branching mechanism:
```python
resume_checkpoint = '/kaggle/input/visionsafe-yolo-training/last.pt'
if os.path.exists(resume_checkpoint):
    model = YOLO(resume_checkpoint)
    model.train(resume=True, ...)
```
When `resume=True` is passed to Ultralytics YOLO:
1. It reads the previous epoch, configuration (`data.yaml`), and image size directly from `last.pt`.
2. It restores the optimizer state and learning rate scheduler.
3. It seamlessly continues training to reach the original `epochs` target. **Warning:** Do not change configuration arguments when `resume=True` is active, as YOLO strictly enforces the original hyperparameters.

## 4. GPU Inspection & Batch-Size Optimization
- **AutoBatching**: The training script utilizes `batch=-1`. This Ultralytics feature runs a memory profile at the start of training and dynamically scales the batch size to consume ~90% of the available GPU memory (e.g., T4 vs P100).
- **Environment Logging**: The script prints PyTorch versions, CUDA status, and the physical GPU device name (`nvidia-smi`) before downloading data.

## 5. Required Validation
Before doing a multi-day (multi-session) training run, we must pass these tests:
- [x] **Smoke Test**: A 1-epoch test is included to guarantee the dataset slices load without corruption.
- [ ] **Resume Test**: Intentionally halt the notebook at Epoch 6. Attach the output to a new kernel, verify it finds `last.pt`, and confirm training continues at Epoch 7.
- [ ] **Export Test**: Verify `visionsafe_artifacts.zip` successfully exports and can be unzipped locally.
