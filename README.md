# NetWatch

NetWatch is a learning-focused network and infrastructure monitoring system.

## Current Status

Milestone 2 provides an in-memory Device API with validation, CRUD operations,
and automated API tests. PostgreSQL persistence is planned for Milestone 3.

## Requirements

- Python 3.11 or newer

## Backend Setup

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

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
- PostgreSQL will replace the temporary storage in Milestone 3.

## Run Tests

```bash
cd backend
source .venv/bin/activate
python -m pytest -v
```
