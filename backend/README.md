# DroneGuard Local Demo Backend

## Purpose
Local-only FastAPI backend for demo/hackathon. Accepts telemetry via WebSocket at `/ws/pi` (from local `drone.py`) and publishes telemetry/alerts to frontend at `/ws/frontend`.

**Important safety note:** By default this backend is local-only (binds to 127.0.0.1). Do not change to public interfaces unless you understand the risks.

## Run
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m app.main
