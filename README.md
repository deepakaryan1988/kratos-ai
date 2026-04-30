# KRATOS - AI Cloud Security Scanner

AI-powered cloud security scanner with architectural remediation recommendations.

## Quick Start

```bash
# Copy environment template
cp .env.example .env

# Start infrastructure
docker-compose up -d

# Install dependencies
uv pip install -e .

# Run security scan
uv run python kratos.py
```

## Architecture

```
┌─────────────┐     ┌──────────┐     ┌────────────┐
│    Scanner  │────▶│   Brain  │────▶│   Vault    │
│ (Cloud APIs)│     │(LLM Plan)│     │(PostgreSQL)│
└─────────────┘     └──────────┘     └────────────┘
```

## Components

- **agents/scanner.py** - Checks S3, IAM, EC2, RDS for security issues
- **agents/brain.py** - Generates Terraform plans via LLM
- **agent/agent.py** - Autonomous agent with scheduled scanning
- **agent/watcher.py** - Filesystem change detection
- **agent/notifier.py** - Notification delivery
- **vault/policy_store.py** - Stores findings as vectors for similarity search
- **kratos.py** - CLI entry point

## Scan Types

| Resource | Checks |
|----------|--------|
| S3 | KMS encryption required |
| IAM | User verification, MFA enforcement |
| EC2 | Public IP exposure |
| RDS | Public access, encryption at rest |

## Development

```bash
# Run tests
uv run pytest

# Dry run (scan only)
uv run python kratos.py --dry-run

# Run autonomous agent (scheduled scans)
uv run python agent/agent.py
```

## Environment Variables

```bash
LOCAL_LLM_URL=http://localhost:1234/v1    # LM Studio API
LOCAL_LLM_MODEL=qwen3.5-9b-claude-4.6-opus-reasoning-distilled-v2
AWS_ENDPOINT_URL=http://localhost:4566      # LocalStack
SCAN_INTERVAL=60                            # Agent scan interval (seconds)
```

## License

MIT