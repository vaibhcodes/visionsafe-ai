"""Kaggle-first YOLO entry point. It never starts training at import time."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

from backend.ml.training_config import TrainingPaths

EXPECTED_CLASSES = ["two_wheeler", "auto_rickshaw", "car", "lcv", "bus", "truck", "vru"]


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise ValueError(f"Required YAML file does not exist: {path}")
    with path.open(encoding="utf-8") as handle:
        value = yaml.safe_load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"YAML root must be a mapping: {path}")
    return value


def validate_dataset(data_yaml: Path) -> dict[str, Any]:
    """Validate declared inputs only; this function never downloads or alters data."""
    data = load_yaml(data_yaml)
    if data.get("names") != EXPECTED_CLASSES:
        raise ValueError(f"Expected class order {EXPECTED_CLASSES}, got {data.get('names')}")
    base = Path(data.get("path", data_yaml.parent))
    if not base.is_absolute():
        base = data_yaml.parent / base
    paths = {split: (Path(data[split]) if Path(data[split]).is_absolute() else base / data[split]) for split in ("train", "val", "test")}
    missing = [f"{split}={path}" for split, path in paths.items() if not path.is_dir()]
    if missing:
        raise ValueError("Missing dataset split directories: " + ", ".join(missing))
    if len({path.resolve() for path in paths.values()}) != 3:
        raise ValueError("train, val, and test directories must be distinct")
    return {"data_yaml": str(data_yaml), "class_names": data["names"], "splits": {key: str(value) for key, value in paths.items()}}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_manifest(paths: TrainingPaths, config: dict[str, Any], dataset: dict[str, Any], run_dir: Path) -> Path:
    paths.artifact_root.mkdir(parents=True, exist_ok=True)
    payload = {"created_at": datetime.now(UTC).isoformat(), "training_config": config,
               "data_yaml": str(paths.data_yaml), "data_yaml_sha256": sha256(paths.data_yaml),
               "dataset_validation": dataset, "run_dir": str(run_dir)}
    output = paths.artifact_root / "run_manifest.json"
    output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return output


def train(paths: TrainingPaths, smoke: bool) -> None:
    config, dataset = load_yaml(paths.config_path), validate_dataset(paths.data_yaml)
    run_name = f"{config['run_name']}-smoke" if smoke else config["run_name"]
    manifest = write_manifest(paths, config, dataset, paths.runs_dir / run_name)
    from ultralytics import YOLO  # Avoids a heavyweight import for validation only.
    if paths.resume_checkpoint:
        if not paths.resume_checkpoint.is_file():
            raise ValueError(f"Resume checkpoint does not exist: {paths.resume_checkpoint}")
        result = YOLO(str(paths.resume_checkpoint)).train(resume=True, project=str(paths.runs_dir), name=run_name)
    else:
        result = YOLO(config["base_model"]).train(data=str(paths.data_yaml), epochs=int(config["smoke_epochs"] if smoke else config["epochs"]), imgsz=int(config["image_size"]), batch=config["batch"], device=config["device"], seed=int(config["seed"]), project=str(paths.runs_dir), name=run_name, save=True, save_period=int(config["save_period"]), exist_ok=True, workers=int(config["workers"]), deterministic=True)
    print(f"Training completed. Manifest: {manifest}; result: {result}")


def evaluate(paths: TrainingPaths, checkpoint: Path) -> None:
    validate_dataset(paths.data_yaml)
    if not checkpoint.is_file():
        raise ValueError(f"Checkpoint does not exist: {checkpoint}")
    from ultralytics import YOLO
    metrics = YOLO(str(checkpoint)).val(data=str(paths.data_yaml), split="test", project=str(paths.runs_dir), name="evaluation", exist_ok=True)
    report = {"checkpoint": str(checkpoint), "map50": metrics.box.map50, "map50_95": metrics.box.map, "precision": metrics.box.mp, "recall": metrics.box.mr}
    paths.artifact_root.mkdir(parents=True, exist_ok=True)
    (paths.artifact_root / "evaluation_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("validate", help="Validate YAML and dataset directories only")
    train_parser = commands.add_parser("train", help="Run Kaggle training")
    train_parser.add_argument("--smoke", action="store_true")
    eval_parser = commands.add_parser("evaluate", help="Evaluate held-out test data")
    eval_parser.add_argument("--checkpoint", required=True, type=Path)
    export_parser = commands.add_parser("export", help="Archive a completed run")
    export_parser.add_argument("--run-name", required=True)
    args, paths = parser.parse_args(), TrainingPaths.from_environment()
    if args.command == "validate": print(json.dumps(validate_dataset(paths.data_yaml), indent=2))
    elif args.command == "train": train(paths, args.smoke)
    elif args.command == "evaluate": evaluate(paths, args.checkpoint)
    else:
        source = paths.runs_dir / args.run_name
        if not source.is_dir(): raise ValueError(f"Run directory does not exist: {source}")
        paths.artifact_root.mkdir(parents=True, exist_ok=True)
        print(shutil.make_archive(str(paths.artifact_root / "visionsafe_artifacts"), "zip", source))
    return 0


if __name__ == "__main__":
    try: raise SystemExit(main())
    except ValueError as error:
        print(f"INPUT ERROR: {error}", file=sys.stderr)
        raise SystemExit(2)
