# KRATOS Anomaly Detection Architecture

# Future Architecture — Anomaly Detection

This document outlines the **target-state architecture** for anomaly detection in KRATOS.

⚠️ This is NOT fully implemented.

Current focus:
- Build minimal MVP for cost anomaly detection
- Validate real-world usefulness before scaling architecture

Scope of this doc:
- Long-term design (T1 + T2 + T3 anomaly detection)
- Multi-account scaling
- Event-driven ingestion

## Overview

Extend KRATOS with a hybrid anomaly detection engine that detects behavioral anomalies in cloud infrastructure — cost spikes, IAM abuse, resource anomalies — while preserving the core principle: **AI reasons, deterministic rules enforce.**

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        KRATOS PLATFORM (Extended)                       │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌───────────┐   ┌──────────┐   ┌──────────┐   ┌───────────────┐       │
│  │  Event    │──▶│ Scanner  │──▶│ Policy   │──▶│ Anomaly       │       │
│  │  Sources  │   │          │   │ Engine   │   │ Engine (NEW)  │       │
│  └───────────┘   └──────────┘   └──────────┘   └───────┬───────┘       │
│   CloudTrail                                            │               │
│   CloudWatch      ┌──────────────┐                      ▼               │
│   Billing API     │ Baseline     │              ┌───────────────┐       │
│   IAM Logs        │ Store        │◀────────────▶│ Risk Scorer   │       │
│                   │ (TimescaleDB)│              │ (Composite)   │       │
│                   └──────────────┘              └───────┬───────┘       │
│                                                         │               │
│                   ┌──────────────┐              ┌───────▼───────┐       │
│                   │ Feedback     │◀─────────────│ AI Brain      │       │
│                   │ Loop Store   │              │ (Remediation) │       │
│                   └──────────────┘              └───────┬───────┘       │
│                                                         │               │
│                                                 ┌───────▼───────┐       │
│                                                 │ Approval Gate │       │
│                                                 │ → Executor    │       │
│                                                 └───────────────┘       │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 1. Detection Strategy — Hybrid Three-Tier

| Tier | Method | When to Use | Trade-off |
|------|--------|-------------|-----------|
| **T1: Rule-Based** | Deterministic thresholds | Known-bad patterns (e.g. GPU launch at 2AM) | Fast, zero false positives for known patterns; misses novel threats |
| **T2: Statistical** | EWMA + percentile deviation | Baseline drift detection (cost, usage) | Catches gradual anomalies; needs 2+ weeks of data to be useful |
| **T3: ML-Based** | Isolation Forest (optional) | Multi-dimensional anomalies | Best for complex patterns; harder to debug, needs more data |

### Decision Flow

```
Event arrives
  ├─ T1: Does it match a deterministic rule? → ALERT (immediate)
  ├─ T2: Does it deviate from statistical baseline? → SCORE + threshold check
  └─ T3: (Optional) Does ML model flag it? → SCORE with lower weight
```

> [!IMPORTANT]
> Start with T1 + T2 only. Add T3 after 3+ months of baseline data.

---

## 2. Data Sources & Ingestion

### Sources

| Source | Signals | Ingestion Method |
|--------|---------|-----------------|
| CloudTrail | API calls, IAM activity, resource CRUD | EventBridge → SQS → Worker |
| CloudWatch | CPU, network, disk, GPU utilization | Polling (5-min) or CloudWatch Metric Streams → Kinesis |
| Cost Explorer / CUR | Hourly/daily cost by service | Scheduled pull (hourly) |
| IAM Access Analyzer | Unused permissions, external access | Scheduled pull (6-hourly) |
| VPC Flow Logs | Network anomalies, public exposure | S3 → SQS notification → Worker |

### Ingestion Architecture

```
                    Real-Time Path                    Batch Path
                    ─────────────                    ──────────
EventBridge ──▶ SQS ──▶ ┌────────────┐     Scheduler ──▶ ┌────────────┐
                        │ RT Worker  │                    │ Batch      │
CloudWatch  ──▶ Kinesis ▶│ (async)    │     (cron)   ──▶ │ Collector  │
Streams                 └─────┬──────┘                    └─────┬──────┘
                              │                                  │
                              ▼                                  ▼
                        ┌─────────────────────────────────────────┐
                        │         Metric Ingestion Buffer         │
                        │         (PostgreSQL / TimescaleDB)      │
                        └─────────────────────────────────────────┘
```

