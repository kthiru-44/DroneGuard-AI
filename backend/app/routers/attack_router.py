from fastapi import APIRouter
from ..state.attack_state import add_attack, clear_attacks, is_attacking, get_attacks

router = APIRouter()

@router.get("/pi/attack-state")
def pi_attack_state():
    return {"status": "ok", "active": bool(is_attacking()), "attacks": get_attacks()}

@router.post("/attack")
def attack(mode: str = None, mag: float = 1.0, style: str = "sudden", dur: int = 10):
    entry = {"mode": mode, "mag": mag, "style": style, "dur": dur}
    e = add_attack(entry)
    return {"status": "ok", "received": e}

@router.post("/attack/clear")
def clear_attack():
    clear_attacks()
    return {"status": "ok", "cleared": True}
