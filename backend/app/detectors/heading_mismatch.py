# app/detectors/heading_mismatch.py
"""
Another simple check focusing on yaw jumps between samples.
If yaw changes abruptly without corresponding rotation, flag.
"""
from typing import Dict, List
import math

YAW_JUMP_THRESHOLD = 60.0  # degrees

def detect_heading(pkt: Dict, buf: List[Dict]) -> Dict:
    alert = {"type": "YAW_JUMP", "anomaly": False, "detail": {}}
    try:
        if not buf:
            return alert
        prev = buf[-1]
        if prev.get("yaw") is None or pkt.get("yaw") is None:
            return alert
        try:
            prev_yaw = float(prev["yaw"]); cur_yaw = float(pkt["yaw"])
        except Exception:
            return alert
        diff = abs((cur_yaw - prev_yaw + 180.0) % 360.0 - 180.0)
        if diff >= YAW_JUMP_THRESHOLD:
            alert["anomaly"] = True
            alert["detail"] = {"prev_yaw": prev_yaw, "yaw": cur_yaw, "diff": diff}
            return alert
    except Exception:
        return alert
    return alert
