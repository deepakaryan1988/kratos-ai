# KRATOS Architecture Document

**Internal System Design — Not for external distribution**

---

## 1. System Overview

### Goals

Autonomous cloud governance with human oversight. Detect misconfigurations, generate safe remediations, execute only after approval.

### Key Design Principles

| Principle | Implementation |
|-----------|----------------|
| Deterministic Enforcement | Policy Engine uses rules, not AI |
| AI-Assisted Remediation | LLM suggests Terraform only |
| Safety-First Execution | Plan-validate-approve-execute loop |

---

## 2. High-Level Architecture

```
┌────────────────────────────────────────────────────────────────────┐
│                         KRATOS PLATFORM                            │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  ┌─────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐     │
│  │  Event  │───▶│Detection  │───▶│Policy    │───▶│AI Brain  │──┐
│  │Source   │    │(Scanner)  │    │Engine    │    │(Suggest) │  │
│  └─────────┘    └──────────┘    └────┬─────┘    └──────────┘  │
│                                     │                          ▼
│                                     │                    ┌──────────┐
│                                     ▼                    │Approval  │
│                              ┌────────────┐             │(Human)   │
│                              │Vector DB   │◀────────────┤Gating   │
│                              │(Context)   │             └────┬─────┘
│                              └────────────┘                  │
│                                     ▲                          │
│                                     │                          │
│                              ┌────┴─────┐                     │
│                              │Executor   │◀────────────────────┘
│                              │(Terraform)│
│                              └────┬─────┘
│                                     │
│                                     ▼
│                              ┌────────────┐
│                              │Feedback     │
│                              │(State Store)│
│                              └────────────┘
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

### Flow

1. **Event**: CloudTrail or polling detects resource change
2. **Detection**: Scanner collects resource state
3. **Policy Engine**: Applies deterministic rules, outputs risk score
4. **AI Brain**: If risk HIGH, generates Terraform suggestion (temperature=0)
5. **Approval**: Human gate for HIGH risk actions
6. **Executor**: Validates plan, applies via Terraform
7. **Feedback**: State stored for future context

---

## 3. Policy Engine Design

### Rationale

AI hallucinations and non-determinism are unacceptable for enforcement. Policy Engine is pure code/rules.

### Rule Structure

Rules defined in `vault/policy_engine.py`:

```python
RULES = [
    {
        "name": "s3_kms_required",
        "resource": "s3",
        "condition": "server_side_encryption_configuration.rules[0].apply_server_side_encryption_by_default.sse_algorithm != 'aws:kms'",
        "risk": "HIGH",
        "remediation_template": "s3_kms_terraform.tf"
    },
    {
        "name": "ec2_public_ip",
        "resource": "ec2",
        "condition": "public_ip_address != null",
        "risk": "HIGH",
        "remediation_template": "ec2_private_subnet.tf"
    }
]
```

### Risk Scoring

```
Risk = POLICY_RULE.risk + CONTEXT.risk_modifier

HIGH: Requires approval, immediate action
MEDIUM: 5-min auto-approval, rollback ready
LOW: Auto-execute with notification
```

### Separation from AI

Policy Engine runs first. AI only invoked if:
- Policy score is HIGH
- No destructive action (deletion) without explicit rule

---

## 4. AI Brain Design

### Role

Terraform generation ONLY. Not enforcement.

### Prompt Structure

```python
PROMPT = f"""
Context from similar findings:
{similar_findings_context}

Resource: {resource_json}
Policy Violation: {policy_violation}

Generate Terraform to fix. Output valid HCL only.
Temperature=0
"""
```

### Context Injection

1. Query Vector DB with current finding
2. Retrieve top-5 similar past remediations
3. Inject as context in prompt

### Temperature=0

Ensures deterministic output. Same input → same Terraform every time.

---

## 5. Terraform Execution & Validation Layer

### Validation Pipeline

```
1. terraform fmt -check
2. terraform validate
3. terraform plan -out=plan.tfplan
4. Policy check on plan (deny public access, destructive actions)
5. Approval gate
6. terraform apply plan.tfplan
```

### Guardrails

| Rule | Implementation |
|------|----------------|
| No destructive without approval | Policy Engine blocks, approval required |
| No direct SDK/API | All changes via Terraform state |
| Plan must succeed | Validation fails → blocked |

---

## 6. Safety & Failure Handling

| Failure | Fallback |
|---------|----------|
| LLM fails | Skip remediation, alert |
| Invalid Terraform | Block, alert, log prompt |
| Approval timeout (24h) | Alert, mark as ignored |
| Partial execution | Rollback via stored previous state |
| Duplicate events | Event ID deduplication |

### Guarantees

- **At-most-once execution**: Event deduplication
- **Rollback available**: Previous state stored per resource
- **No destructive unapproved**: Policy Engine prevents

---

## 7. Idempotency & Event Handling

### Event Deduplication

```python
seen_events = RedisSet()  # TTL 24h
if event_id in seen_events:
    return  # Skip
