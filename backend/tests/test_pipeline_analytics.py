from backend.pipeline.analytics import CountingLine, LineCounter, occupancy_ratio
from backend.pipeline.types import Track


def test_line_counter_counts_a_track_only_when_it_crosses():
    counter = LineCounter(CountingLine((0, 5), (10, 5)))
    before = Track(7, "car", 0.9, (3, 1, 5, 3))
    after = Track(7, "car", 0.9, (3, 7, 5, 9))
    assert counter.update([before]) == {}
    assert counter.update([after]) == {"car": 1}
    assert counter.update([after]) == {"car": 1}


def test_line_counter_does_not_recount_an_oscillating_track():
    counter = LineCounter(CountingLine((0, 5), (10, 5)))
    above = Track(42, "auto_rickshaw", 0.9, (3, 1, 5, 3))
    below = Track(42, "auto_rickshaw", 0.9, (3, 7, 5, 9))
    counter.update([above])
    counter.update([below])
    assert counter.update([above]) == {"auto_rickshaw": 1}


def test_occupancy_is_clamped_to_roi():
    tracks = [Track(1, "car", 0.9, (0, 0, 20, 20))]
    assert occupancy_ratio(tracks, 100) == 1.0
