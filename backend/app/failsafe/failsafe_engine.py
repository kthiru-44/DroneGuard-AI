# failsafe_engine.py
from typing import Dict, Any

def evaluate_alerts(alerts):
    # Simple rule: if any high severity alert present -> enable failsafe
    for a in alerts:
        if a.get("severity") == "high":
            return {"activate": True, "reason": a.get("type")}
    return {"activate": False}
