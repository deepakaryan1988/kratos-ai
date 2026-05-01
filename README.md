# KRATOS: AI Cloud Security & Governance Platform

KRATOS is an intelligent cloud security platform that combines deterministic policy enforcement with AI-driven anomaly detection and architectural remediation.

## 🌟 Key Features

- **Hybrid Anomaly Detection**: Real-time monitoring using deterministic rules (T1) and statistical baselines (T2).
- **AI Brain (LLM)**: Autonomous reasoning for complex security incidents and Terraform remediation generation.
- **Human-in-the-Loop**: Integrated approval gates for high-risk architectural changes.
- **Time-Series Analysis**: Built-in TimescaleDB support for metric baselines and cost projection.
- **Event-Driven Execution**: Parallel processing of security scans and behavioral signals.

## 🛡️ Anomaly Detection & AI Governance

KRATOS now features a production-grade, hybrid anomaly detection system that works alongside the deterministic policy engine.

### 🏗️ Architecture
The system follows a multi-tier detection strategy as outlined in the [Anomaly Architecture Documentation](docs/future-anomaly-architecture.md):
- **Tier 1 (Deterministic Rules)**: Flags known high-risk patterns (GPU launch hours, mass scale-ups).
- **Tier 2 (Statistical EWMA)**: Learns behavioral baselines and flags Z-score deviations in CPU/GPU/Cost.
- **Tier 3 (AI Governance)**: Uses a local LLM to reason about anomalies and generate forensic isolation plans.

### 🚥 Human-in-the-Loop Workflow
For high-risk findings (Composite Score > 50), KRATOS pauses for manual approval:
1. **Detect**: Parallel scan of policies and behavioral metrics.
2. **Reason**: AI generates an architectural remediation plan.
3. **Gate**: System pauses if risk is critical.
4. **Execute**: Terraform applies the isolation/fix once approved.

## 🚀 Running KRATOS

### Initializing the Environment
Ensure LocalStack and PostgreSQL (with TimescaleDB) are running:
```bash
docker-compose up -d
```

### Seeding Chaos (Testing)
Populate the environment with multiple anomaly scenarios:
```bash
uv run python scripts/seed_anomaly.py
```

### Running the Engine
**Dry Run (View Findings & Risk):**
```bash
uv run python kratos.py --dry-run
```

**Full Run (With AI Reasoning & Approval Gate):**
```bash
uv run python kratos.py
```

**Approve & Execute (Apply Architectural Fixes):**
```bash
uv run python kratos.py --approve
```

---

## 📜 Documentation Reference
- [Full Architecture Design](docs/future-anomaly-architecture.md)
- [Project Status & Roadmap](docs/project_status.md)
- [S3 Security Policies](vault/s3_policies.py)

**KRATOS**: Evolved with behavioral intelligence.