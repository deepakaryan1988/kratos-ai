# KRATOS — AI Cloud Security & Governance Platform

**Autonomous cloud security remediation with deterministic guardrails.**

[![Python](https://img.shields.io/badge/Python-3.12+-3776AB?logo=python)](https://www.python.org/)
[![LangGraph](https://img.shields.io/badge/LangGraph-AI%20Workflow-000000?logo=langchain)](https://www.langchain.com/langgraph)
[![AWS](https://img.shields.io/badge/AWS-Security%20Focused-232F3E?logo=amazon-aws)](https://aws.amazon.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-pgvector-4169E1?logo=postgresql)](https://www.postgresql.org/)

**Status: Beta. Production use requires additional hardening.**

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    KRATOS PLATFORM                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐    ┌────────────┐    ┌──────────┐              │
│  │ CloudTrail/  │───▶│ Policy     │───▶│ AI Brain │───▶ Approval │
│  │ LocalStack   │    │ Engine     │    │ (Suggest)│      ▲     │
│  └──────────────┘    └────────────┘    └──────────┘      │     │
│         │                   │                              │     │
│         ▼                   ▼                              ▼     │
│  ┌──────────────┐    ┌────────────┐    ┌───────────────────────┐    │
│  │  Watcher     │    │ Vector DB  │    │ Executor (Terraform)│    │
│  │ (Polling)    │    │ (PostgreSQL)│    │                     │    │
│  └──────────────┘    └────────────┘    └───────────────────────┘    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## How It Works

1. **Detection**: CloudTrail events or polling detects resource changes
2. **Policy Evaluation**: Deterministic rules evaluate risk (HIGH/MEDIUM/LOW)
3. **AI Suggestion**: LLM proposes Terraform remediation ONLY if policy allows
4. **Controlled Execution**: Approval → Terraform apply with dry-run validation

---

## Documentation

For detailed internal architecture, see [docs/architecture.md](docs/architecture.md).

---

## Safety & Guardrails

### LLM Safety & Determinism
- **Prompt templates**: Strict JSON schema for all LLM inputs
- **Policy constraint injection**: LLM receives only pre-approved remediation patterns
- **Dry-run validation**: All Terraform generates plan before apply
- **Hallucination mitigation**: Vector DB retrieves similar past plans as context
- **Temperature=0**: Deterministic LLM outputs for consistency

### Destructive Action Prevention
- **Approval required**: HIGH-risk actions require explicit approval
- **Read-only default**: Scanner runs with read-only IAM roles
- **Terraform plan validation**: `terraform plan` must succeed before apply
- **No direct API calls**: All changes via Terraform state management

---

## Policy Engine (Deterministic Layer)

AI is NEVER used for enforcement decisions.

```
[Event] → [Policy Rules] → [Risk Score] → [AI Suggestion?] → [Action]
```

**Policy Rules (Current Implementation)**:
- S3: `encryption != aws:kms` → HIGH risk
- IAM: User without MFA active > 90 days → MEDIUM risk  
- EC2: `PublicIpAddress != null` → HIGH risk
- RDS: `PubliclyAccessible == true` → HIGH risk

AI only generates remediation suggestions when policy scores HIGH risk.

---

## Observability

### Logging
- **Structured JSON logs**: Each component logs with correlation IDs
- **Log levels**: DEBUG/TRACE, INFO, WARN, ERROR, CRITICAL
- **Sensitive data**: Masked (resource ARNs only, no credentials)

### Metrics
- **Counter**: `scan_findings_total{resource_type, risk_level}`
- **Gauge**: `active_remediations`, `pending_approvals`
- **Histogram**: `remediation_duration_seconds`
- **Labels**: `account_id`, `region`, `policy_rule`

### Tracing
- **Request flow**: Event → Policy → AI → Approval → Execute
- **Trace ID**: Propagated across all components via context
- **Span attributes**: Resource ARN, risk score, remediation status

---

## Security Boundaries

### IAM Model
- **Principle**: Least privilege, separate roles per component
- **Scanner**: `ReadOnlyAccess` + specific `Describe*` permissions
- **Executor**: Terraform backend assumes per-account deploy roles
- **No long-lived credentials**: All from IAM roles or LocalStack

### Approval Gating
- **HIGH risk**: Manual approval required (Telegram/Slack)
- **MEDIUM risk**: 5-minute auto-approval window with rollback
- **LOW risk**: Auto-execute with notification

---

## Event-Driven Architecture

### Current Implementation
- **LocalStack**: Simulated CloudTrail events via polling
- **Real AWS**: EventBridge → Lambda → SQS → Scanner (planned)

### Detection Modes
| Mode | Trigger | Latency | Use Case |
|------|---------|---------|----------|
| Batch | Scheduled (hourly) | High | Compliance scans |
| Real-time | EventBridge | Low | Abuse prevention |

---

## Idempotency & Safety

- **Terraform state**: Backend state file ensures idempotent applies
- **Dry-run first**: Always `terraform plan` before `terraform apply`
- **Rollback plan**: Each remediation includes reverse Terraform
- **Audit trail**: All actions logged with Terraform plan JSON

---

## Scale Considerations

### Current Limits
- **Accounts**: Single AWS account (LocalStack multi-account simulation)
- **Resources**: ~1000 resources per scan (limited by API rate limits)
- **LLM**: Single concurrent request (resource constrained)

### Planned Enhancements
- **AWS Organizations**: Multi-account support via assumed roles
- **Rate limiting**: Token bucket per service endpoint
- **LLM batching**: Async queue for remediation generation
- **Caching**: Reduce repeated policy evaluations

---

## Vector Database (PostgreSQL + pgvector)

### Why Vector Storage?
- **Similar findings**: Find past remediations for similar resource configurations
- **Context for LLM**: "Last time S3 bucket X was unencrypted, we did Y"

### Approach (Simplified)
```
Finding embedding = LLM embedding("S3 bucket production-data has no KMS encryption")
Similar = ORDER BY embedding <=> query_embedding LIMIT 5
```

- **Index**: IVFFlat for approximate nearest neighbor
- **Dimensions**: 768 (nomic-embed-text-v1.5)
- **Purpose**: Context retrieval, NOT enforcement decisions

---

## Tech Stack

| Component | Technology | Notes |
|-----------|------------|-------|
| Core | Python 3.12, LangGraph 0.4+ | State machine orchestration |
| Policy | Custom rules engine | Not OPA (yet) |
| AI | Local LLM (LM Studio) | qwen3.5-9b variant |
| Storage | PostgreSQL 17 + pgvector | Vector similarity search |
| Cloud | AWS (S3/IAM/EC2/RDS), LocalStack | Dev simulation |
| Notification | Telegram Bot, Slack-ready | aiogram async |
| Infrastructure | Docker Compose | Local development |

---

## Current Limitations

**This is beta software. Known gaps:**

- [ ] Multi-account AWS support (single account only)
- [ ] Real CloudTrail EventBridge integration (polling only)
- [ ] OPA policy engine (custom rules only)
- [ ] Prometheus metrics export (local logging only)
- [ ] Slack approval (Telegram only)
- [ ] No GitOps drift detection
- [ ] LLC resource constraints (single model, no queue)

---

## Getting Started

```bash
# 1. Setup
cp .env.example .env

# 2. Start
docker-compose up -d
uv pip install -e .

# 3. Run
uv run python kratos.py --dry-run    # Safe scan
uv run python agent/agent.py         # Autonomous mode
```

---

## Future Roadmap

- Multi-account AWS Organizations support
- EventBridge real-time detection
- OPA integration for policy-as-code
- Azure/GCP scanner modules

---

**KRATOS**: Evolving cloud governance platform. Not yet a Wiz competitor.