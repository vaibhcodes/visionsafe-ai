from backend.ml.training_config import TrainingPaths


def test_kaggle_environment_paths_are_centralized(monkeypatch):
    monkeypatch.setenv("KAGGLE_KERNEL_RUN_TYPE", "Interactive")
    monkeypatch.delenv("VISIONSAFE_DATASET_ROOT", raising=False)
    monkeypatch.delenv("VISIONSAFE_RUNS_DIR", raising=False)
    monkeypatch.delenv("VISIONSAFE_ARTIFACT_ROOT", raising=False)

    paths = TrainingPaths.from_environment()

    assert str(paths.dataset_root) == "/kaggle/input/visionsafe-indian-traffic"
    assert str(paths.runs_dir) == "/kaggle/working/runs"
    assert str(paths.artifact_root) == "/kaggle/working/visionsafe_artifacts"


def test_explicit_environment_paths_override_defaults(monkeypatch):
    monkeypatch.setenv("VISIONSAFE_DATASET_ROOT", "/tmp/dataset")
    monkeypatch.setenv("VISIONSAFE_ARTIFACT_ROOT", "/tmp/artifacts")

    paths = TrainingPaths.from_environment()

    assert str(paths.dataset_root) == "/tmp/dataset"
    assert str(paths.data_yaml) == "/tmp/dataset/data.yaml"
    assert str(paths.artifact_root) == "/tmp/artifacts"
