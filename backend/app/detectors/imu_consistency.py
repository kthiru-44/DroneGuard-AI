# imu_consistency.py
# Check IMU roll/pitch/yaw for extreme jumps

from typing import Dict, Any

def imu_consistency(prev: Dict[str,Any], curr: Dict[str,Any]) -> Dict[str,Any]:
    try:
        if not prev or not curr:
            return None
        for k in ("roll","pitch","yaw"):
            if abs(curr.get(k,0) - prev.get(k,0)) > 60:  # degrees jump
                return {"type":"imu_heading_mismatch", "severity":"medium", "detail": {"field":k, "delta": abs(curr.get(k,0) - prev.get(k,0))}}
    except Exception:
        return None
    return None
