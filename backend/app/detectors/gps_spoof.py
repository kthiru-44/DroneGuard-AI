# gps_spoof.py
# Simple GPS spoof detector: checks sudden coordinate jumps inconsistent with IMU velocity.

from typing import Dict, Any

def gps_spoof_check(prev: Dict[str,Any], curr: Dict[str,Any]) -> Dict[str,Any]:
    try:
        if not prev or not curr:
            return None
        # compare reported speed vs positional displacement
        dx = curr.get("vx",0)
        dy = curr.get("vy",0)
        reported_speed = curr.get("speed",0)
        from math import hypot
        vel_mag = hypot(dx, dy)
        # if difference between reported speed and IMU vel > threshold, and big position jump, flag
        pos_jump = abs(curr["gps_lat"] - prev["gps_lat"]) + abs(curr["gps_lon"] - prev["gps_lon"])
        if pos_jump > 0.0005 and abs(reported_speed - vel_mag) > 5:
            return {"type":"gps_spoof", "severity":"medium", "detail": {"pos_jump": pos_jump, "reported_speed":reported_speed, "imu_speed":vel_mag}}
    except Exception:
        return None
    return None
