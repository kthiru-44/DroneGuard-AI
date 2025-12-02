from ..state.failsafe_state import set_failsafe

CRITICAL_ALERTS = [
    "GPS_SPOOF",
    "IMU_HEADING_MISMATCH",
    "IMPOSSIBLE_MOVEMENT",
    "IMU_SPIKE",
    "GPS_JAMMING"
]

def evaluate_failsafe(alerts):
    if not alerts:
        set_failsafe("NONE")
        return {"action": "NONE"}

    # Check if any critical alert exists
    for alert in alerts:
        if alert["type"] in CRITICAL_ALERTS:
            # Select proper action
            if alert["type"] == "GPS_SPOOF":
                action = "HOLD"      # freeze motion
            elif alert["type"] == "GPS_JAMMING":
                action = "HOLD"
            elif alert["type"] == "IMU_SPIKE":
                action = "HOLD"
            elif alert["type"] == "IMPOSSIBLE_MOVEMENT":
                action = "LAND"
            elif alert["type"] == "IMU_HEADING_MISMATCH":
                action = "LAND"
            else:
                action = "KILL"

            set_failsafe(action)
            return {"action": action}

    set_failsafe("NONE")
    return {"action": "NONE"}