---

## 3. Baseline Modeling — Practical Approach

### Method: EWMA + Percentile Bands

For each metric (CPU, cost, API call count, etc.), maintain:

```python
# Exponentially Weighted Moving Average
ewma_t = α * x_t + (1 - α) * ewma_(t-1)
# where α = 0.1 (slow adaptation) to 0.3 (fast adaptation)

# Standard deviation (exponentially weighted)
ewma_var_t = α * (x_t - ewma_t)² + (1 - α) * ewma_var_(t-1)
ewma_std_t = sqrt(ewma_var_t)
```

**Anomaly if:** `|x_t - ewma_t| > k * ewma_std_t` where k = 2.5 (tunable)

### Baseline Dimensions

| Dimension | Granularity | Example |
|-----------|-------------|---------|
| Time-of-day | Hourly buckets (0-23) | "CPU is normally 40% at 3PM" |
| Day-of-week | Weekday vs weekend | "No GPU usage on weekends" |
| Per-service | S3, EC2, IAM, RDS | "IAM calls spike during deploy windows" |
| Per-account | Account-level patterns | "Dev account never runs p4d instances" |

### Bootstrap Period

- **Minimum:** 14 days of data before alerting
- **During bootstrap:** Only T1 (rule-based) detection active
- **Storage:** Rolling 90-day window of aggregated metrics (not raw)

### Practical Implementation

```python
class BaselineTracker:
    def __init__(self, metric_key: str, alpha: float = 0.15):
        self.metric_key = metric_key
        self.alpha = alpha
        self.ewma = None
        self.ewma_var = 0.0
        self.hourly_baselines = {}  # {hour: {ewma, var, count}}

    def update(self, value: float, hour: int):
        bucket = self.hourly_baselines.setdefault(hour, {"ewma": value, "var": 0.0, "count": 0})
        bucket["count"] += 1
        if bucket["count"] < 50:  # Bootstrap: just accumulate
            bucket["ewma"] = (bucket["ewma"] * (bucket["count"]-1) + value) / bucket["count"]
            return None  # No score during bootstrap
        old_ewma = bucket["ewma"]
        bucket["ewma"] = self.alpha * value + (1 - self.alpha) * old_ewma
        bucket["var"] = self.alpha * (value - old_ewma)**2 + (1 - self.alpha) * bucket["var"]
        std = bucket["var"] ** 0.5
        if std == 0:
            return 0.0
        return abs(value - bucket["ewma"]) / std  # Z-score
```

---

## 4. Anomaly Scoring — Composite Risk Score

```
Composite Risk = W1 * Policy_Score + W2 * Anomaly_Score + W3 * Cost_Impact
```

| Component | Range | Weight | Source |
|-----------|-------|--------|--------|
| Policy_Score | 0-100 | W1=0.4 | Existing Policy Engine (rule match severity) |
| Anomaly_Score | 0-100 | W2=0.35 | Statistical deviation (z-score normalized) |
| Cost_Impact | 0-100 | W3=0.25 | Estimated $/hr impact, log-scaled |

### Normalization

```python
def normalize_anomaly(z_score: float) -> float:
    """Convert z-score to 0-100 scale."""
    return min(100, max(0, (z_score / 5.0) * 100))

def normalize_cost(hourly_cost: float) -> float:
    """Log-scale cost impact to 0-100."""
    import math
    if hourly_cost <= 0: return 0
    return min(100, math.log10(hourly_cost + 1) * 33)  # $1000/hr → ~100

def composite_risk(policy: float, anomaly_z: float, cost_hr: float) -> float:
    return (0.40 * policy +
            0.35 * normalize_anomaly(anomaly_z) +
            0.25 * normalize_cost(cost_hr))
```

### Action Thresholds

| Composite Score | Action |
|----------------|--------|
| 0–30 | Log only |
| 30–60 | Alert (Telegram/Slack notification) |
| 60–80 | Alert + AI Brain generates remediation |
| 80–100 | Alert + AI Brain + Urgent approval request |

---

## 5. Integration with Existing Pipeline

### Extended Flow

