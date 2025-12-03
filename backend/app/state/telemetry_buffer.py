# telemetry_buffer.py
from collections import deque
import threading

class TelemetryBuffer:
    def __init__(self, maxlen=1024):
        self.buf = deque(maxlen=maxlen)
        self.lock = threading.Lock()

    def push(self, item):
        with self.lock:
            self.buf.append(item)

    def snapshot(self):
        with self.lock:
            return list(self.buf)
