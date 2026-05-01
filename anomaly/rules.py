import re
from typing import Dict, List

# GPU instance types pattern
GPU_INSTANCE_PATTERN = r"^(p[2-5]|g[4-6]|inf[1-2]|trn[1-2]|dl[1-2])\."

DEFAULT_ANOMALY_RULES = [
    {
        "name": "sustained_high_utilization",
        "condition": lambda e: (
            e.get("metric_name") in ("CPUUtilization", "GPUUtilization") and 
            float(e.get("value", 0)) > 90.0
        ),
        "risk": 75,
        "message": "Sustained high utilization (>90%) detected. Potential runaway process or unauthorized workload."
    },
    {
        "name": "high_cost_gpu_detected",
        "condition": lambda e: (
            e.get("resource_type") == "ec2" and 
            re.match(r"^p4d\.", e.get("instance_type", ""))
        ),
        "risk": 95,
        "message": "CRITICAL: Ultra-high-cost p4d instance detected. Immediate review required."
    },
    {
        "name": "gpu_usage_outside_business_hours",
        "condition": lambda e: (
            e.get("resource_type") == "ec2" and 
            re.match(GPU_INSTANCE_PATTERN, e.get("instance_type", "")) and 
            (e["hour"] < 8 or e["hour"] > 20)
        ),
        "risk": 85,
        "message": "High-cost GPU resource detected outside business hours (8AM-8PM UTC)."
    },
    {
        "name": "gpu_usage_weekend",
        "condition": lambda e: (
            e.get("resource_type") == "ec2" and 
            re.match(GPU_INSTANCE_PATTERN, e.get("instance_type", "")) and 
            e["day_of_week"] in (5, 6)
        ),
        "risk": 90,
        "message": "High-cost GPU resource detected on weekend."
    },
    {
        "name": "unusual_iam_activity_window",
        "condition": lambda e: (
            e.get("resource_type") == "iam" and 
            (e["hour"] >= 0 and e["hour"] <= 4)
        ),
        "risk": 60,
        "message": "IAM configuration change detected during graveyard hours (0-4AM UTC)."
    },
    {
        "name": "expensive_resource_scale_up",
        "condition": lambda e: (
            e.get("resource_type") == "ec2" and 
            int(e.get("instance_count", 1)) > 10
        ),
        "risk": 70,
        "message": "Large scale-up event detected (>10 instances)."
    }
]
