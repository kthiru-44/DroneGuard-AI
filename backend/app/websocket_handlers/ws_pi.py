import json
from fastapi import APIRouter, WebSocket

from ..state.telemetry_buffer import add, get_buffer
from ..detectors.physics_check import detect_physics
from ..detectors.gps_spoof import detect_gps_spoof
from ..detectors.imu_consistency import detect_imu
from ..detectors.heading_mismatch import detect_heading

from ..failsafe.failsafe_engine import evaluate_failsafe
from ..state.failsafe_state import get_failsafe

from .ws_frontend import broadcast_to_frontend   # <--- MUST BE HERE

router = APIRouter()

@router.websocket("/ws/pi")
async def ws_pi(websocket: WebSocket):
    await websocket.accept()

    while True:
        raw = await websocket.receive_text()
        data = json.loads(raw)
        pkt = data["payload"]

        add(pkt)
        buf = get_buffer()

        alerts = []
        for detector in [detect_physics, detect_gps_spoof, detect_imu, detect_heading]:
            result = detector(pkt, buf)
            if result["anomaly"]:
                alerts.append(result)

        failsafe_result = evaluate_failsafe(alerts)
        failsafe_state = get_failsafe()

        await broadcast_to_frontend({
            "type": "telemetry",
            "payload": pkt,
            "alerts": alerts,
            "failsafe": failsafe_state
        })
