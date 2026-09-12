# NetWatch

NetWatch is a learning-focused network and infrastructure monitoring system.

## Current Status

Milestone 1 provides a minimal FastAPI backend with a health-check endpoint and an automated test.

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

## Run Tests

```bash
cd backend
source .venv/bin/activate
python -m pytest -v
```
