"""Deterministic, provider-independent scoring for candidate routes."""
from dataclasses import dataclass


@dataclass(frozen=True)
class RouteScoreInput:
    free_flow_minutes: float
    congestion_index: float
    delay_minutes: float = 0.0
    uncertainty_minutes: float = 0.0


def score_route(route: RouteScoreInput, congestion_weight: float = 0.35,
                delay_weight: float = 1.0, uncertainty_weight: float = 0.5) -> float:
    """Lower is better: free-flow time plus documented congestion/delay uncertainty penalties."""
    if route.free_flow_minutes < 0 or route.delay_minutes < 0 or route.uncertainty_minutes < 0:
        raise ValueError("time components cannot be negative")
    if not 0 <= route.congestion_index <= 1:
        raise ValueError("congestion_index must be between zero and one")
    return round(route.free_flow_minutes * (1 + congestion_weight * route.congestion_index)
                 + delay_weight * route.delay_minutes + uncertainty_weight * route.uncertainty_minutes, 3)
