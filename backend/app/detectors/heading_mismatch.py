# heading_mismatch.py
# Compare GPS track-bearing with IMU yaw

from typing import Dict, Any
import math

def heading_mismatch(prev: Dict[str,Any], curr: Dict[str,Any]) -> Dict[str,Any]:
    try:
        if not prev or not curr:
            return None
        # compute course from vx,vy
        vx = curr.get("vx",0); vy = curr.get("vy",0)
        if vx==0 and vy==0:
            return None
        course = (math.degrees(math.atan2(vy, vx)) + 360) % 360
        yaw = curr.get("yaw",0) % 360
        delta = min(abs(course-yaw), 360-abs(course-yaw))
        if delta > 45:
            return {"type":"course_vs_yaw_mismatch", "severity":"low", "detail": {"course":course, "yaw":yaw, "delta":delta}}
    except Exception:
        return None
    return None
