from typing import TypedDict, List, Annotated
import operator

class KratosState(TypedDict):
    # 'findings' uses operator.add so nodes can append to the list without overwriting
    findings: Annotated[List[str], operator.add]
    # NEW: Structured anomaly findings
    anomaly_findings: Annotated[List[dict], operator.add]
    # NEW: Composite risk score for the current session
    composite_risk_score: float
    # NEW: Human approval flag
    approved: bool
    # The final architectural decision or remediation code
    remediation_plan: str
    # A simple status flag to track where we are in the workflow
    status: str