```
Event
  │
  ▼
Scanner (existing) ──────────────────────────────┐
  │                                               │
  ▼                                               ▼
Policy Engine (existing)               Anomaly Engine (NEW)
  │ outputs: policy_score,               │ outputs: anomaly_score,
  │ risk_level, violations                │ anomaly_type, z_score
  │                                       │
  └──────────────┬────────────────────────┘
                 │
                 ▼
          Risk Scorer (NEW)
          combines policy + anomaly + cost
                 │
                 ▼
          AI Brain (existing, enhanced)
          receives anomaly context
                 │
                 ▼
          Approval → Executor (existing)
```

### Key Design Decision: Anomaly Engine runs IN PARALLEL with Policy Engine

> [!IMPORTANT]
> The Anomaly Engine does NOT replace or gate the Policy Engine. They run independently and their scores are merged by the Risk Scorer.

**Conflict resolution:**
- If Policy says HIGH but Anomaly says normal → **Policy wins** (enforce the rule)
- If Anomaly says HIGH but Policy says nothing → **Alert only** (no auto-enforcement on anomaly alone)
- If both say HIGH → **Highest urgency** (composite score boosted)

### State Extension

```python
class KratosState(TypedDict):
    findings: Annotated[List[str], operator.add]
    remediation_plan: str
    status: str
    # NEW fields
    anomaly_findings: Annotated[List[dict], operator.add]
    composite_risk_score: float
    anomaly_context: str  # Injected into AI Brain prompt
```

### LangGraph Extension

```python
workflow = StateGraph(KratosState)
workflow.add_node("scanner", cloud_scanner_node)
workflow.add_node("policy_engine", policy_engine_node)    # extracted from scanner
workflow.add_node("anomaly_engine", anomaly_engine_node)  # NEW
workflow.add_node("risk_scorer", risk_scorer_node)        # NEW
workflow.add_node("brain", reasoning_node)

workflow.set_entry_point("scanner")
workflow.add_edge("scanner", "policy_engine")
workflow.add_edge("scanner", "anomaly_engine")            # parallel
workflow.add_edge("policy_engine", "risk_scorer")
workflow.add_edge("anomaly_engine", "risk_scorer")
workflow.add_edge("risk_scorer", "brain")
workflow.add_edge("brain", END)
```

---

## 6. Real-Time vs Batch Modes

| Aspect | Real-Time | Batch |
|--------|-----------|-------|
| **Trigger** | EventBridge → SQS | Scheduled (cron) |
| **Latency** | < 60 seconds | Hourly / daily |
| **Use Cases** | IAM privilege escalation, GPU launch, public exposure | Cost trend analysis, usage pattern drift, compliance reports |
| **Detection Tiers** | T1 (rules) + T2 (EWMA check) | T2 (full statistical) + T3 (ML optional) |
| **Data** | Single event | Aggregated metrics window |

### Real-Time Path

```
EventBridge Rule (ec2:RunInstances, iam:AttachRolePolicy, etc.)
  → SQS Queue (anomaly-rt-queue)
    → RT Worker:
       1. Classify event type
       2. Check T1 rules (instant)
       3. Query latest baseline, compute EWMA deviation
       4. If score > threshold → inject into KRATOS pipeline
```

### Batch Path

```
Cron (every hour):
  1. Pull CloudWatch metrics (last hour, 5-min granularity)
  2. Pull Cost Explorer data (last hour)
  3. For each metric:
     a. Update baseline (EWMA)
     b. Compute deviation scores
     c. If any score > threshold → create anomaly finding
  4. Aggregate findings → inject into KRATOS pipeline
```

---

## 7. Cost Anomaly Detection

### GPU Misuse Detection (T1 Rule)

```python
GPU_INSTANCE_PATTERN = r"^(p[2-5]|g[4-6]|inf[1-2]|trn[1-2]|dl[1-2])\."

COST_RULES = [
    {
        "name": "gpu_outside_hours",
        "condition": lambda e: (
            re.match(GPU_INSTANCE_PATTERN, e.get("instance_type", ""))
            and e["hour"] not in range(8, 20)  # outside 8AM-8PM
        ),
        "risk": 90,
        "message": "GPU instance launched outside business hours"
    },
    {
        "name": "gpu_weekend",
        "condition": lambda e: (
            re.match(GPU_INSTANCE_PATTERN, e.get("instance_type", ""))
            and e["day_of_week"] in (5, 6)  # Saturday, Sunday
        ),
        "risk": 95,
    },
    {
        "name": "excessive_scale_up",
        "condition": lambda e: e.get("instance_count", 1) > 10,
        "risk": 80,
    }
]
```

