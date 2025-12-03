# app/state/attack_state.py
import time
from typing import List, Dict

# Very small in-memory store for demo
_state = {
    "attacks": []  # each attack is dict with keys mode, mag, style, dur, ts
}

def list_attacks() -> List[Dict]:
    return list(_state["attacks"])

def add_attack(entry: Dict):
    entry = dict(entry)
    entry.setdefault("ts", time.time())
    _state["attacks"].append(entry)
    return entry

def clear_attacks():
    _state["attacks"].clear()

def active() -> bool:
    return len(_state["attacks"]) > 0

def latest_attack() -> Dict | None:
    return _state["attacks"][-1] if _state["attacks"] else None
