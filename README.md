# NetWatch

NetWatch is a learning-focused network and infrastructure monitoring system.

## Current Status

Milestone 4 is complete. Device inventory and historical metrics persist in
PostgreSQL, which runs locally through Docker Compose.

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

## Run The API

```bash
cd backend
source .venv/bin/activate
python -m uvicorn app.main:app --reload
```

Health check: `http://127.0.0.1:8000/health`

Interactive documentation: `http://127.0.0.1:8000/docs`

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

## Current Limitations

- Database constraints reject duplicate hostnames and IP addresses, but the API
  does not yet translate those conflicts into a friendly HTTP response.
- Automatic monitoring workers and alerts are not implemented yet.
- The React dashboard is not implemented yet.

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
