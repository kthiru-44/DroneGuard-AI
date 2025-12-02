from collections import deque
from ..config import MAX_BUFFER_SIZE

telemetry_buffer = deque(maxlen=MAX_BUFFER_SIZE)

def add(pkt):
    telemetry_buffer.append(pkt)

def get_buffer():
    return list(telemetry_buffer)
