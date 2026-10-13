# Endpoint Diagnostics & IT Support Toolkit (EDST)

Independent local-first portfolio project demonstrating endpoint diagnostics, DNS/TCP troubleshooting, incident handling, reporting, documentation, and automation. This project is not affiliated with OpenAI and does not imitate or access internal employer systems.

## Features
- Safe Windows/Linux-oriented system summary: OS, architecture, uptime, CPU, memory, and disks.
- DNS resolution and TCP reachability with validation and timeouts. No shell execution.
- Incident create/read/update/delete, notes, filters, SQLite persistence, and history clearing.
- JSON and Markdown exports with a review-before-sharing warning.
- Manual local device inventory. No network discovery or MDM claims.
- Responsive accessible React UI with loading, empty, success/error states and demo mode.
- Predictable API errors with request IDs.

## Stack
Python 3.11+, FastAPI, Pydantic, SQLAlchemy, SQLite, psutil, pytest, Ruff; React, TypeScript, Vite, Vitest/Testing Library.

## Architecture
See [docs/architecture.md](docs/architecture.md). Flow: React UI -> FastAPI -> isolated diagnostics / incidents / reports -> SQLite or safe OS/network APIs.

## Quick start
### Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -e '.[dev]'
uvicorn app.main:app --reload
```
API: http://localhost:8000, docs: http://localhost:8000/docs.

### Frontend
```bash
cd frontend
npm install
npm run dev
```
Open http://localhost:5173.

Or run `docker compose up`.

## Configuration
Copy `.env.example` to `.env`. `EDST_DATABASE_URL`, `EDST_DEMO_MODE`, `EDST_SHOW_HOSTNAME`, and `VITE_API_URL` are supported.

## Quality commands
```bash
make backend-test
make backend-lint
make frontend-test
make frontend-build
# optional coverage
cd backend && pytest --cov=app
```

## API examples
```bash
curl http://localhost:8000/api/v1/health
curl 'http://localhost:8000/api/v1/diagnostics/system?demo=true'
curl -X POST http://localhost:8000/api/v1/diagnostics/network -H 'Content-Type: application/json' -d '{"hostname":"example.com","port":443}'
curl -X POST http://localhost:8000/api/v1/incidents -H 'Content-Type: application/json' -d '{"title":"Internet unavailable","description":"DNS lookup fails","category":"Network","priority":"High","status":"Open"}'
```

## Privacy & security
Collected: OS/platform summary, hostname only when enabled, uptime, CPU/memory/disk availability, requested DNS/TCP results, and operator-entered incident fields. Not collected: passwords, tokens, cookies, file contents, browser history, MAC addresses, serial numbers, or personal files. The app never executes user input as a command. Delete an incident with `DELETE /api/v1/incidents/{id}` or clear incident history with `DELETE /api/v1/history`.

## Supported platforms
| Platform | Status |
|---|---|
| Linux container used for automated verification | Tested |
| Windows | Implemented using psutil/platform; not tested in this environment |
| macOS | Not tested; no support claim |

## Demo and usage
Enable Demo mode in the header. Suggested flow: Overview -> Diagnostics -> DNS/TCP check -> Incidents -> create incident -> export JSON/Markdown -> review Threat Model.

## Documentation
- [Architecture](docs/architecture.md)
- [Threat model](docs/threat-model.md)
- [Troubleshooting runbook](docs/troubleshooting-runbook.md)
- [Sample report](docs/sample-report.md)

## Known limitations and roadmap
No authentication (local single-user MVP), no gateway auto-detection, no HTTP checker, no MDM/enterprise integrations, no remote control, and no macOS test claim. Future work may add explicit local authentication, configured HTTP allowlists, gateway detection, and manually verified screenshots/demo video.
