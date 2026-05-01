import requests
import os
from vault.policy_store import get_embedding, store_policy, find_similar

def reasoning_node(state: dict):
    print("🧠 KRATOS [Brain]: Analyzing findings with Local Qwen 9B...")
    
    findings_str = "\n".join(state['findings'])
    anomaly_str = "\n".join([f"- {a['message']} (Risk: {a['risk']})" for a in state.get('anomaly_findings', [])])
    risk_score = state.get('composite_risk_score', 0.0)

    # Find similar past findings
    similar = []
    try:
        similar = find_similar(state['findings'])
    except Exception:
        pass

    context_str = ""
    if similar:
        context_str = "Previous similar findings and remediations:\n" + \
                     "\n".join([f"- {s[0]}: {s[1][:100]}..." for s in similar[:3]])

    prompt = f"""You are KRATOS, an AI Cloud Architect.
    
{context_str}

SECURITY FINDINGS:
{findings_str}

ANOMALY SIGNALS:
{anomaly_str}
COMPOSITE RISK SCORE: {risk_score}/100

INSTRUCTIONS:
1. If there is a policy violation, provide Terraform to fix the configuration (e.g. enable encryption).
2. If there is a CRITICAL anomaly (Risk > 80), prioritize a SHUTDOWN or ISOLATION plan.
   - For EC2: Generate Terraform to set `instance_state = "stopped"` or remove public routes.
   - Output valid HCL only.
3. Provide a brief architectural explanation for your choice.
"""

    # Pointing to your LM Studio Windows Host IP
    url = os.getenv("LOCAL_LLM_URL", "http://172.17.0.1:1234/v1") + "/chat/completions"
    
    try:
        response = requests.post(url, json={
            "model": os.getenv("LOCAL_LLM_MODEL", "qwen3.5-9b-claude-4.6-opus-reasoning-distilled-v2"),
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 2000
        }, timeout=120)
        msg = response.json()['choices'][0]['message']
        plan = msg.get('content') or msg.get('reasoning_content', '')
    except Exception as e:
        plan = f"Error connecting to Brain: {e}. Switching to Hardcoded Policy: Encrypt all buckets."

    # Store policies in database
    try:
        for finding in state.get('findings', []):
            embedding = get_embedding(finding)
            store_policy(finding, plan, embedding)
    except Exception:
        pass  # Database optional

    return {
        "remediation_plan": plan,
        "status": "Reasoning Complete"
    }