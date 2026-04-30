#!/usr/bin/env python3
"""KRATOS - AI Cloud Security Scanner CLI"""

import argparse
from app import kratos_engine

def main():
    parser = argparse.ArgumentParser(description="KRATOS - Cloud Security Scanner")
    parser.add_argument("--dry-run", action="store_true", help="Scan only, no brain analysis")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show detailed output")
    args = parser.parse_args()

    print("🛡️  KRATOS - AI Cloud Security Scanner")
    print("=" * 50)

    initial_input = {
        "findings": [],
        "remediation_plan": "",
        "status": "Initiating"
    }

    if args.dry_run:
        from agents.scanner import cloud_scanner_node
        result = cloud_scanner_node(initial_input)
        print("\n📋 Scan Results:")
        for finding in result['findings']:
            print(f"  - {finding}")
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