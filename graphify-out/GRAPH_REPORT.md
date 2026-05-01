# Graph Report - .  (2026-05-01)

## Corpus Check
- Corpus is ~10,715 words - fits in a single context window. You may not need a graph.

## Summary
- 108 nodes · 126 edges · 15 communities detected
- Extraction: 74% EXTRACTED · 26% INFERRED · 0% AMBIGUOUS · INFERRED: 33 edges (avg confidence: 0.65)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 6|Community 6]]
- [[_COMMUNITY_Community 7|Community 7]]
- [[_COMMUNITY_Community 8|Community 8]]
- [[_COMMUNITY_Community 13|Community 13]]
- [[_COMMUNITY_Community 14|Community 14]]
- [[_COMMUNITY_Community 15|Community 15]]
- [[_COMMUNITY_Community 16|Community 16]]
- [[_COMMUNITY_Community 17|Community 17]]
- [[_COMMUNITY_Community 18|Community 18]]

## God Nodes (most connected - your core abstractions)
1. `AnomalyEngine` - 12 edges
2. `BaselineTracker` - 11 edges
3. `RiskScorer` - 10 edges
4. `get_connection()` - 8 edges
5. `ChangeWatcher` - 7 edges
6. `MetricCollector` - 6 edges
7. `TerraformExecutor` - 6 edges
8. `CostEstimator` - 6 edges
9. `find_similar()` - 5 edges
10. `get_embedding()` - 4 edges

## Surprising Connections (you probably didn't know these)
- `MetricCollector` --uses--> `AnomalyEngine`  [INFERRED]
  ingestion/collector.py → anomaly/engine.py
- `Collects metrics from CloudWatch and feeds them to the Anomaly Engine.` --uses--> `AnomalyEngine`  [INFERRED]
  ingestion/collector.py → anomaly/engine.py
- `Collect CPU utilization for all EC2 instances.` --uses--> `AnomalyEngine`  [INFERRED]
  ingestion/collector.py → anomaly/engine.py
- `record_feedback()` --calls--> `get_connection()`  [INFERRED]
  anomaly/feedback.py → vault/policy_store.py
- `get_stats()` --calls--> `get_connection()`  [INFERRED]
  anomaly/feedback.py → vault/policy_store.py

## Communities

### Community 0 - "Community 0"
Cohesion: 0.16
Nodes (10): BaselineTracker, Fetch existing baseline or initialize a new one., Update baseline with new sample and return the Z-score (deviation)., Tracks and updates statistical baselines using Exponentially Weighted      Movin, CostEstimator, Estimates financial impact of cloud resources and anomalies., AnomalyEngine, Tier 1: Rule-based (deterministic) anomaly detection. (+2 more)

### Community 1 - "Community 1"
Cohesion: 0.14
Nodes (8): anomaly_detection_node(), Combine scores into a single 0-100 risk value., Determine the response level based on the composite score., Calculates composite risk scores based on multiple signals., RiskScorer, MetricCollector, Collect CPU utilization for all EC2 instances., Collects metrics from CloudWatch and feeds them to the Anomaly Engine.

### Community 2 - "Community 2"
Cohesion: 0.19
Nodes (11): reasoning_node(), AnomalyFeedback, get_stats(), Handles feedback from the approval system to tune detection thresholds., record_feedback(), test_embedding_returns_list(), find_similar(), get_connection() (+3 more)

### Community 3 - "Community 3"
Cohesion: 0.19
Nodes (7): ChangeWatcher, Get hash of current bucket state, Check if infrastructure changed, Start watching for changes, main(), Run scan and prepare for notification, scan_and_notify()

### Community 4 - "Community 4"
Cohesion: 0.31
Nodes (5): executor_node(), Write the AI-generated HCL to a file., Execute the remediation plan., Mock Terraform executor for LocalStack remediations., TerraformExecutor

### Community 5 - "Community 5"
Cohesion: 0.33
Nodes (4): KratosState, check_approval(), Route based on risk and approval status., TypedDict

### Community 6 - "Community 6"
Cohesion: 0.4
Nodes (2): Send notification with approval buttons, send_alert()

### Community 7 - "Community 7"
Cohesion: 0.5
Nodes (2): estimate_burn_rate(), get_hourly_rate()

### Community 8 - "Community 8"
Cohesion: 0.5
Nodes (3): cloud_scanner_node(), test_scanner_handles_no_buckets(), test_scanner_returns_findings()

### Community 13 - "Community 13"
Cohesion: 1.0
Nodes (1): Record user feedback (true_positive/false_positive) and update the event status.

### Community 14 - "Community 14"
Cohesion: 1.0
Nodes (1): Retrieve system performance stats.

### Community 15 - "Community 15"
Cohesion: 1.0
Nodes (1): Get the hourly rate for a given instance type.

### Community 16 - "Community 16"
Cohesion: 1.0
Nodes (1): Calculate total hourly cost for a set of resources.

### Community 17 - "Community 17"
Cohesion: 1.0
Nodes (1): Log-scale cost impact to a 0-100 score.

### Community 18 - "Community 18"
Cohesion: 1.0
Nodes (1): Project the cost if an anomaly continues for a given window.

## Knowledge Gaps
- **22 isolated node(s):** `Find similar past findings using vector similarity.`, `Send notification with approval buttons`, `Get hash of current bucket state`, `Check if infrastructure changed`, `Start watching for changes` (+17 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 6`** (5 nodes): `handle_approval()`, `notifier.py`, `Send notification with approval buttons`, `run_bot()`, `send_alert()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 7`** (5 nodes): `calculate_cost_score()`, `estimate_burn_rate()`, `get_hourly_rate()`, `get_projected_waste()`, `cost.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 13`** (1 nodes): `Record user feedback (true_positive/false_positive) and update the event status.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 14`** (1 nodes): `Retrieve system performance stats.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 15`** (1 nodes): `Get the hourly rate for a given instance type.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 16`** (1 nodes): `Calculate total hourly cost for a set of resources.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 17`** (1 nodes): `Log-scale cost impact to a 0-100 score.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 18`** (1 nodes): `Project the cost if an anomaly continues for a given window.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `AnomalyEngine` connect `Community 0` to `Community 1`?**
  _High betweenness centrality (0.153) - this node is a cross-community bridge._
- **Why does `get_connection()` connect `Community 2` to `Community 0`?**
  _High betweenness centrality (0.112) - this node is a cross-community bridge._
- **Are the 7 inferred relationships involving `AnomalyEngine` (e.g. with `MetricCollector` and `Collects metrics from CloudWatch and feeds them to the Anomaly Engine.`) actually correct?**
  _`AnomalyEngine` has 7 INFERRED edges - model-reasoned connections that need verification._
- **Are the 5 inferred relationships involving `BaselineTracker` (e.g. with `AnomalyEngine` and `Orchestrates multiple tiers of anomaly detection.`) actually correct?**
  _`BaselineTracker` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Are the 5 inferred relationships involving `RiskScorer` (e.g. with `MetricCollector` and `Collects metrics from CloudWatch and feeds them to the Anomaly Engine.`) actually correct?**
  _`RiskScorer` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Are the 5 inferred relationships involving `get_connection()` (e.g. with `.get_or_create_baseline()` and `.update_baseline()`) actually correct?**
  _`get_connection()` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `ChangeWatcher` (e.g. with `Run scan and prepare for notification` and `main()`) actually correct?**
  _`ChangeWatcher` has 2 INFERRED edges - model-reasoned connections that need verification._