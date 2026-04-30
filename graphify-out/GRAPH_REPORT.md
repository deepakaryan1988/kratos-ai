# Graph Report - .  (2026-04-30)

## Corpus Check
- Corpus is ~690 words - fits in a single context window. You may not need a graph.

## Summary
- 24 nodes · 19 edges · 6 communities detected
- Extraction: 47% EXTRACTED · 53% INFERRED · 0% AMBIGUOUS · INFERRED: 10 edges (avg confidence: 0.83)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Scanner Workflow|Scanner Workflow]]
- [[_COMMUNITY_Brain Reasoning|Brain Reasoning]]
- [[_COMMUNITY_State Module|State Module]]
- [[_COMMUNITY_Kratos Engine|Kratos Engine]]
- [[_COMMUNITY_Claude Model|Claude Model]]
- [[_COMMUNITY_PostgreSQL|PostgreSQL]]

## God Nodes (most connected - your core abstractions)
1. `Reasoning Node` - 6 edges
2. `StateGraph Workflow` - 5 edges
3. `Cloud Scanner Node` - 5 edges
4. `KratosState` - 3 edges
5. `KratosState` - 2 edges
6. `Kratos Engine` - 2 edges
7. `Project Kratos` - 1 edges
8. `LangGraph` - 1 edges
9. `LocalStack` - 1 edges
10. `Qwen 9B` - 1 edges

## Surprising Connections (you probably didn't know these)
- `StateGraph Workflow` --implements--> `LangGraph`  [INFERRED]
  main.py → docs/PRD.md
- `Cloud Scanner Node` --implements--> `Sensory Node (Scanner)`  [INFERRED]
  agents/scanner.py → docs/PRD.md
- `Cloud Scanner Node` --references--> `LocalStack`  [INFERRED]
  agents/scanner.py → docs/PRD.md
- `Reasoning Node` --implements--> `Cognitive Node (Brain)`  [INFERRED]
  agents/brain.py → docs/PRD.md
- `Reasoning Node` --references--> `Qwen 9B`  [INFERRED]
  agents/brain.py → docs/PRD.md

## Hyperedges (group relationships)
- **Kratos Workflow Nodes** — main_workflow, scanner_cloud_scanner_node, brain_reasoning_node [EXTRACTED 0.90]

## Communities

### Community 0 - "Scanner Workflow"
Cohesion: 0.4
Nodes (6): StateGraph Workflow, LangGraph, LocalStack, Sensory Node (Scanner), Cloud Scanner Node, KratosState

### Community 1 - "Brain Reasoning"
Cohesion: 0.5
Nodes (4): Reasoning Node, Cognitive Node (Brain), Qwen 9B, Remediation Node

### Community 2 - "State Module"
Cohesion: 0.67
Nodes (2): KratosState, TypedDict

### Community 6 - "Kratos Engine"
Cohesion: 1.0
Nodes (2): Kratos Engine, Project Kratos

### Community 8 - "Claude Model"
Cohesion: 1.0
Nodes (1): Claude 3.5 Sonnet

### Community 9 - "PostgreSQL"
Cohesion: 1.0
Nodes (1): PostgreSQL

## Knowledge Gaps
- **9 isolated node(s):** `Project Kratos`, `LangGraph`, `LocalStack`, `Qwen 9B`, `Claude 3.5 Sonnet` (+4 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `State Module`** (3 nodes): `KratosState`, `state.py`, `TypedDict`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Kratos Engine`** (2 nodes): `Kratos Engine`, `Project Kratos`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Claude Model`** (1 nodes): `Claude 3.5 Sonnet`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `PostgreSQL`** (1 nodes): `PostgreSQL`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Reasoning Node` connect `Brain Reasoning` to `Scanner Workflow`?**
  _High betweenness centrality (0.107) - this node is a cross-community bridge._
- **Why does `StateGraph Workflow` connect `Scanner Workflow` to `Brain Reasoning`, `Kratos Engine`?**
  _High betweenness centrality (0.103) - this node is a cross-community bridge._
- **Why does `Cloud Scanner Node` connect `Scanner Workflow` to `Brain Reasoning`?**
  _High betweenness centrality (0.075) - this node is a cross-community bridge._
- **Are the 4 inferred relationships involving `Reasoning Node` (e.g. with `Cognitive Node (Brain)` and `Qwen 9B`) actually correct?**
  _`Reasoning Node` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `StateGraph Workflow` (e.g. with `LangGraph` and `KratosState`) actually correct?**
  _`StateGraph Workflow` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `Cloud Scanner Node` (e.g. with `Sensory Node (Scanner)` and `LocalStack`) actually correct?**
  _`Cloud Scanner Node` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `KratosState` (e.g. with `StateGraph Workflow` and `Cloud Scanner Node`) actually correct?**
  _`KratosState` has 3 INFERRED edges - model-reasoned connections that need verification._