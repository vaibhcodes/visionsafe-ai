"""Central paths and settings shared by Kaggle training and local smoke checks."""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _path_from_env(name: str, default: str) -> Path:
    return Path(os.environ.get(name, default)).expanduser()


@dataclass(frozen=True)
class TrainingPaths:
    """Paths are configurable; Kaggle inputs remain read-only by convention."""
    dataset_root: Path
    runs_dir: Path
    models_dir: Path
    artifact_root: Path
    config_path: Path
    data_yaml: Path
    resume_checkpoint: Path | None

    @classmethod
    def from_environment(cls) -> "TrainingPaths":
        kaggle = bool(os.environ.get("KAGGLE_KERNEL_RUN_TYPE"))
        root = "/kaggle" if kaggle else "."
        dataset_root = _path_from_env("VISIONSAFE_DATASET_ROOT", f"{root}/input/visionsafe-indian-traffic" if kaggle else "data/processed/detection")
        artifact_root = _path_from_env("VISIONSAFE_ARTIFACT_ROOT", f"{root}/working/visionsafe_artifacts" if kaggle else "runs/artifacts")
        resume_raw = os.environ.get("VISIONSAFE_RESUME_CHECKPOINT")
        return cls(
            dataset_root=dataset_root,
            runs_dir=_path_from_env("VISIONSAFE_RUNS_DIR", f"{root}/working/runs" if kaggle else "runs"),
            models_dir=_path_from_env("VISIONSAFE_MODELS_DIR", "models"),
            artifact_root=artifact_root,
            config_path=_path_from_env("VISIONSAFE_TRAIN_CONFIG", "backend/ml/configs/vision_detection.yaml"),
            data_yaml=_path_from_env("VISIONSAFE_DATA_YAML", str(dataset_root / "data.yaml")),
            resume_checkpoint=Path(resume_raw) if resume_raw else None,
        )
