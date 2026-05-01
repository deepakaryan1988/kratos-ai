import math
from datetime import datetime
from typing import Dict, Optional, Tuple
import psycopg2
from vault.policy_store import get_connection

class BaselineTracker:
    """
    Tracks and updates statistical baselines using Exponentially Weighted 
    Moving Average (EWMA) and Variance.
    """
    
    def __init__(self, alpha: float = 0.15):
        self.alpha = alpha

    def _get_day_type(self, dt: datetime) -> str:
        return "weekend" if dt.weekday() in (5, 6) else "weekday"

    def get_or_create_baseline(self, metric_key: str, dt: datetime) -> Dict:
        """Fetch existing baseline or initialize a new one."""
        hour = dt.hour
        day_type = self._get_day_type(dt)
        
        conn = get_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                "SELECT ewma, ewma_var, sample_count FROM baselines "
                "WHERE metric_key = %s AND hour_bucket = %s AND day_type = %s",
                (metric_key, hour, day_type)
            )
            row = cur.fetchone()
            if row:
                return {"ewma": row[0], "ewma_var": row[1], "count": row[2]}
            return {"ewma": None, "ewma_var": 0.0, "count": 0}
        finally:
            cur.close()
            conn.close()

    def update_baseline(self, metric_key: str, value: float, dt: datetime) -> float:
        """
        Update baseline with new sample and return the Z-score (deviation).
        """
        hour = dt.hour
        day_type = self._get_day_type(dt)
        baseline = self.get_or_create_baseline(metric_key, dt)
        
        count = baseline["count"] + 1
        ewma = baseline["ewma"]
        ewma_var = baseline["ewma_var"]
        z_score = 0.0

        if ewma is None:
            # First sample: initialization
            ewma = value
            ewma_var = 0.0
        else:
            # Calculate Z-score before updating
            std = math.sqrt(ewma_var) if ewma_var > 0 else 0
            if std > 0:
                z_score = abs(value - ewma) / std
            
            # Update EWMA and Variance
            old_ewma = ewma
            ewma = self.alpha * value + (1 - self.alpha) * old_ewma
            ewma_var = self.alpha * (value - old_ewma)**2 + (1 - self.alpha) * ewma_var

        # Persist update
        conn = get_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                "INSERT INTO baselines (metric_key, hour_bucket, day_type, ewma, ewma_var, sample_count, updated_at) "
                "VALUES (%s, %s, %s, %s, %s, %s, NOW()) "
                "ON CONFLICT (metric_key, hour_bucket, day_type) DO UPDATE SET "
                "ewma = EXCLUDED.ewma, ewma_var = EXCLUDED.ewma_var, "
                "sample_count = EXCLUDED.sample_count, updated_at = NOW()",
                (metric_key, hour, day_type, ewma, ewma_var, count)
            )
            conn.commit()
        finally:
            cur.close()
            conn.close()
            
        return z_score
