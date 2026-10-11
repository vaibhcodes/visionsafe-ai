"""Transparent congestion baseline used before any trained model exists."""
from dataclasses import dataclass

PCU_FACTORS = {
    "two_wheeler": 0.5, "auto_rickshaw": 0.8, "car": 1.0,
    "lcv": 1.5, "bus": 3.0, "truck": 3.0, "vru": 0.2,
}


@dataclass(frozen=True)
class CongestionEstimate:
    pcu_total: float
    pcu_flow_rate_per_hour: float
    congestion_index: float
    level_of_service: str


def level_of_service(congestion_index: float) -> str:
    """Map the architecture's [0, 1] index to the A--F LOS scale."""
    if congestion_index < 0.15:
        return "A"
    if congestion_index < 0.30:
        return "B"
    if congestion_index < 0.45:
        return "C"
    if congestion_index < 0.70:
        return "D"
    if congestion_index < 0.85:
        return "E"
    return "F"


def estimate_congestion(vehicle_counts: dict[str, int], window_seconds: int, capacity_pcu_per_hour: float) -> CongestionEstimate:
    """PCU/capacity baseline; it is not a trained congestion prediction model."""
    if window_seconds <= 0 or capacity_pcu_per_hour <= 0:
        raise ValueError("window_seconds and capacity_pcu_per_hour must be positive")
    if any(value < 0 for value in vehicle_counts.values()):
        raise ValueError("vehicle counts cannot be negative")
    pcu_total = sum(PCU_FACTORS.get(label, 0.0) * count for label, count in vehicle_counts.items())
    pcu_flow = pcu_total * 3600 / window_seconds
    index = min(pcu_flow / capacity_pcu_per_hour, 1.0)
    return CongestionEstimate(pcu_total, pcu_flow, index, level_of_service(index))