### Near Real-Time Cost Estimation

```python
# Pricing lookup table (cached, updated daily from AWS Price List API)
HOURLY_COST = {
    "p4d.24xlarge": 32.77,
    "p3.16xlarge": 24.48,
    "g5.48xlarge": 16.29,
    "t3.medium": 0.0416,
    # ...loaded from pricing API
}

def estimate_burn_rate(running_instances: list[dict]) -> float:
    """Estimate current hourly burn rate."""
    return sum(HOURLY_COST.get(i["type"], 0) * i["count"] for i in running_instances)

def project_cost(burn_rate: float, hours: int = 24) -> float:
    """Project cost if unchecked."""
    return burn_rate * hours
```

### Idle Resource Detection (Batch)

```python
def detect_idle_expensive(cloudwatch_client, instance_id, instance_type):
    """Flag expensive instances with <5% CPU for 2+ hours."""
    metrics = cloudwatch_client.get_metric_statistics(
        Namespace='AWS/EC2',
        MetricName='CPUUtilization',
        Dimensions=[{'Name': 'InstanceId', 'Value': instance_id}],
        StartTime=datetime.utcnow() - timedelta(hours=2),
        EndTime=datetime.utcnow(),
        Period=300,  # 5 min
        Statistics=['Average']
    )
    avg_cpu = mean([dp['Average'] for dp in metrics['Datapoints']]) if metrics['Datapoints'] else None
    hourly_cost = HOURLY_COST.get(instance_type, 0)

    if avg_cpu is not None and avg_cpu < 5.0 and hourly_cost > 1.0:
        return {
            "type": "idle_expensive_resource",
            "instance_id": instance_id,
            "avg_cpu": avg_cpu,
            "hourly_cost": hourly_cost,
            "projected_waste_24h": hourly_cost * 24,
            "risk": 75
        }
    return None
```

---

## 8. Safety & False Positive Reduction

### Strategy: Progressive Trust

| Phase | Duration | Behavior |
|-------|----------|----------|
| **Shadow Mode** | Weeks 1-4 | Detect + log, NO alerts. Build baselines. |
| **Advisory Mode** | Weeks 5-8 | Alert only, NO auto-remediation. Collect feedback. |
| **Active Mode** | Week 9+ | Full integration with KRATOS pipeline. |

### Threshold Tuning

```python
class AdaptiveThreshold:
    def __init__(self, initial_k=3.0, min_k=2.0, max_k=5.0):
        self.k = initial_k
        self.false_positive_count = 0
        self.true_positive_count = 0

    def record_feedback(self, was_true_positive: bool):
        if was_true_positive:
            self.true_positive_count += 1
        else:
            self.false_positive_count += 1
        # Adjust: too many FPs → raise threshold
        total = self.false_positive_count + self.true_positive_count
        if total >= 20:
            fp_rate = self.false_positive_count / total
            if fp_rate > 0.3:  # >30% false positive rate
                self.k = min(self.k + 0.25, 5.0)
            elif fp_rate < 0.1:  # <10% FP rate, can be more sensitive
                self.k = max(self.k - 0.1, 2.0)
            self.false_positive_count = 0
            self.true_positive_count = 0
```

### Feedback Loop from Approvals

```
Approval Approved  → record_feedback(true_positive=True)
Approval Rejected  → record_feedback(true_positive=False)
Approval Ignored   → record_feedback(true_positive=False) after 48h
```

### Noise Reduction Techniques

1. **Cooldown window:** Same anomaly type + resource → suppress for 1 hour
2. **Minimum severity:** Only alert if composite score > 30
3. **Correlation:** Group related anomalies (e.g., CPU spike + cost spike on same instance = 1 alert)
4. **Business calendar:** Suppress known maintenance windows

---

## 9. Storage & State

### Schema (TimescaleDB extension on existing PostgreSQL)

