#!/usr/bin/env python3
"""KRATOS Autonomous Security Agent"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agent.watcher import ChangeWatcher
from app import kratos_engine

def scan_and_notify():
    """Run scan and prepare for notification"""
    print("\n=== KRATOS Autonomous Scan ===")
    result = kratos_engine.invoke({
        "findings": [],
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