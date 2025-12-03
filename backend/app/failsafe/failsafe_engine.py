# app/failsafe/failsafe_engine.py
"""
Simple failsafe evaluator:
- if multiple alerts occur within short time window, or IMPOSSIBLE_MOVEMENT detected,
  decide to activate failsafe automatically (demo).
This is a demo policy; in production you'd have more nuanced rules.
"""
from typing import List, Dict
from ..state.failsafe_state import activate, get_state

AUTO_ALERT_COUNT_TO_FAILSAFE = 4

def evaluate_failsafe(alerts: List[Dict]) -> Dict:
    """
    Decide (demo) whether to trigger failsafe automatically.
    Returns dict describing action; does NOT activate failsafe by default (for demo).
    """
    result = {"trigger": False, "reason": None}
    if not alerts:
        return result
    # If any impossible movement -> recommend failsafe
    for a in alerts:
        if a.get("type") == "IMPOSSIBLE_MOVEMENT":
            result["trigger"] = True
            result["reason"] = "IMPOSSIBLE_MOVEMENT"
            return result
    # if too many alerts in this batch
    if len(alerts) >= AUTO_ALERT_COUNT_TO_FAILSAFE:
        result["trigger"] = True
        result["reason"] = "TOO_MANY_ALERTS"
    return result
