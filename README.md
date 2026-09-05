# Optical Fault Backside Laser Agent

> **Domain:** Clinical Decision Support & Biomedical Computing  
> **Standards:** CAP / CLSI / ISO Quality Frameworks

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB.svg?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688.svg?logo=fastapi&logoColor=white)
![Audit Trail](https://img.shields.io/badge/Audit-HMAC--SHA256_Tamper--Evident-brightgreen.svg)
![Zero-PHI Guard](https://img.shields.io/badge/Guard-Zero--PHI_Outbound-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)

</div>

---

## Overview

Optical Fault Backside Laser Agent is an enterprise-grade analytical platform that orchestrates multi-worker evaluation of optical fault injection data. It provides deterministic risk classification, cryptographic audit trails, and zero-PHI outbound data protection for clinical and biomedical AI workflows.

---

## Key Capabilities

- **Multi-Worker Evaluation Engine**: Three specialized workers (InvariantQC, SafetyEscalation, ProtocolConformance) analyze each task payload
- **Risk & Urgency Classification**: Multi-tier categorization (ROUTINE, ELEVATED_RISK, CRITICAL_STAT_PANIC) with automated remediation recommendations
- **Zero-PHI Outbound Interceptor**: Active regex inspection blocking SSNs, MRNs, phone numbers, and patient identifiers
- **Tamper-Evident HMAC-SHA256 Audit Trail**: Chained, cryptographically signed logs for every evaluation
- **FastAPI REST API**: OpenAPI 3.1 endpoints with Prometheus telemetry (`/metrics`)
- **Batch Processing**: CSV-based high-throughput task evaluation
- **Enrichment Suite**: 8 domain-specific analytical engines for optical fault injection analysis

---

## Installation

```bash
# Clone the repository
git clone https://github.com/abusuraihsakhri/optical-fault-backside-laser-agent.git
cd optical-fault-backside-laser-agent

# Install dependencies
pip install fastapi uvicorn pydantic pytest
```

---

## CLI Usage

### 1. Single Task Evaluation (Audit)
```bash
python cli.py audit --task-id TASK-001 --target KEY-01 --primary 28.5 --secondary 14.2 --critical --status DISCORDANT
```

### 2. System Query (Chat)
```bash
python cli.py chat "What is the system status?"
```

### 3. Batch CSV Processing
```bash
python cli.py batch -i sample.csv -o results.csv
```

### 4. Verify Audit Trail Integrity
```bash
python cli.py verify-audit
```

### 5. Launch REST API Server
```bash
python cli.py serve --host 127.0.0.1 --port 8000
```

### CLI Parameters

| Parameter | Description | Default |
|:----------|:------------|:--------|
| `--task-id` | Unique task/case identifier | TASK-2026-001 |
| `--target` | Target entity or specimen key | KEY-TARGET-01 |
| `--primary` | Primary measurement value (float) | 28.5 |
| `--secondary` | Secondary metric value (float) | 14.2 |
| `--critical` | Flag as critical/emergency | False |
| `--status` | Status descriptor (NOMINAL, DISCORDANT, etc.) | DISCORDANT |

### Input Data Schema (CSV/JSON)

| Field | Type | Description | Required |
|:------|:-----|:------------|:---------|
| `task_id` | string | Unique task identifier | Yes |
| `target_identifier` | string | Target entity key | Yes |
| `primary_metric` | float | Primary measurement | Yes |
| `secondary_metric` | float | Secondary metric | No (default: 0.0) |
| `is_critical_flag` | bool | Emergency escalation flag | No (default: false) |
| `status_descriptor` | string | Status/phenotype descriptor | No (default: NOMINAL) |

---

## REST API Endpoints

| Method | Endpoint | Description |
|:-------|:---------|:------------|
| GET | `/health` | Service health check |
| GET | `/metrics` | Operational metrics |
| POST | `/api/audit` | Submit task for evaluation |
| POST | `/api/chat` | Query the system |
| GET | `/api/audit/logs` | Retrieve audit trail |

---

## Security Configuration

### Audit Secret Key
The HMAC-SHA256 audit trail requires a secret key. Set the `AUDIT_SECRET_KEY` environment variable in production:

```bash
export AUDIT_SECRET_KEY="your-secure-random-key-min-32-chars"
```

If not set, an ephemeral key is generated at startup (signatures will not persist across restarts).

### PHI Protection
The Zero-PHI Outbound Guard automatically blocks:
- Medical Record Numbers (MRN)
- Social Security Numbers (SSN)
- Phone numbers
- Email addresses
- Patient names (e.g., "John Doe")
- Date of birth patterns

---

## Testing

```bash
# Run the full test suite
pytest -v

# Run with coverage
pytest -v --tb=short
```

### Test Coverage
- PHI guard enforcement
- Individual worker evaluation logic
- Supervisor consensus and audit trail
- CLI command execution
- Enrichment suite execution and threshold escalation

---

## Docker Deployment

```bash
docker build -t optical-fault-backside-laser-agent .
docker run -p 8000:8000 -e AUDIT_SECRET_KEY="your-secret-key" optical-fault-backside-laser-agent
```

Using Docker Compose:
```bash
docker-compose up -d
```

---

## Project Structure

```
optical-fault-backside-laser-agent/
├── agents/                  # Core agent modules
│   ├── __init__.py
│   ├── api.py              # FastAPI REST server
│   ├── base.py             # Security, PHI guard, HMAC audit
│   ├── learning.py         # Bayesian calibration engine
│   ├── llm_factory.py      # LLM provider factory
│   ├── metrics.py          # Prometheus metrics
│   ├── models.py           # Pydantic data models
│   ├── streamer.py         # WebSocket telemetry
│   ├── supervisor.py       # Main orchestrator
│   └── workers.py          # Specialized evaluation workers
├── tests/                   # Test suite
├── web/                     # Operations console (HTML)
├── cli.py                   # CLI entry point
├── enrichment.py            # Domain enrichment engines
├── simulator.py             # High-throughput simulation
├── pyproject.toml           # Project metadata
├── Dockerfile               # Container build
└── docker-compose.yml       # Container orchestration
```

---

## License

MIT License - see [LICENSE](LICENSE) for details.
