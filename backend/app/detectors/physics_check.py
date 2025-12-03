# physics_check.py
# Defensive implementation: given previous telemetry and current telemetry,
# flag impossible movement (excessive speed jump).

from typing import Dict, Any
from . import __all__  # keep module importable

def physics_check(prev: Dict[str, Any], curr: Dict[str, Any]) -> Dict[str,Any]:
    # returns alert dict or None
    try:
        if not prev or not curr:
            return None
        dt = max(0.001, curr.get("time",0) - prev.get("time",0))
        # compute distance
        from ..utils.geo import haversine
        dist = haversine(prev["gps_lat"], prev["gps_lon"], curr["gps_lat"], curr["gps_lon"])
        speed = dist / dt if dt>0 else 0.0
        # if instantaneous speed > 80 m/s (~288 km/h) unlikely for demo drone
        if speed > 80:
            return {"type":"physics_impossible", "severity":"high", "detail":{"speed_m_s":speed, "dt":dt}}
    except Exception as e:
        return None
    return None
