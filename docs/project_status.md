# KRATOS Project Status: May 2026

## 🟢 Current State (Completed)

### 1. Hybrid Anomaly Engine
- [x] **Tier 1 Rules**: GPU abuse, IAM backdoor creation, Mass scale-up.
- [x] **Tier 2 Statistics**: EWMA baseline tracker for CPU/Cost metrics.
- [x] **Composite Scoring**: Balanced risk calculation (40% Policy, 35% Anomaly, 25% Cost).

### 2. AI Governance (The Brain)
- [x] **Context-Aware Remediation**: LLM distinguishes between configuration fixes and forensic isolation.
- [x] **Terraform Generation**: Automated HCL generation for stop/isolate/encrypt actions.
- [x] **Memory (RAG)**: Integration with pgvector for historical policy retrieval.

### 3. Execution Pipeline
- [x] **Approval Gate**: LangGraph-based workflow that pauses for critical risks.
- [x] **Terraform Executor**: Prepares and executes remediation HCL in a sandbox.

### 4. Database Infrastructure
- [x] **TimescaleDB Integration**: Optimized for time-series metric storage.
- [x] **Feedback Loop**: Tables ready to store approval/rejection data for auto-tuning.

---

## 🟡 What's Left (Roadmap to Production)

### Phase 1: Real-Time & Notifications
- [ ] **EventBridge Integration**: Move from polling/scanning to real-time CloudTrail event triggers.
- [ ] **Telegram/Slack Module**: Connect the `notifier.py` to a real messaging bot for mobile approvals.

### Phase 2: Intelligence & Scaling
- [ ] **Auto-Threshold Tuning**: Implement the background job to adjust Z-score sensitivity based on human feedback.
- [ ] **Multi-Account Manager**: Implement Cross-Account IAM role assumption logic.
- [ ] **Cost Forecasting**: Integrate with AWS Budgets API for financial context.

### Phase 3: Observability
- [ ] **Admin Dashboard**: A simple UI to visualize cost anomalies and baseline trends.
- [ ] **Audit Trail**: Full logging of every AI decision and subsequent Terraform execution.
