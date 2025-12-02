import math

def distance_m(lat1, lon1, lat2, lon2):
    R = 6371000
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat/2)**2 +
        math.cos(math.radians(lat1)) *
        math.cos(math.radians(lat2)) *
        math.sin(dlon/2)**2
    )
    return 2 * R * math.asin(math.sqrt(a))

def detect_physics(pkt, buf):
    if len(buf) < 2:
        return {"anomaly": False}

    prev = buf[-2]

    if pkt["gps_lat"] is None or prev["gps_lat"] is None:
        return {"anomaly": True, "type": "GPS_JAMMING", "reason": "GPS missing"}

    dist = distance_m(prev["gps_lat"], prev["gps_lon"],
                      pkt["gps_lat"], pkt["gps_lon"])
    dt = pkt["time"] - prev["time"]

    if dt > 0 and dist/dt > 40:
        return {"anomaly": True, "type": "IMPOSSIBLE_MOVEMENT",
                "reason": "speed too high", "speed": dist/dt}

    return {"anomaly": False}
