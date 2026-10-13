# Optical Fault Backside Laser Agent

A rule-based telemetry classification demonstration with a Python CLI, FastAPI endpoint, HMAC-linked in-memory event log, and a standalone browser interface.

**Scope:** The software compares two abstract measurements against demonstration thresholds (primary > 25; secondary > 12), a critical flag, and status descriptors. It does **not** simulate laser physics, operate hardware, validate semiconductor security, or implement CAP/CLSI/ISO certification workflows.

## Browser interface

Open [web/index.html](web/index.html) directly or serve it locally. The default mode runs entirely in the browser, without external APIs or Python. For API-backed results, run the server and select **Same-origin FastAPI backend**. Browser demonstration results are deliberately **not** signed audit records.

GitHub Pages deployment is defined in [the Pages workflow](.github/workflows/pages.yml); availability depends on repository Pages settings and a successful workflow run.

## Installation

Requires Python 3.10 or newer.

```bash
python -m pip install -e ".[dev]"
python -m pytest -q

# Single-task classification
python cli.py audit --task-id TASK-001 --target KEY-01 --primary 28.5 --secondary 14.2 --status DISCORDANT

# Batch file processing
python cli.py batch -i sample.csv -o results.csv

# Start local HTTP server and browser interface
python cli.py serve --host 127.0.0.1 --port 8000
```

The API UI is available at `http://127.0.0.1:8000/`, interactive API docs at `/docs`. Endpoints are `GET /health`, `GET /metrics` (JSON counters), `POST /api/audit`, `POST /api/chat`, and `GET /api/audit/logs`. Chat is a deterministic mock responder, not a network-connected language model.

**CSV fields:** `task_id,target_identifier,primary_metric,secondary_metric,is_critical_flag,status_descriptor`. Numeric measurements must be finite. Critical flags accept `true/false`, `yes/no`, or `1/0` (case-insensitive). Malformed Booleans are rejected.

The repository also retains a **separate legacy interface** in `optical_fault_agent/`, available as `optical-fault-backside-laser-engine`. It has different thresholds and output field names. The primary command is `optical-fault-backside-laser-agent`.

## Container deployment

```bash
export AUDIT_SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')"
docker compose up --build
```

Docker Compose binds to `127.0.0.1:8000` only. The API has **no authentication or authorization**. Do not expose it publicly without appropriate access controls, TLS, and rate limits.

## Security and privacy boundaries

- Audit event metadata and the event payload hash are HMAC-SHA256 signed, with per-record chaining. Verification recomputes signatures; audit data is held only in process memory.
- Set a stable `AUDIT_SECRET_KEY` to keep a consistent signing key across restarts. Without it, an ephemeral key is used; no events are persisted regardless.
- Regex-based checks reject a limited set of recognizable sensitive identifiers. This does **not** guarantee removal of personal information, HIPAA compliance, or comprehensive de-identification.
- Browser-only mode keeps the entered data in the current page session; Save JSON downloads the displayed result. It makes no API calls or third-party font requests.
- These are software demonstration rules, not validated physical limits or certified safety controls.

## Testing and platform support

```bash
python -m pytest -q
node --check web/app.js
node --test web/test_app.cjs
```

CI tests Python 3.10–3.12 and browser classifier rules. The browser interface uses standard JavaScript; no Pyodide/PyScript runtime is necessary. Modern Chrome, Firefox, Safari, and Edge are supported targets.

## License

[MIT](LICENSE).
