#!/usr/bin/env python3
"""KRATOS - AI Cloud Security Scanner CLI"""

import argparse
from app import kratos_engine

def main():
    parser = argparse.ArgumentParser(description="KRATOS - Cloud Security Scanner")
    parser.add_argument("--dry-run", action="store_true", help="Scan only, no brain analysis")
    parser.add_argument("--approve", action="store_true", help="Approve remediation execution")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show detailed output")
    args = parser.parse_args()

    print("🛡️  KRATOS - AI Cloud Security Scanner")
    print("=" * 50)

    initial_input = {
        "findings": [],
        "anomaly_findings": [],
        "composite_risk_score": 0.0,
        "approved": args.approve,
        "remediation_plan": "",
        "status": "Initiating"
    }

    if args.dry_run:
        # Still use the engine but focus on findings and anomalies
        result = kratos_engine.invoke(initial_input)
        print("\n📋 Scan Results (Deterministic):")
        for finding in result['findings']:
            print(f"  - {finding}")
            
        print("\n🔍 Anomaly Detection Results:")
        if not result.get('anomaly_findings'):
            print("  ✅ No behavioral anomalies detected.")
        for anomaly in result.get('anomaly_findings', []):
            print(f"  - [{anomaly['tier']}] {anomaly['type']}: {anomaly['message']} (Risk: {anomaly['risk']})")
            
        print(f"\n📊 Composite Risk Score: {result.get('composite_risk_score', 0.0):.1f}/100")
    else:
        result = kratos_engine.invoke(initial_input)
        print("\n📋 Scan Results:")
        for finding in result['findings']:
            print(f"  - {finding}")
        print("\n" + "=" * 50)
        print("🏛️  ARCHITECTURAL REMEDIATION:")
        print(result['remediation_plan'])

if __name__ == "__main__":
    main()