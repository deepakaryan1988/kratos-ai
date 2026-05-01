from typing import List, Dict, Optional
import re
from datetime import datetime

class AnomalyEngine:
    """Orchestrates multiple tiers of anomaly detection."""
    
    def __init__(self, rules: List[Dict] = None):
        from .rules import DEFAULT_ANOMALY_RULES
        self.rules = rules or DEFAULT_ANOMALY_RULES

    def detect_t1_anomalies(self, event: Dict) -> List[Dict]:
        """Tier 1: Rule-based (deterministic) anomaly detection."""
        findings = []
        
        # Add context for rules (e.g., current hour)
        now = datetime.utcnow()
        event_with_context = {
            **event,
            "hour": now.hour,
            "day_of_week": now.weekday()
        }

        for rule in self.rules:
            if rule["condition"](event_with_context):
                findings.append({
                    "type": rule["name"],
                    "risk": rule["risk"],
                    "message": rule["message"],
                    "tier": "T1"
                })
        
        return findings

    def analyze(self, event: Dict) -> Dict:
        """Run full anomaly analysis pipeline (T1 + T2)."""
        findings = self.detect_t1_anomalies(event)
        
        # Tier 2: Statistical Analysis
        from .baseline import BaselineTracker
        from .cost import CostEstimator
        
        tracker = BaselineTracker()
        metric_name = event.get("metric_name", "usage")
        metric_key = f"{event.get('account_id', 'local')}:{event.get('region', 'us-east-1')}:{metric_name}:{event.get('resource_id', 'global')}"
        
        value = float(event.get("value", 0.0))
        z_score = tracker.update_baseline(metric_key, value, datetime.utcnow())
        
        # Cost Analysis
        hourly_rate = CostEstimator.get_hourly_rate(event.get("instance_type", ""))
        cost_impact = hourly_rate * float(event.get("instance_count", 1))
        cost_score = CostEstimator.calculate_cost_score(cost_impact)
        
        # Normalize anomaly score (z-score > 3 is significant)
        anomaly_score = min(100.0, (z_score / 5.0) * 100.0) if z_score > 2.0 else 0.0
        
        if anomaly_score > 50:
            findings.append({
                "type": "statistical_anomaly",
                "risk": anomaly_score,
                "message": f"Statistical anomaly detected in {metric_name} (Z-score: {z_score:.2f})",
                "tier": "T2"
            })

        t1_score = max([f["risk"] for f in findings if f["tier"] == "T1"]) if any(f["tier"] == "T1" for f in findings) else 0.0
        
        # PERSIST: Store in database for history and feedback loop
        from vault.policy_store import get_connection
        conn = get_connection()
        cur = conn.cursor()
        try:
            for f in findings:
                cur.execute(
                    "INSERT INTO anomaly_events (anomaly_type, resource_id, account_id, metric_name, observed_value, z_score, composite_score, tier) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                    (f["type"], event.get("resource_id"), event.get("account_id"), event.get("metric_name"), value, z_score, f["risk"], f["tier"])
                )
            conn.commit()
        except Exception as e:
            print(f"Error persisting anomaly: {e}")
        finally:
            cur.close()
            conn.close()

        return {
            "findings": findings,
            "scores": {
                "policy_risk": t1_score,
                "anomaly_risk": anomaly_score,
                "cost_risk": cost_score
            },
            "z_score": z_score,
            "cost_impact": cost_impact
        }
