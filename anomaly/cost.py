from typing import Dict, Optional
import math

# Simple pricing lookup (USD per hour) - In production, this would call the AWS Price List API
# Values are approximate for us-east-1
PRICING_TABLE = {
    # GPU Instances
    "p4d.24xlarge": 32.77,
    "p3.16xlarge": 24.48,
    "p3.2xlarge": 3.06,
    "g5.48xlarge": 16.29,
    "g5.xlarge": 1.00,
    "g4dn.xlarge": 0.52,
    
    # Standard Instances
    "t3.medium": 0.0416,
    "t3.large": 0.0832,
    "m5.large": 0.096,
    "m5.4xlarge": 0.768,
    "c5.xlarge": 0.17,
    
    # DB Instances
    "db.t3.medium": 0.068,
    "db.m5.large": 0.175,
}

class CostEstimator:
    """Estimates financial impact of cloud resources and anomalies."""
    
    @staticmethod
    def get_hourly_rate(instance_type: str) -> float:
        """Get the hourly rate for a given instance type."""
        return PRICING_TABLE.get(instance_type, 0.10) # Default to 0.10 if unknown

    @staticmethod
    def estimate_burn_rate(resources: list[Dict]) -> float:
        """Calculate total hourly cost for a set of resources."""
        total = 0.0
        for res in resources:
            rate = CostEstimator.get_hourly_rate(res.get("instance_type", ""))
            count = int(res.get("instance_count", 1))
            total += rate * count
        return total

    @staticmethod
    def calculate_cost_score(hourly_impact: float) -> float:
        """Log-scale cost impact to a 0-100 score."""
        if hourly_impact <= 0:
            return 0.0
        # $1/hr -> ~0, $10/hr -> ~33, $100/hr -> ~66, $1000/hr -> ~100
        score = math.log10(hourly_impact + 0.1) * 25 + 25
        return min(100.0, max(0.0, score))

    @staticmethod
    def get_projected_waste(hourly_impact: float, hours: int = 24) -> float:
        """Project the cost if an anomaly continues for a given window."""
        return hourly_impact * hours
