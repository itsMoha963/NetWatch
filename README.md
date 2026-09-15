# NetWatch

NetWatch is a learning-focused network and infrastructure monitoring system.

## Current Status

Milestone 3 is in progress. The Device API still uses temporary in-memory
storage, and a PostgreSQL development database now runs through Docker Compose.

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

## Current Limitations

- Devices are stored in process memory and disappear when the API restarts.
- Multiple API processes would not share the same device data.
- Duplicate hostnames and IP addresses are not rejected yet.
- Metrics, monitoring workers, and alerts are not implemented yet.
- PostgreSQL is running, but the Device API is not connected to it yet.

## Run Tests

```bash
cd backend
source .venv/bin/activate
python -m pytest -v
```
