# app/api/control.py
from fastapi import APIRouter, Body
from ..state.attack_state import add_attack, clear_attacks, list_attacks, active as attack_active, latest_attack
from ..state.failsafe_state import get_state, activate, deactivate

router = APIRouter()

@router.get("/pi/attack-state")
def pi_attack_state():
    """
    Polled by PI. Returns whether any attack is active.
    """
    return {"status": "ok", "time": __import__("time").time(), "active": bool(attack_active())}

@router.post("/attack")
def post_attack(mode: str = None, mag: float = 1.0, style: str = "sudden", dur: int = 10):
    entry = {"mode": mode, "mag": float(mag), "style": style, "dur": int(dur)}
    added = add_attack(entry)
    return {"status": "ok", "received": added}

@router.post("/attack/clear")
def post_attack_clear():
    clear_attacks()
    return {"status": "ok", "cleared": True}

@router.get("/attack/list")
def get_attack_list():
    return {"status": "ok", "attacks": list_attacks()}

@router.get("/attack/latest")
def get_attack_latest():
    return {"status": "ok", "latest": latest_attack()}

@router.get("/failsafe/state")
def get_failsafe():
    return get_state()

@router.post("/failsafe/activate")
def post_failsafe_activate(reason: str = None):
    s = activate(reason=reason)
    return {"status": "ok", "failsafe": s}

@router.post("/failsafe/deactivate")
def post_failsafe_deactivate():
    s = deactivate()
    return {"status": "ok", "failsafe": s}
