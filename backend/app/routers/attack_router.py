from fastapi import APIRouter, Query
from ..state.attack_state import set_attack, clear_attack, get_attack

attack_router = APIRouter(prefix="/attack", tags=["Attack API"])

@attack_router.post("/")
def apply_attack(
    mode: str = Query(...),
    magnitude: float = Query(1.0),
    style: str = Query("sudden"),
):
    params = {"magnitude": magnitude, "style": style}
    set_attack(mode, params)
    return {"status": "attack_set", "mode": mode, "params": params}

@attack_router.post("/clear")
def reset_attack():
    clear_attack()
    return {"status": "attack_cleared"}

@attack_router.get("/state")
def attack_status():
    return get_attack()
