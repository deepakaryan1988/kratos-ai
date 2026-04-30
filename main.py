#!/usr/bin/env python3
"""Legacy entry point - use kratos.py instead."""

from app import kratos_engine

def main():
    result = kratos_engine.invoke({
        "findings": [],
        "remediation_plan": "",
        "status": "Initiating"
    })
    print(result['remediation_plan'])

if __name__ == "__main__":
    main()