seen_events.add(event_id)
```

### Resource State Check

Before execution:
```python
current_state = aws.resource_get(resource_id)
if current_state != expected_state:
    re-evaluate policy
```

### Terraform State Role

- Source of truth for idempotency
- Backend: Local file (dev), S3+Lock (prod)

---

## 8. Observability Design

### Logging

```python
logger.info({
    "trace_id": trace_id,
    "component": "scanner",
    "resource": resource_id,
    "risk": "HIGH",
    "action": "policy_evaluated"
})
```

### Metrics

```
scan_findings_total{resource_type, risk_level}
active_remediations
remediation_duration_seconds{risk_level}
approval_latency_seconds
```

### Tracing

- OpenTelemetry integration planned
- Trace ID propagated through all components
- Spans: detection, policy_eval, ai_generate, approval, execute

---

## 9. Security Model

### IAM Separation

| Component | Permissions |
|-----------|-------------|
| Scanner | ReadOnlyAccess + Describe* |
| Executor | AssumeRole per-account terraform-deploy |
| AI Brain | No AWS permissions |

### Approval Gating

```python
if risk == "HIGH":
    require_approval("telegram://...")
elif risk == "MEDIUM":
    auto_approve_after(300)  # 5 min
else:
    auto_execute()
```

### Terraform Lockdown

Policy Engine blocks:
- `aws_instance` with `instance_type` containing "gpu" (configurable)
- `terraform` blocks with `delete` lifecycle

---

## 10. Vector Database Design

### Purpose

Context retrieval for LLM. NOT enforcement.

### Retrieval Strategy

```python
finding_text = f"{resource_type} {violation_description}"
embedding = llm.embed(finding_text)
similar = db.query(embedding, k=5)
context = "\n".join([r.remediation for r in similar])
```

### Fallback

If Vector DB down:
- Proceed without context
- Log degraded experience
- Alert monitoring

---

## 11. Scale & Performance Considerations

### Current Limits

- Single AWS account (LocalStack)
- Single LLM instance
- Polling-based detection

### Bottlenecks

- LLM latency: ~2-5s per suggestion
- AWS API rate limits
- No queuing system

### Scaling Plan

| Dimension | Solution |
|-----------|----------|
| Multi-account | AWS Organizations + role assumption |
| LLM scaling | Async queue, batch processing |
| Rate limits | Token bucket per service |

---

## 12. Cost Governance Use Case

### Scenario

Friday 18:00: `p4d.24xlarge` (x4) launched → $1,536/weekend risk.

### Flow

```
[Event] EC2 RunInstances → p4d.24xlarge

[Detection] Resource state captured

[Policy Engine] 
  Rule: ec2_high_cost_instance
  Condition: instance_type matches "p[3-5].*" AND hour NOT IN business_hours
  Risk: HIGH

[AI Brain] 
  Generate: resource "aws_instance" "gpu_downgrade" {
    instance_type = "t3.medium"
  }

[Approval] Telegram: "Stop 4×p4d.24xlarge? Est. savings: $1,500"

[Executor] terraform apply → Instances stopped

[Savings] $1,536
```

---

## 13. Trade-offs & Design Decisions

### Why Not Fully Autonomous AI?

Too risky. Hallucinations would cause outages/cost leaks.

### Why Terraform Over SDK?

- Idempotent
- Plan validation
- Rollback capability
- State management

### Why Custom Policy Engine?

OPA is planned. Current custom engine is faster to iterate for PoC.

---

## 14. Known Limitations

- Polling-based (no real CloudTrail)
- Single account
- Single LLM
- No OPA yet
- No Prometheus exporter
- Telegram-only approval

---

**End of Document**