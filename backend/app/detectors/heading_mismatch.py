def detect_heading(pkt, buf):
    if len(buf) < 2:
        return {"anomaly": False}

    roll = pkt.get("roll")
    pitch = pkt.get("pitch")

    if abs(roll) > 45 or abs(pitch) > 45:
        return {
            "anomaly": True,
            "type": "IMU_SPIKE",
            "reason": "Roll/Pitch spike detected"
        }

    return {"anomaly": False}
