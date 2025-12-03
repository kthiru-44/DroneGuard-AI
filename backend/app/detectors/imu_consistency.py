# app/detectors/imu_consistency.py
"""
Compare IMU-derived heading (from vx,vy) against IMU yaw value.
Flag if mismatch greater than threshold.
"""
from typing import Dict, List
import math

HEADING_MISMATCH_THRESHOLD_DEG = 40.0  # degrees

def detect_imu(pkt: Dict, buf: List[Dict]) -> Dict:
    alert = {"type": "IMU_HEADING_MISMATCH", "anomaly": False, "detail": {}}
    try:
        vx = pkt.get("vx", None)
        vy = pkt.get("vy", None)
        yaw = pkt.get("yaw", None)
        # require numeric values
        if vx is None or vy is None or yaw is None:
            return alert
        try:
            vx = float(vx); vy = float(vy); yaw = float(yaw)
        except Exception:
            return alert
        speed = math.hypot(vx, vy)
        if speed < 0.5:  # low speed: IMU heading unreliable
            return alert
        # compute velocity-derived heading (0-360)
        heading = (math.degrees(math.atan2(vx, vy)) + 360.0) % 360.0
        diff = abs((heading - yaw + 180) % 360 - 180)
        if diff >= HEADING_MISMATCH_THRESHOLD_DEG:
            alert["anomaly"] = True
            alert["detail"] = {"heading": heading, "yaw": yaw, "diff": diff, "threshold": HEADING_MISMATCH_THRESHOLD_DEG}
            return alert
    except Exception:
        return alert
    return alert
