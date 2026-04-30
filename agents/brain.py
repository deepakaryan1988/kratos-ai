import requests
import os
from vault.policy_store import get_embedding, store_policy, find_similar

def reasoning_node(state: dict):
    print("🧠 KRATOS [Brain]: Analyzing findings with Local Qwen 9B...")
    
    findings_str = "\n".join(state['findings'])

    # Find similar past findings
    similar = []
    try:
        similar = find_similar(state['findings'])
    except Exception:
        pass

    if similar:
        context = "\n".join([f"- {s[0]}: {s[1][:100]}..." for s in similar[:3]])
        prompt = f"""You are KRATOS, an AI Cloud Architect.

Previous similar findings and remediations:
{context}

Current security issues:
{findings_str}

Provide an architectural remediation plan building on similar past cases."""
    else:
        prompt = f"""You are KRATOS, an AI Cloud Architect.
    The following security issues were found:
    {findings_str}

    Provide a brief architectural remediation plan and a sample Terraform snippet to fix these."""

    # Pointing to your LM Studio Windows Host IP
    url = os.getenv("LOCAL_LLM_URL", "http://172.17.0.1:1234/v1") + "/chat/completions"
    
    try:
        response = requests.post(url, json={
            "model": os.getenv("LOCAL_LLM_MODEL", "qwen3.5-9b-claude-4.6-opus-reasoning-distilled-v2"),
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 500
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