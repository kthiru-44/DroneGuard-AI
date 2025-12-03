# app/detectors/physics_check.py
"""
Detect impossible movement between consecutive GPS points.
Produces alert dict or None.
"""
from typing import Dict, List, Optional
from ..state.telemetry_buffer import get_buffer
from math import isfinite

# conservative threshold: speed > 50 m/s (~180 km/h) flagged as impossible for small drones
MAX_REASONABLE_SPEED = 50.0

def detect_physics(pkt: Dict, buf: List[Dict]) -> Dict:
    alert = {"type": "PHYSICS_CHECK", "anomaly": False, "detail": {}}
    try:
        # need previous sample (most recent before current)
        if not buf:
            return alert
        prev = buf[-1]
        # require gps fields
        if pkt.get("gps_lat") is None or prev.get("gps_lat") is None:
            return alert
        dt = None
        if "time" in pkt and "time" in prev:
            try:
                dt = float(pkt["time"]) - float(prev["time"])
            except Exception:
                dt = None
        # attempt compute speed from vx/vy if available
        vx = pkt.get("vx", None)
        vy = pkt.get("vy", None)
        speed = None
        if vx is not None and vy is not None:
            try:
                speed = (float(vx)**2 + float(vy)**2) ** 0.5
            except Exception:
                speed = None

        # if telemetry has speed field, use it as fallback
        if not speed and pkt.get("speed") is not None:
            try:
                speed = float(pkt["speed"])
            except Exception:
                speed = None

        # If we have dt and prev gps, check for weird jump by euclidean distance
        if dt and dt > 0 and prev.get("gps_lat") is not None and prev.get("gps_lon") is not None:
            # great-circle distance approx (very small distances)
            lat1, lon1 = float(prev["gps_lat"]), float(prev["gps_lon"])
            lat2, lon2 = float(pkt["gps_lat"]), float(pkt["gps_lon"])
            # rough meters delta using lat ~111km, lon scaled by cos(lat)
            dy = (lat2 - lat1) * 111000.0
            dx = (lon2 - lon1) * (111000.0 * abs(math.cos(math.radians(lat1))) if lat1 is not None else 111000.0)
            dist = (dx*dx + dy*dy) ** 0.5
            implied_speed = dist / dt if dt else None
            if implied_speed and implied_speed > MAX_REASONABLE_SPEED:
                alert["anomaly"] = True
                alert["type"] = "IMPOSSIBLE_MOVEMENT"
                alert["detail"] = {
                    "implied_speed": implied_speed,
                    "threshold": MAX_REASONABLE_SPEED,
                    "dt": dt,
                    "jump_meters": dist
                }
                return alert

        if speed and speed > MAX_REASONABLE_SPEED:
            alert["anomaly"] = True
            alert["type"] = "IMPOSSIBLE_MOVEMENT"
            alert["detail"] = {"speed": speed, "threshold": MAX_REASONABLE_SPEED}
            return alert

    except Exception as e:
        # silently handle errors; do not crash
        return alert

    return alert
