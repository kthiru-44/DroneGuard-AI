from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json

from ..state.telemetry_buffer import add as add_telemetry, get_buffer
from ..detectors.physics_check import detect_physics
from ..detectors.gps_spoof import detect_gps_spoof
from ..detectors.imu_consistency import detect_imu
from ..detectors.heading_mismatch import detect_heading

from app.failsafe.failsafe_engine import FailsafeEngine
from ..state.failsafe_state import get_state as get_failsafe_state

from .ws_frontend import broadcast_to_frontend
from app.security.signature_verify import verify_signature

router = APIRouter()

DETECTORS = [detect_physics, detect_gps_spoof, detect_imu, detect_heading]

# ------------------------------
# Initialize new failsafe engine
# ------------------------------
failsafe_engine = FailsafeEngine()


@router.websocket("/ws/pi")
async def ws_pi(websocket: WebSocket):
    await websocket.accept()

    try:
        while True:
            raw = await websocket.receive_text()

            # Parse incoming JSON
            try:
                message = json.loads(raw)
            except Exception:
                continue

            pkt = message.get("payload") if isinstance(message, dict) else None
            if not pkt or not isinstance(pkt, dict):
                continue

            # ----------------------------------------
            # SIGNATURE VERIFICATION (security feature)
            # ----------------------------------------
            if not verify_signature(pkt):
                await broadcast_to_frontend({
                    "type": "signature_fail",
                    "reason": "Invalid signature — telemetry rejected",
                    "raw": pkt
                })
                continue

            # Store telemetry
            add_telemetry(pkt)
            buf = get_buffer()

            # ---------------------------------------------------------
            # RUN DETECTORS → produce list of alerts (same as before)
            # ---------------------------------------------------------
            alerts = []
            for det in DETECTORS:
                try:
                    res = det(pkt, buf)
                    if res and res.get("anomaly"):
                        alerts.append(res)
                except Exception:
                    continue  # Do not break other detectors

            # ---------------------------------------------------------
            # CONVERT alerts[] → single detection object for failsafe
            # ---------------------------------------------------------
            if alerts:
                # Just use the FIRST anomaly (you can combine if needed)
                primary = alerts[0]
                detection = {
                    "attack_detected": True,
                    "attack_type": primary.get("type", "UNKNOWN"),
                    "severity": primary.get("severity", "low"),
                }
            else:
                detection = {"attack_detected": False}

            # --------------------------------------------
            # 💥 NEW FAILSAFE ENGINE LOGIC (AUTO/OFF mode)
            # --------------------------------------------
            failsafe_engine.process_detection(detection)

            # Get failsafe state for frontend
            failsafe_state = get_failsafe_state()

            # ---------------------------------------------------------
            # SEND TELEMETRY + ALERTS + FAILSAFE STATE TO FRONTEND
            # ---------------------------------------------------------
            await broadcast_to_frontend({
                "type": "telemetry",
                "payload": pkt,
                "verified": True,
                "alerts": alerts,
                "failsafe": failsafe_state
            })

    except WebSocketDisconnect:
        return
    except Exception:
        return