```sql
-- Enable TimescaleDB (extension on existing PostgreSQL)
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Raw metrics (time-series, auto-partitioned)
CREATE TABLE metric_samples (
    time        TIMESTAMPTZ NOT NULL,
    account_id  TEXT NOT NULL,
    region      TEXT NOT NULL,
    metric_name TEXT NOT NULL,
    resource_id TEXT,
    value       DOUBLE PRECISION NOT NULL
);
SELECT create_hypertable('metric_samples', 'time');

-- Baselines (updated by batch job)
CREATE TABLE baselines (
    metric_key  TEXT NOT NULL,     -- "account:region:metric:resource"
    hour_bucket SMALLINT NOT NULL, -- 0-23
    day_type    TEXT NOT NULL,     -- 'weekday' or 'weekend'
    ewma        DOUBLE PRECISION,
    ewma_var    DOUBLE PRECISION,
    sample_count INTEGER DEFAULT 0,
    updated_at  TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (metric_key, hour_bucket, day_type)
);

-- Anomaly history
CREATE TABLE anomaly_events (
    id              SERIAL PRIMARY KEY,
    detected_at     TIMESTAMPTZ DEFAULT NOW(),
    anomaly_type    TEXT NOT NULL,
    resource_id     TEXT,
    account_id      TEXT,
    metric_name     TEXT,
    observed_value  DOUBLE PRECISION,
    expected_value  DOUBLE PRECISION,
    z_score         DOUBLE PRECISION,
    composite_score DOUBLE PRECISION,
    tier            TEXT,             -- 'T1', 'T2', 'T3'
    action_taken    TEXT,             -- 'logged', 'alerted', 'remediated'
    feedback        TEXT              -- 'true_positive', 'false_positive', NULL
);

-- Feedback signals
CREATE TABLE anomaly_feedback (
    anomaly_id  INTEGER REFERENCES anomaly_events(id),
    feedback    TEXT NOT NULL,  -- 'confirmed', 'dismissed', 'ignored'
    source      TEXT NOT NULL,  -- 'approval_system', 'manual', 'auto_timeout'
    created_at  TIMESTAMPTZ DEFAULT NOW()
);
```

### Retention Policy

| Data | Retention | Storage |
|------|-----------|---------|
| Raw metric samples | 30 days | TimescaleDB (compressed) |
| Baselines | Indefinite (updated in-place) | PostgreSQL |
| Anomaly events | 1 year | PostgreSQL |
| Feedback | 1 year | PostgreSQL |

> [!TIP]
> TimescaleDB is an extension on PostgreSQL — no new database needed. Reuse the existing `postgres-kratos` container with the extension added.

---

## 10. Scalability

### Multi-Account Architecture

```
AWS Organization
  ├── Account A ──▶ EventBridge ──▶ Central Event Bus ──▶ SQS
  ├── Account B ──▶ EventBridge ──▶ Central Event Bus ──▶ SQS
  └── Account C ──▶ EventBridge ──▶ Central Event Bus ──▶ SQS
                                                          │
                                          ┌───────────────┘
                                          ▼
                                   ┌──────────────┐
                                   │ Worker Pool  │
                                   │ (async, N=4) │
                                   └──────────────┘
```

### Queue Design

```python
# Using asyncio + SQS (or Redis Streams for LocalStack dev)
QUEUES = {
    "anomaly-rt":    {"workers": 2, "visibility_timeout": 60},
    "anomaly-batch": {"workers": 1, "visibility_timeout": 300},
    "anomaly-cost":  {"workers": 1, "visibility_timeout": 120},
}
```

### Rate Limiting

```python
import asyncio
from collections import defaultdict

class TokenBucketRateLimiter:
    def __init__(self, rate: float, capacity: int):
        self.rate = rate          # tokens per second
        self.capacity = capacity
        self.tokens = capacity
        self.last_refill = asyncio.get_event_loop().time()

    async def acquire(self):
        while self.tokens < 1:
            await asyncio.sleep(0.1)
            now = asyncio.get_event_loop().time()
            self.tokens = min(self.capacity,
                            self.tokens + self.rate * (now - self.last_refill))
            self.last_refill = now
        self.tokens -= 1

# Per-service rate limiters
rate_limiters = {
    "cloudwatch": TokenBucketRateLimiter(rate=5, capacity=20),
    "cost_explorer": TokenBucketRateLimiter(rate=1, capacity=5),
    "iam": TokenBucketRateLimiter(rate=3, capacity=10),
}
```

---

## 11. Observability — Monitoring the Anomaly System

### Key Metrics

