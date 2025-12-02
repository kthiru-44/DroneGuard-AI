import math

def detect_imu(pkt, buf):
    if len(buf) < 2:
        return {"anomaly": False}

    vx, vy = pkt.get("vx"), pkt.get("vy")
    if vx == 0 and vy == 0:
        return {"anomaly": False}

    heading = math.degrees(math.atan2(vy, vx)) % 360
    yaw = pkt.get("yaw", 0) % 360

    diff = abs((heading - yaw + 180) % 360 - 180)

    if diff > 60:
        return {
            "anomaly": True,
            "type": "IMU_HEADING_MISMATCH",
            "reason": f"Heading {heading} vs Yaw {yaw}"
        }

    return {"anomaly": False}
