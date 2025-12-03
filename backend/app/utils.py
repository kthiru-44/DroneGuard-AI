# app/utils.py
import math

def speed_from_vxy(vx, vy):
    try:
        return float(math.hypot(float(vx), float(vy)))
    except Exception:
        return None
