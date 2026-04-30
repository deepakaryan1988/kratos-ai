from langgraph.graph import StateGraph, END
from agents.state import KratosState
from agents.scanner import cloud_scanner_node
from agents.brain import reasoning_node

workflow = StateGraph(KratosState)

# Add Nodes
workflow.add_node("scanner", cloud_scanner_node)
workflow.add_node("brain", reasoning_node)

# Define Logic: Start -> Scanner -> Brain -> End
workflow.set_entry_point("scanner")
workflow.add_edge("scanner", "brain")
workflow.add_edge("brain", END)

kratos_engine = workflow.compile()

if __name__ == "__main__":
    initial_input = {"findings": [], "remediation_plan": "", "status": "Initiating"}
    result = kratos_engine.invoke(initial_input)
    
    print("\n--- KRATOS ARCHITECTURAL DECISION ---")
    print(result['remediation_plan'])