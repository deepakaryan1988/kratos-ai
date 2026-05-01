from typing import Dict, List

class RiskScorer:
    """Calculates composite risk scores based on multiple signals."""
    
    def __init__(self, weights: Dict[str, float] = None):
        # Default weights from architecture proposal
        self.weights = weights or {
            "policy": 0.40,
            "anomaly": 0.35,
            "cost": 0.25
        }

    def calculate_composite_score(
        self, 
        policy_score: float, 
        anomaly_score: float, 
        cost_score: float
    ) -> float:
        """
        Combine scores into a single 0-100 risk value.
        """
        weighted_score = (
            (policy_score * self.weights["policy"]) +
            (anomaly_score * self.weights["anomaly"]) +
            (cost_score * self.weights["cost"])
        )
        return min(100.0, max(0.0, weighted_score))

    def get_action_level(self, composite_score: float) -> str:
        """Determine the response level based on the composite score."""
        if composite_score >= 80:
            return "CRITICAL_ACTION"
        elif composite_score >= 60:
            return "REMEDIATION_SUGGESTED"
        elif composite_score >= 30:
            return "ALERT"
        return "LOG"
