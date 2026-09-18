# NetWatch: Step-by-Step Guide

This file is a compact map of the project. Read it from top to bottom when the
folders start feeling disconnected.

## 1. The Main Idea

NetWatch stores devices in PostgreSQL and checks them repeatedly.

```text
React dashboard or Postman
          |
       FastAPI
          |
   service layer
          |
    repositories
          |
     PostgreSQL

monitoring worker -> simulator -> service layer -> PostgreSQL
```

The simulator pretends to be a router, server, or switch. It produces an online
or offline result and, when online, CPU, memory, latency, and uptime values.
The worker stores those results. The dashboard reads the stored results through
the API.

## 2. Folder Map

```text
backend/
  app/
    main.py                         FastAPI application and global handlers
    api/routes/                     HTTP endpoints
    api/deps.py                     dependency injection functions
    core/config.py                  environment-backed settings
    db/session.py                   SQLAlchemy engine and sessions
    db/base.py                      declarative SQLAlchemy Base
    models/                         database table definitions
    schemas/                        Pydantic request and response shapes
    repositories/                   database queries and writes
    services/                       application and business rules
    simulator/                      fake device behavior
    workers/                        repeated monitoring orchestration
  alembic/                          database migration files
  tests/                            fast and PostgreSQL integration tests
  Dockerfile                        backend and worker image
frontend/
  src/api.ts                        typed HTTP calls to FastAPI
  src/types.ts                      TypeScript API types
  src/App.tsx                       dashboard state and components
  src/styles.css                    dashboard presentation
  Dockerfile                        Vite build served by Nginx
compose.yaml                        PostgreSQL, backend, worker, frontend
```

## 3. Configuration

`.env` contains local values such as database name, user, password, host, and
port. It is ignored by Git. `.env.example` is the safe template.

`backend/app/core/config.py` loads those values using `pydantic-settings`.
`backend/app/db/session.py` uses the settings to construct a PostgreSQL URL,
create the SQLAlchemy engine, and create sessions.

In Docker Compose, the backend does not use `localhost` for PostgreSQL.
`POSTGRES_HOST=postgres` means "the Compose service named postgres". Docker's
internal network resolves that service name to the database container.

## 4. Database Tables

`Device` is the parent table. `Metric` and `Alert` have foreign keys pointing
to `devices.id`.

```text
devices 1 ---- many metrics
devices 1 ---- many alerts
```

Important relationships:

- A primary key uniquely identifies each row.
- A foreign key connects a child row to its device.
- An index helps PostgreSQL find rows efficiently.
- A migration records a repeatable schema change.
- A metric is historical data and is not overwritten by the next metric.
- An alert is historical data; resolution marks it healthy again instead of
  deleting its history.

Current migrations create devices, metrics, and alerts. Run them with:

```bash
cd backend
python -m alembic upgrade head
```

## 5. One Device Request

For `POST /devices`, the request travels like this:

1. `backend/app/api/routes/devices.py` receives HTTP and validates the body.
2. FastAPI gets a `DeviceService` through `backend/app/api/deps.py`.
3. `DeviceService` applies application rules.
4. `DeviceRepository` performs the database operation.
5. `DeviceResponse` converts the result into JSON.
6. FastAPI returns the response.

The route stays thin. It translates HTTP to a service call and translates the
service result back to HTTP. It does not contain SQL queries.

The same shape is used for metrics and alerts.

## 6. Sessions And Repositories

A SQLAlchemy `Session` is the unit used to talk to the database. It is similar
to a controlled conversation with PostgreSQL:

```python
session.scalar(select(Device).where(Device.id == device_id))
```

That means: execute a SELECT for a Device whose id equals `device_id`, then
return one matching object.

The repository owns this database language. A service owns the decision about
what the application should do. Keeping those responsibilities separate makes
each part easier to test.

## 7. Monitoring Flow

`backend/app/workers/run_monitoring.py` is the command-line entry point.
`backend/app/workers/monitoring_worker.py` is the orchestrator.

For each cycle:

1. Open one fresh database session.
2. Load all registered devices.
3. Ask `DeviceSimulator` for one result per device.
4. Update the device status and `last_seen`.
5. If the result is online, store a new metric row.
6. Ask `AlertService` whether any alert condition changed.
7. Commit changes through the repositories.
8. Close the session.

The simulator does not write to the database because data generation and data
persistence are different jobs. That separation lets us replace the simulator
with ping or SNMP later without rewriting the database layer.

Run one local cycle from `backend/`:

```bash
python -m app.workers.run_monitoring
```

Run continuously:

```bash
python -m app.workers.run_monitoring --cycles 0 --interval 30
```

## 8. Alerts

`AlertService` evaluates four rules:

- offline device -> critical `device_offline`
- CPU over 80 -> warning `high_cpu`
- memory over 90 -> critical `high_memory`
- latency over 200 ms -> warning `high_latency`

The partial unique PostgreSQL index allows at most one unresolved alert of a
given type for a device. When the condition becomes healthy, the service sets
`resolved=True` and records `resolved_at`. The old row remains available as
history.

Endpoints:

```text
GET /alerts
GET /alerts?resolved=false
GET /alerts/devices/{device_id}
```

## 9. Docker Compose

Run the complete MVP from the repository root:

```bash
docker compose up --build
```

Compose starts services in dependency order:

1. `postgres` becomes healthy.
2. `backend` runs `alembic upgrade head`, then starts Uvicorn.
3. `monitoring-worker` waits for the backend health check, then runs every 30
   seconds.
4. `frontend` waits for backend health and serves the built dashboard.

URLs:

- Dashboard: `http://127.0.0.1:5173`
- API docs: `http://127.0.0.1:8000/docs`
- Health: `http://127.0.0.1:8000/health`

The database volume survives `docker compose down`. Use
`docker compose down --volumes` only when you intentionally want to delete
local database data.

## 10. Tests

Fast tests use dependency overrides and do not need PostgreSQL:

```bash
cd backend
python -m pytest -v
```

Integration tests use the separate `netwatch_test` database:

```bash
POSTGRES_DB=netwatch_test python -m alembic upgrade head
RUN_DB_TESTS=1 POSTGRES_DB=netwatch_test python -m pytest -m integration -v
```

The current verified result is 33 fast tests and 3 PostgreSQL integration
tests passing. The frontend is verified with `npm run build` and its Docker
image build.

## 11. What Is Not In The MVP

The current system monitors simulated devices. Real network monitoring would
replace or extend the simulator with ICMP/ping and SNMP collectors. Other
portfolio extensions are Prometheus, Grafana, authentication, role-based
access, WebSockets, retryable job processing, and production deployment.

Those are separate milestones because the current MVP already demonstrates the
core backend loop: register a device, collect measurements, persist history,
generate alerts, expose an API, and inspect the result in a dashboard.
