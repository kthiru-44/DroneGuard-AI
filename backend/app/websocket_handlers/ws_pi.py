# ws_pi.py - handle incoming websocket telemetry from Pi
import json
import asyncio
from fastapi import WebSocket

from ..state.telemetry_buffer import TelemetryBuffer
from ..state.failsafe_state import FailsafeState

# shared in-memory state (backend main will provide)
# this module expects main.py to set container attributes

async def handle_pi_ws(websocket: WebSocket, shared):
    await websocket.accept()
    tb: TelemetryBuffer = shared["telemetry_buffer"]
    front_clients = shared["front_clients"]
    failsafe: FailsafeState = shared["failsafe_state"]

    prev = None
    try:
        while True:
            text = await websocket.receive_text()
            try:
                data = json.loads(text)
            except Exception:
                # malformed payload: ignore
                continue
            # attach
            tb.push(data)
            # run detectors defensively
            alerts = []
            from ..detectors.physics_check import physics_check
            from ..detectors.gps_spoof import gps_spoof_check
            from ..detectors.imu_consistency import imu_consistency
            from ..detectors.heading_mismatch import heading_mismatch

            for fn in (physics_check, gps_spoof_check, imu_consistency, heading_mismatch):
                try:
                    a = fn(prev, data)
                    if a:
                        alerts.append(a)
                except Exception:
                    # never crash
                    continue

            # evaluate failsafe decision
            from ..failsafe.failsafe_engine import evaluate_alerts
            decision = evaluate_alerts(alerts)
            if decision.get("activate"):
                failsafe.activate(decision.get("reason","auto"))
                # broadcast failsafe message to frontends
                payload = {"type":"failsafe", "payload":{"active":True, "reason":failsafe.reason}}
                # broadcast
                for ws in list(front_clients):
                    try:
                        await ws.send_text(json.dumps(payload))
                    except Exception:
                        pass

            # broadcast telemetry to frontends
            tmsg = {"type":"telemetry", "payload": data}
            for ws in list(front_clients):
                try:
                    await ws.send_text(json.dumps(tmsg))
                except Exception:
                    # ignore failures
                    pass

            # broadcast alerts if any
            if alerts:
                amsg = {"type":"alert", "payload": alerts}
                for ws in list(front_clients):
                    try:
                        await ws.send_text(json.dumps(amsg))
                    except Exception:
                        pass

            prev = data
    except Exception:
        try:
            await websocket.close()
        except Exception:
            pass
