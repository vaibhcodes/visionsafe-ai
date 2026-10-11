import pytest
from unittest.mock import MagicMock, patch

from backend.pipeline.perception import UltralyticsByteTrackPipeline

def test_pipeline_raises_file_not_found_if_checkpoint_missing(tmp_path):
    missing_path = tmp_path / "missing.pt"
    with pytest.raises(FileNotFoundError, match="Configured YOLO checkpoint does not exist"):
        UltralyticsByteTrackPipeline(missing_path)

@patch("backend.pipeline.perception.YOLO")
def test_pipeline_loads_model_once_and_exposes_methods(mock_yolo, tmp_path):
    checkpoint = tmp_path / "dummy.pt"
    checkpoint.touch()
    
    mock_instance = MagicMock()
    mock_instance.names = {0: "Hatchback", 1: "Sedan"}
    mock_yolo.return_value = mock_instance
    
    pipeline = UltralyticsByteTrackPipeline(checkpoint)
    
    assert pipeline.names == {0: "Hatchback", 1: "Sedan"}
    mock_yolo.assert_called_once_with(str(checkpoint))
    
    # Test tracking empty result
    mock_track_result = MagicMock()
    mock_track_result.boxes = None
    mock_instance.track.return_value = [mock_track_result]
    
    tracks = pipeline.track_frame(None)
    assert tracks == []
    mock_instance.track.assert_called_once()
