#!/usr/bin/env python3
"""KRATOS Autonomous Security Agent Runner"""

import os
import time
from agents.watcher import ChangeWatcher # I will move watcher.py too
from app import kratos_engine

def scan_and_notify():
    """Run scan and prepare for notification"""
    print("\n=== KRATOS Autonomous Scan ===")
    result = kratos_engine.invoke({
        "findings": [],
        "anomaly_findings": [],
        "composite_risk_score": 0.0,
        "approved": False,
        "remediation_plan": "",
        "status": "Initiating"
    })
    for finding in result['findings']:
        print(f"🚨 {finding}")
    print("\n=== Remediation Plan ===")
    print(result['remediation_plan'][:500])
    return result

def main():
    interval = int(os.getenv("SCAN_INTERVAL", "60"))
    watcher = ChangeWatcher(interval=interval)
    watcher.start(scan_and_notify)

if __name__ == "__main__":
    main()
