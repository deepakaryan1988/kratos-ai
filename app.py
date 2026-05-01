from langgraph.graph import StateGraph, END
from agents.state import KratosState
from agents.scanner import cloud_scanner_node
from agents.brain import reasoning_node
from agents.anomaly import anomaly_detection_node
from agents.executor import executor_node

workflow = StateGraph(KratosState)

# Add Nodes
workflow.add_node("scanner", cloud_scanner_node)
workflow.add_node("anomaly_engine", anomaly_detection_node)
workflow.add_node("brain", reasoning_node)
workflow.add_node("executor", executor_node)

def check_approval(state: dict):
    """Route based on risk and approval status."""
    if state.get("composite_risk_score", 0) > 50 and not state.get("approved"):
        print("\n⚠️  [GATE]: High risk detected. Pausing for human approval...")
        return "end"
    return "execute"

# Define Logic: Start -> Scanner & Anomaly -> Brain -> (Conditional) -> Executor -> End
workflow.set_entry_point("scanner")
workflow.add_edge("scanner", "anomaly_engine")
workflow.add_edge("anomaly_engine", "brain")

workflow.add_conditional_edges(
    "brain",
    check_approval,
    {
        "execute": "executor",
        "end": END
    }
)

workflow.add_edge("executor", END)

kratos_engine = workflow.compile()

if __name__ == "__main__":
    initial_input = {
        "findings": [], 
        "anomaly_findings": [],
        "composite_risk_score": 0.0,
        "approved": False,
        "remediation_plan": "", 
        "status": "Initiating"
    }
    result = kratos_engine.invoke(initial_input)
    
    print("\n--- KRATOS ARCHITECTURAL DECISION ---")
    print(result['remediation_plan'])