```python
ANOMALY_METRICS = {
    # Detection health
    "anomaly_detections_total":     Counter(labels=["tier", "type", "account"]),
    "anomaly_false_positive_total": Counter(labels=["tier", "type"]),
    "anomaly_detection_latency_ms": Histogram(labels=["tier"]),

    # Baseline health
    "baseline_staleness_seconds":   Gauge(labels=["metric_key"]),
    "baseline_sample_count":        Gauge(labels=["metric_key"]),

    # Queue health
    "queue_depth":                  Gauge(labels=["queue_name"]),
    "queue_processing_time_ms":     Histogram(labels=["queue_name"]),

    # System health
    "ingestion_errors_total":       Counter(labels=["source"]),
    "api_rate_limit_hits_total":    Counter(labels=["service"]),
}
```

### Dashboard Queries (SQL)

```sql
-- False positive rate (last 7 days)
SELECT
    tier,
    COUNT(*) FILTER (WHERE feedback = 'false_positive') * 100.0 / NULLIF(COUNT(*), 0) as fp_rate
FROM anomaly_events
WHERE detected_at > NOW() - INTERVAL '7 days' AND feedback IS NOT NULL
GROUP BY tier;

-- Detection latency P95
SELECT percentile_cont(0.95) WITHIN GROUP (ORDER BY detection_latency_ms)
FROM anomaly_events
WHERE detected_at > NOW() - INTERVAL '1 day';
```

### Alerting on Anomaly System Itself

| Condition | Alert |
|-----------|-------|
| FP rate > 40% for any tier | Tune thresholds |
| No detections in 24h | Ingestion may be broken |
| Queue depth > 1000 | Worker scaling needed |
| Baseline staleness > 48h | Batch job failing |

---

## 12. Component Breakdown & Implementation Plan

### New Files

```
kratos-ai/
├── anomaly/
│   ├── __init__.py
│   ├── engine.py          # AnomalyEngine: orchestrates T1/T2/T3
│   ├── rules.py           # T1: deterministic anomaly rules
│   ├── baseline.py        # T2: EWMA baseline tracker
│   ├── scorer.py          # Composite risk scorer
│   ├── cost.py            # Cost anomaly detection + pricing
│   └── feedback.py        # Feedback loop + threshold adaptation
├── ingestion/
│   ├── __init__.py
│   ├── cloudwatch.py      # CloudWatch metric collector
│   ├── cloudtrail.py      # CloudTrail event processor
│   ├── cost_explorer.py   # Cost data collector
│   └── worker.py          # Async SQS/queue worker
├── scripts/
│   └── init-timescale.sql # TimescaleDB schema migration
└── docker-compose.yml     # Updated: add timescaledb extension
```

### Modified Files

| File | Change |
|------|--------|
| `agents/state.py` | Add anomaly fields to `KratosState` |
| `app.py` | Add anomaly_engine + risk_scorer nodes, parallel edges |
| `agents/brain.py` | Accept anomaly context in prompt |
| `docker-compose.yml` | Switch to TimescaleDB image |
| `scripts/init-db.sql` | Add anomaly tables |

### Implementation Phases

| Phase | Duration | Deliverables |
|-------|----------|-------------|
| **Phase 1** | 2 weeks | T1 rules engine, cost detection, schema, ingestion skeleton |
| **Phase 2** | 2 weeks | T2 EWMA baselines, composite scorer, shadow mode |
| **Phase 3** | 2 weeks | Integration with LangGraph pipeline, feedback loop |
| **Phase 4** | 2 weeks | Multi-account, queue workers, observability dashboard |

---

## Open Questions

> [!IMPORTANT]
> 1. **TimescaleDB vs plain PostgreSQL?** TimescaleDB adds time-series compression and retention policies but requires the extension. Alternatively, we can use plain PostgreSQL with manual partitioning — simpler but less efficient at scale.

> [!IMPORTANT]
> 2. **Shadow mode duration?** Proposed 4 weeks before enabling alerts. Is this acceptable, or do you want a faster path to production?

> [!WARNING]
> 3. **Cost data source in LocalStack?** Cost Explorer and Billing APIs aren't available in LocalStack. For dev, we'd need mock cost data. Is that acceptable?

> [!IMPORTANT]
> 4. **Queue technology?** For dev/LocalStack: Redis Streams or in-process asyncio queues. For production: SQS or Kafka. Preference?
