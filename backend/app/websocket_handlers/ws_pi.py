# app/websocket_handlers/ws_pi.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json
from ..state.telemetry_buffer import add as add_telemetry, get_buffer
from ..detectors.physics_check import detect_physics
from ..detectors.gps_spoof import detect_gps_spoof
from ..detectors.imu_consistency import detect_imu
from ..detectors.heading_mismatch import detect_heading
from ..failsafe.failsafe_engine import evaluate_failsafe
from ..state.failsafe_state import get_state as get_failsafe_state
from .ws_frontend import broadcast_to_frontend

router = APIRouter()

DETECTORS = [detect_physics, detect_gps_spoof, detect_imu, detect_heading]

@router.websocket("/ws/pi")
async def ws_pi(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            raw = await websocket.receive_text()
            try:
                message = json.loads(raw)
            except Exception:
                # ignore invalid
                continue
            # expect {"payload": pkt}
            pkt = message.get("payload") if isinstance(message, dict) else None
            if not pkt or not isinstance(pkt, dict):
                continue

            # store telemetry
            add_telemetry(pkt)
            buf = get_buffer()

            # run detectors
            alerts = []
            for d in DETECTORS:
                try:
                    res = d(pkt, buf)
                    if res and res.get("anomaly"):
                        alerts.append(res)
                except Exception:
                    # keep running detectors even if one fails
                    continue

            failsafe_eval = evaluate_failsafe(alerts)
            failsafe_state = get_failsafe_state()

            # broadcast telemetry and alerts to frontends
            await broadcast_to_frontend({
                "type": "telemetry",
                "payload": pkt,
                "alerts": alerts,
                "failsafe_eval": failsafe_eval,
                "failsafe": failsafe_state
            })

    except WebSocketDisconnect:
        return
    except Exception:
        return
