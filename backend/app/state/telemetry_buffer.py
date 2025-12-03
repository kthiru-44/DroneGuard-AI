# app/state/telemetry_buffer.py
from collections import deque
from ..config import MAX_TELEMETRY_BUFFER

telemetry_buffer = deque(maxlen=MAX_TELEMETRY_BUFFER)

def add(pkt: dict):
    telemetry_buffer.append(pkt)

def get_buffer():
    # return newest-first to be consistent with frontend expectations
    return list(reversed(telemetry_buffer))

def latest():
    if telemetry_buffer:
        return telemetry_buffer[-1]
    return None

def clear():
    telemetry_buffer.clear()
