
# attack_router.py - safe, local-only attack endpoints (demo)
from fastapi import APIRouter, HTTPException, Request
from typing import Dict, Any

router = APIRouter()

# in-memory attack state (simple)
_attack_state = {"active": False, "mode": None, "params": {}}

@router.post("/attack")
async def attack(request: Request):
    """
    Demo-only endpoint to mark an attack as active and store params.
    This does NOT itself reach out to other devices. The local drone simulator polls /pi/attack-state to see the attack
    and changes its own simulated telemetry.
    """
    q = dict(request.query_params)
    mode = q.get("mode")
    if not mode:
        raise HTTPException(status_code=400, detail="mode param required")
    _attack_state["active"] = True
    _attack_state["mode"] = mode
    _attack_state["params"] = q
    return {"status":"ok", "attack": _attack_state}

@router.post("/attack/clear")
async def clear_attack():
    _attack_state["active"] = False
    _attack_state["mode"] = None
    _attack_state["params"] = {}
    return {"status":"ok", "cleared": True}

@router.get("/pi/attack-state")
async def attack_state():
    return {"status":"ok", "attack": dict(_attack_state)}
