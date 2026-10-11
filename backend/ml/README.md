# Kaggle-first training interface

All substantial model training runs on Kaggle. Local use is limited to input
validation, inference integration, tests, and small user-provided smoke
fixtures. These scripts never download a dataset themselves.

## Shared environment contract

The existing Kaggle notebook and the CLI share these paths. When
`KAGGLE_KERNEL_RUN_TYPE` exists, the defaults are Kaggle locations.

| Variable | Kaggle default | Purpose |
| --- | --- | --- |
| `VISIONSAFE_DATASET_ROOT` | `/kaggle/input/visionsafe-indian-traffic` | Attached, read-only dataset root |
| `VISIONSAFE_DATA_YAML` | `$VISIONSAFE_DATASET_ROOT/data.yaml` | YOLO split configuration |
| `VISIONSAFE_RUNS_DIR` | `/kaggle/working/runs` | Ultralytics run directory |
| `VISIONSAFE_ARTIFACT_ROOT` | `/kaggle/working/visionsafe_artifacts` | Manifest, report, archive |
| `VISIONSAFE_MODELS_DIR` | `models` | Local integration destination |
| `VISIONSAFE_RESUME_CHECKPOINT` | unset | Attached prior Kaggle `last.pt` |
| `VISIONSAFE_TRAIN_CONFIG` | `backend/ml/configs/vision_detection.yaml` | Central settings |

The prepared Kaggle dataset must contain `data.yaml`, distinct `train`, `val`,
and `test` directories, and exactly the seven harmonized classes in the dataset
plan. Generate temporal splits upstream from a manifest; the CLI rejects only
identical split paths and cannot prove temporal independence by itself.

## Notebook commands

```bash
!pip install -q -r backend/ml/requirements-kaggle.txt
%env VISIONSAFE_DATASET_ROOT=/kaggle/input/visionsafe-indian-traffic
%env VISIONSAFE_RUNS_DIR=/kaggle/working/runs
%env VISIONSAFE_ARTIFACT_ROOT=/kaggle/working/visionsafe_artifacts
!python -m backend.ml.train_vision validate
!python -m backend.ml.train_vision train --smoke
!python -m backend.ml.train_vision train
!python -m backend.ml.train_vision evaluate --checkpoint /kaggle/working/runs/yolo11n-indotraffic-v1/weights/best.pt
!python -m backend.ml.train_vision export --run-name yolo11n-indotraffic-v1
```

For recovery, attach the previous Kaggle output and set
`VISIONSAFE_RESUME_CHECKPOINT` to its `last.pt` before `train`. Expected
outputs: Ultralytics `best.pt`, `last.pt`, plots/confusion matrix under
`VISIONSAFE_RUNS_DIR`; plus `run_manifest.json`, `evaluation_report.json`, and
`visionsafe_artifacts.zip` under `VISIONSAFE_ARTIFACT_ROOT`. Only record actual
evaluation results in the model registry.
