# NetWatch

NetWatch is a learning-focused network and infrastructure monitoring system.

## Current Status

The MVP is complete. NetWatch persists devices, historical metrics, and
duplicate-safe alerts in PostgreSQL. A Docker Compose stack runs the API,
database, monitoring worker, and React dashboard together.

## Requirements

- Python 3.11 or newer
- Docker Desktop with Docker Compose

## Backend Setup

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

## PostgreSQL Setup

Run these commands from the repository root. Create your local environment file
from the tracked example, then replace `change_me` with a development password:

```bash
cp .env.example .env
docker compose config --quiet
docker compose up -d postgres
```

Apply the database migrations from the `backend/` directory:

```bash
cd backend
python -m alembic upgrade head
```

Check that PostgreSQL is running:

```bash
docker compose ps
docker compose exec postgres psql -U netwatch -d netwatch \
  -c "SELECT current_database(), current_user;"
```

Stop the container when you are finished:

```bash
docker compose down
```

The named Docker volume preserves the database between normal stops. Running
`docker compose down --volumes` also deletes the local database data.

## Run The Full Stack With Docker

From the repository root:

```bash
docker compose up --build
```

Open the dashboard at `http://127.0.0.1:5173` and the API documentation at
`http://127.0.0.1:8000/docs`. The Compose network lets the backend and worker
reach PostgreSQL using the service hostname `postgres`; the browser reaches the
API through the published host port `8000`.

The `monitoring-worker` service runs one simulated check every 30 seconds. Stop
the stack with `Ctrl+C` or `docker compose down`.

## Run The API

```bash
cd backend
source .venv/bin/activate
python -m uvicorn app.main:app --reload
```

Health check: `http://127.0.0.1:8000/health`

Interactive documentation: `http://127.0.0.1:8000/docs`

The API can also be run locally while PostgreSQL remains in Docker. In that
case, use the local `.env` values where `POSTGRES_HOST=localhost`.

## Run Simulated Monitoring

Run one monitoring cycle from the `backend/` directory:

```bash
python -m app.workers.run_monitoring
```

Run five cycles with ten seconds between cycles:

```bash
python -m app.workers.run_monitoring --cycles 5 --interval 10
```

Run continuously until `Ctrl+C`:

```bash
python -m app.workers.run_monitoring --cycles 0 --interval 30
```

## Device API

| Method | Path | Purpose |
| --- | --- | --- |
| `POST` | `/devices` | Create a device |
| `GET` | `/devices` | List all devices |
| `GET` | `/devices/{device_id}` | Get one device |
| `PUT` | `/devices/{device_id}` | Replace one device |
| `DELETE` | `/devices/{device_id}` | Delete one device |
| `POST` | `/devices/{device_id}/metrics` | Store one measurement |
| `GET` | `/devices/{device_id}/metrics` | List recent measurements |
| `GET` | `/alerts` | List alerts, optionally filtered by resolution |
| `GET` | `/alerts/devices/{device_id}` | List alerts for one device |

## Current Limitations

- The simulator is deterministic only when given a seeded random generator; it
  is intentionally not a real network probe.
- Simulated monitoring is a simple long-running Compose service rather than a
  production job queue with retries and scheduling guarantees.
- Authentication, authorization, SNMP, Prometheus, Grafana, and WebSockets are
  later extensions.

## Run Tests

Run the fast API tests, which use an in-memory service override:

```bash
cd backend
source .venv/bin/activate
python -m pytest -v
```

Run the PostgreSQL repository integration test against the isolated test
database:

```bash
docker compose exec postgres createdb -U netwatch netwatch_test
cd backend
POSTGRES_DB=netwatch_test python -m alembic upgrade head
RUN_DB_TESTS=1 POSTGRES_DB=netwatch_test python -m pytest -m integration -v
```

The `createdb` command is only needed once and reports an error if the test
database already exists.

The integration test refuses to run against any database other than
`netwatch_test`.
