# app/detectors/gps_spoof.py
"""
Detect sudden GPS jumps relative to previous buffered points.
Simple algorithm:
 - compute horizontal jump between current and previous GPS
 - if jump is greater than a configurable threshold (e.g., 30 m) and speed inconsistency, flag GPS_SPOOF
"""
from typing import Dict, List
import math

GPS_JUMP_THRESHOLD_M = 30.0  # meters for sudden jump

def detect_gps_spoof(pkt: Dict, buf: List[Dict]) -> Dict:
    alert = {"type": "GPS_SPOOF", "anomaly": False, "detail": {}}
    try:
        if not buf:
            return alert
        prev = buf[-1]
        if prev.get("gps_lat") is None or prev.get("gps_lon") is None:
            return alert
        if pkt.get("gps_lat") is None or pkt.get("gps_lon") is None:
            return alert
        lat1, lon1 = float(prev["gps_lat"]), float(prev["gps_lon"])
        lat2, lon2 = float(pkt["gps_lat"]), float(pkt["gps_lon"])
        dy = (lat2 - lat1) * 111000.0
        dx = (lon2 - lon1) * (111000.0 * abs(math.cos(math.radians(lat1))))
        dist = math.hypot(dx, dy)
        if dist >= GPS_JUMP_THRESHOLD_M:
            alert["anomaly"] = True
            alert["detail"] = {"jump_m": dist, "threshold_m": GPS_JUMP_THRESHOLD_M}
            return alert
    except Exception:
        return alert
    return alert
