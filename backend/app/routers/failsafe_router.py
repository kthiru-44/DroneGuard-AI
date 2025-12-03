from fastapi import APIRouter
from ..state.failsafe_state import get_failsafe, activate_failsafe, reset_failsafe
from ..websocket_handlers.ws_frontend import broadcast_to_frontend

router = APIRouter()

@router.get("/failsafe/state")
def read_failsafe():
    return get_failsafe()

@router.post("/failsafe/activate")
async def activate():
    fs = activate_failsafe(reason="operator")
    # broadcast to frontends (best-effort)
    try:
        await broadcast_to_frontend({"type":"failsafe", "failsafe":fs})
    except Exception:
        pass
    return {"status":"ok", "failsafe": fs}

@router.post("/failsafe/reset")
async def reset():
    fs = reset_failsafe()
    try:
        await broadcast_to_frontend({"type":"failsafe", "failsafe":fs})
    except Exception:
        pass
    return {"status":"ok", "failsafe": fs}
