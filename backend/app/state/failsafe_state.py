# failsafe_state.py
import threading
from typing import Dict, Any

class FailsafeState:
    def __init__(self):
        self.lock = threading.Lock()
        self.active = False
        self.reason = ""
        self.history = []

    def activate(self, reason: str):
        with self.lock:
            self.active = True
            self.reason = reason
            self.history.append({"ts": __import__("time").time(), "reason": reason})

    def reset(self):
        with self.lock:
            self.active = False
            self.reason = ""
