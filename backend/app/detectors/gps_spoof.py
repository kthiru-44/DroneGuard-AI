from .physics_check import distance_m

def detect_gps_spoof(pkt, buf):
    if len(buf) < 3:
        return {"anomaly": False}

    p1 = buf[-3]
    p2 = buf[-2]

    if p1["gps_lat"] is None or p2["gps_lat"] is None or pkt["gps_lat"] is None:
        return {"anomaly": False}

    d2 = distance_m(p2["gps_lat"], p2["gps_lon"],
                    pkt["gps_lat"], pkt["gps_lon"])

    if d2 > 20:
        return {"anomaly": True, "type": "GPS_SPOOF", "distance_jump": d2,
                "reason": "sudden GPS change"}

    return {"anomaly": False}
