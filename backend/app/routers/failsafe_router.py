# failsafe_router.py
from fastapi import APIRouter
from ..state.failsafe_state import FailsafeState

router = APIRouter()

# main.py will inject failsafe_state into app.state
@router.get("/pi/failsafe-state")
async def get_failsafe_state(request):
    fs = request.app.state.failsafe_state
    return {"status":"ok", "failsafe": {"active": fs.active, "reason": fs.reason}}
