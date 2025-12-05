# app/state/failsafe_state.py
import time
from typing import Optional, Dict

_failsafe = {
    "active": False,
    "activated_at": None,
    "reason": None,
    "auto_mode": False
    
}

def activate(reason: Optional[str] = None):
    _failsafe["active"] = True
    _failsafe["activated_at"] = time.time()
    _failsafe["reason"] = reason
    return dict(_failsafe)

def deactivate():
    _failsafe["active"] = False
    _failsafe["activated_at"] = None
    _failsafe["reason"] = None
    return dict(_failsafe)

def get_state() -> Dict:
    return dict(_failsafe)

def set_auto_mode(enabled: bool):
    _failsafe["auto_mode"] = enabled
    return dict(_failsafe)
