# Autonomous Security Agent Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development

**Goal:** Build self-healing security agent that watches cloud infra, detects drift, analyzes impacts, and proposes fixes with human approval

**Architecture:** Change watcher → Impact analyzer → Action planner → Approval workflow → Auto-remediation

**Tech Stack:** Python asyncio, Polling agents, WhatsApp/Telegram bots (aiogram), LangGraph

---

## Architecture Flow

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐     ┌────────────┐
│ Change      │────▶│ Impact       │────▶│ Propose     │────▶│ Human      │
│ Watcher     │     │ Analyzer     │     │ Fix (Terra- │     │ Approval   │
│ (S3/EC2/    │     │ (Brain)      │     │ form)       │     │ (WhatsApp/ │
│ RDS polls)  │     │              │     │             │     │ Telegram)  │
└─────────────┘     └──────────────┘     └─────────────┘     └────────────┘
                            ▲                                          │
                            │                                          │
                            └────────────────┬─────────────────────────┘
                                             │
                                    Approved fix runs
```

## Components

1. **agent/watcher.py** - Polls AWS resources, detects changes
2. **agent/analyzer.py** - Uses Brain to assess security impact
3. **agent/planner.py** - Generates Terraform fix
4. **agent/notifier.py** - Sends WhatsApp/Telegram message with buttons
5. **agent/approver.py** - Waits for human confirmation

---

## Tech Stack

- **Polling:** boto3 loops with state comparison
- **Notification:** aiogram (Telegram) / Twilio (WhatsApp)
- **Approval:** UUID tokens + Redis TTL
- **Execution:** subprocess -> terraform apply

---

## Implementation Tasks

1. Create `agent/` module
2. Implement `watcher.py` with S3 polling (10s interval)
3. Build `notifier.py` with Telegram bot
4. Add `approver.py` with inline buttons
5. Connect to existing scanner/brain
6. Test drift detection → notification → approval cycle

---

**Time estimate:** 1 day for Telegram bot, 2-3 days for full flow